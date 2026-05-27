from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel
from datetime import timedelta
import random

from app.core.config import settings
from app.core.security import create_access_token, get_current_user
from app.models.user import User
from app.services.google_auth_service import GoogleAuthError, verify_google_id_token

router = APIRouter()

# In-memory OTP store (use Redis in production)
otp_store: dict = {}

class SendOtpRequest(BaseModel):
    phone: str

class VerifyOtpRequest(BaseModel):
    phone: str
    otp: str

class GoogleAuthRequest(BaseModel):
    id_token: str

class UpdateProfileRequest(BaseModel):
    name: str | None = None
    email: str | None = None
    phone: str | None = None

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict


def _user_to_response(user: User) -> dict:
    return {
        "id": str(user.id),
        "phone": user.phone,
        "name": user.name,
        "email": user.email,
        "avatar_url": user.avatar_url,
        "auth_provider": user.auth_provider,
        "rating": user.rating,
        "total_exchanges": user.total_exchanges,
    }


def _issue_token(user: User) -> TokenResponse:
    access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    return TokenResponse(access_token=access_token, user=_user_to_response(user))

@router.post("/send-otp")
async def send_otp(request: SendOtpRequest):
    """Send OTP to phone number"""
    import logging
    phone = request.phone.strip()
    logger = logging.getLogger("otp")
    try:
        if len(phone) != 10 or not phone.isdigit():
            logger.error(f"Invalid phone number attempted: {phone}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid phone number"
            )
        # Generate 6-digit OTP
        otp = str(random.randint(100000, 999999))
        otp_store[phone] = otp
        # TODO: Send OTP via SMS gateway (MSG91, Twilio, etc.)
        logger.info(f"OTP for {phone}: {otp}")  # For development
        # Simulate sending OTP, catch and log any errors
        # Example: response = send_sms(phone, otp)
        # logger.info(f"SMS response: {response}")
        return {"message": "OTP sent successfully", "debug_otp": otp if settings.DEBUG else None}
    except Exception as e:
        logger.error(f"Failed to send OTP to {phone}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send OTP. Please try again."
        )

@router.post("/verify-otp", response_model=TokenResponse)
async def verify_otp(request: VerifyOtpRequest):
    """Verify OTP and return access token"""
    phone = request.phone.strip()
    otp = request.otp.strip()
    
    stored_otp = otp_store.get(phone)
    
    # For development, accept any OTP if DEBUG mode is enabled
    if settings.DEBUG:
        # In DEBUG mode, accept any 6-digit OTP
        if len(otp) == 6 and otp.isdigit():
            stored_otp = otp
        # Also accept the stored OTP if it exists
        elif stored_otp:
            pass  # Use stored OTP
        else:
            # If no stored OTP, accept any 6-digit OTP
            stored_otp = otp
    
    if not stored_otp or stored_otp != otp:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid OTP"
        )
    
    # Clear OTP after verification
    otp_store.pop(phone, None)
    
    # Find or create user
    user = await User.find_one(User.phone == phone)
    if not user:
        user = User(phone=phone, name=f"User_{phone[-4:]}", auth_provider="phone")
        await user.insert()
    
    return _issue_token(user)


@router.post("/google", response_model=TokenResponse)
async def google_auth(request: GoogleAuthRequest):
    """Sign in or register with a Google ID token."""
    try:
        claims = verify_google_id_token(request.id_token.strip())
    except GoogleAuthError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
        ) from exc

    google_id = claims["sub"]
    email = claims.get("email")
    name = claims.get("name") or (email.split("@")[0] if email else "Google User")
    avatar_url = claims.get("picture")

    user = await User.find_one(User.google_id == google_id)
    if not user and email:
        user = await User.find_one(User.email == email)

    if user:
        user.google_id = google_id
        user.auth_provider = "google"
        if name and not user.name:
            user.name = name
        if email and not user.email:
            user.email = email
        if avatar_url and not user.avatar_url:
            user.avatar_url = avatar_url
        user.is_verified = True
        await user.save()
    else:
        user = User(
            google_id=google_id,
            email=email,
            name=name,
            avatar_url=avatar_url,
            auth_provider="google",
            is_verified=True,
        )
        await user.insert()

    return _issue_token(user)

@router.get("/profile")
async def get_profile(current_user: User = Depends(get_current_user)):
    """Get current user profile"""
    return {
        **_user_to_response(current_user),
        "created_at": current_user.created_at,
    }

@router.put("/profile")
async def update_profile(
    request: UpdateProfileRequest,
    current_user: User = Depends(get_current_user)
):
    """Update user profile"""
    if request.name is not None:
        current_user.name = request.name.strip()

    if request.email is not None:
        email = request.email.strip() or None
        if email and email != current_user.email:
            existing = await User.find_one(User.email == email)
            if existing and existing.id != current_user.id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email is already in use",
                )
        current_user.email = email

    if request.phone is not None:
        phone = request.phone.strip()
        if phone == "":
            current_user.phone = None
        else:
            if len(phone) != 10 or not phone.isdigit():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Mobile number must be 10 digits",
                )
            if phone != current_user.phone:
                existing = await User.find_one(User.phone == phone)
                if existing and existing.id != current_user.id:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Mobile number is already in use",
                    )
            current_user.phone = phone

    await current_user.save()

    return {
        "message": "Profile updated successfully",
        "user": _user_to_response(current_user),
    }

