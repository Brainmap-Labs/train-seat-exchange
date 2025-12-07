import re
import os
from typing import Dict, Any, Optional, List
from io import BytesIO
from PIL import Image

class OCRService:
    """Service for extracting ticket data from images using OCR
    
    Supports multiple OCR methods in priority order:
    1. Hugging Face models (recommended - better accuracy)
    2. Tesseract OCR (fallback)
    3. Mock data (development only)
    """
    
    def __init__(self, tesseract_cmd: Optional[str] = None, 
                 huggingface_model: Optional[str] = None,
                 use_huggingface: bool = True,
                 use_openai_parsing: bool = False,
                 openai_api_key: Optional[str] = None,
                 openai_model: str = "gpt-4o-mini"):
        # PNR patterns - multiple formats
        # Format 1: "PNR: 2647755663" or "PNR:2215801342"
        # Format 2: "2647755663" (standalone 10 digits)
        self.pnr_patterns = [
            re.compile(r'PNR\s*:?\s*(\d{10})', re.IGNORECASE),
            re.compile(r'\b(\d{10})\b'),  # Standalone 10 digits
        ]
        
        # Train number and name patterns - multiple formats
        # Format 1: "12556/GORAKHDHAM EXP" or "12556 GORAKHDHAM EXP"
        # Format 2: "ANVT GKP EXP (15058)" or "15058"
        self.train_patterns = [
            re.compile(r'(\d{4,5})\s*[/-]?\s*([A-Z\s]+(?:EXPRESS|RAJDHANI|SHATABDI|DURONTO|MAIL|EXP|GKP|ANVT)?)', re.IGNORECASE),
            re.compile(r'\((\d{4,5})\)'),  # Train number in parentheses
            re.compile(r'\b(\d{4,5})\b'),  # Standalone train number
        ]
        self.train_name_patterns = [
            re.compile(r'([A-Z\s]+(?:EXPRESS|RAJDHANI|SHATABDI|DURONTO|MAIL|EXP|GKP))\s*\(?\d{4,5}\)?', re.IGNORECASE),
            re.compile(r'([A-Z\s]{3,}(?:EXPRESS|RAJDHANI|SHATABDI|DURONTO|MAIL|EXP))', re.IGNORECASE),
        ]
        
        # Seat/Coach patterns - multiple formats
        # Format 1: "CNF/B2/21" or "CNF/B2/21/LB"
        # Format 2: "CNF/A2/31/LB" or "B2/21/LB"
        # Format 3: "CNF B2/21" or "B2 21"
        # Handle OCR errors: "dking Statu" (Booking Status), "joking Status" (Current Status)
        self.seat_patterns = [
            # Pattern for "CNF/B2/21" or "CNF/B2/21/LB" or "CNF/A2/31/LB"
            re.compile(r'(?:CNF|WL|RAC|CAN)\s*[/-]?\s*([A-Z]\d{1,2})\s*[/-]?\s*(\d{1,3})\s*[/-]?\s*(LB|MB|UB|SL|SU)?', re.IGNORECASE),
            # Pattern for "B2/21/LB" or "A2/31/LB" (without status prefix)
            re.compile(r'\b([A-Z]\d{1,2})\s*[/-]?\s*(\d{1,3})\s*[/-]?\s*(LB|MB|UB|SL|SU)\b', re.IGNORECASE),
            # Pattern near "Booking Status" or "Current Status" (with OCR error tolerance)
            re.compile(r'(?:Booking|Current|dking|joking)\s+(?:Status|Statu)\s*:?\s*(?:CNF|WL|RAC)?\s*[/-]?\s*([A-Z]\d{1,2})\s*[/-]?\s*(\d{1,3})\s*[/-]?\s*(LB|MB|UB|SL|SU)?', re.IGNORECASE),
            # Pattern for "B2/21" or "A2/31" (minimal format)
            re.compile(r'\b([A-Z]\d{1,2})\s*[/-]\s*(\d{1,3})\b', re.IGNORECASE),
        ]
        
        # Date patterns - multiple formats
        # Format 1: "06-Sep-2024" or "14 AUG WEDNESDAY 2024"
        # Format 2: "14 Aug 2024" or "06/09/2024"
        self.date_patterns = [
            re.compile(r'\b(\d{1,2}[-/]\w{3,}[-/]\d{2,4})\b', re.IGNORECASE),
            re.compile(r'\b(\d{1,2}\s+\w{3,}\s+\d{2,4})\b', re.IGNORECASE),
            re.compile(r'(?:Departure|Arrival|Date|Travel Date)\s*:?\s*(\d{1,2}[-/]\w{3,}[-/]\d{2,4})', re.IGNORECASE),
        ]
        
        # Station patterns - multiple formats
        # Format 1: "NEW DELHI (NDLS)" or "Anand Vihar Trm (ANVT)"
        # Format 2: "NDLS - NEW DELHI" or "NDLS > NEW DELHI"
        # Format 3: "ANVT TO KLD" or "FROM ANVT TO KLD"
        # Format 4: "From: NDLS - NEW DELHI" or "To: HWH - HOWRAH"
        self.station_patterns = [
            re.compile(r'([A-Z\s]+)\s*\(([A-Z]{2,5})\)', re.IGNORECASE),  # "NEW DELHI (NDLS)" or "Anand Vihar Trm (ANVT)"
            re.compile(r'([A-Z]{2,5})\s*[-–>]\s*([A-Z\s]+)', re.IGNORECASE),  # "NDLS - NEW DELHI" or "NDLS > NEW DELHI"
            re.compile(r'([A-Z]{2,5})\s+(?:TO|FROM)\s+([A-Z]{2,5})', re.IGNORECASE),  # "ANVT TO KLD"
            re.compile(r'(?:From|Boarding|To|Destination)\s*:?\s*([A-Z\s]+)\s*\(([A-Z]{2,5})\)', re.IGNORECASE),
            # Pattern for "NEW DELHI (NDLS) > KHALILABAD (KLD)" format
            re.compile(r'([A-Z\s]+)\s*\(([A-Z]{2,5})\)\s*[-–>]\s*([A-Z\s]+)\s*\(([A-Z]{2,5})\)', re.IGNORECASE),
        ]
        
        # Class patterns
        self.class_patterns = [
            re.compile(r'(?:Class|CLASS)\s*:?\s*(1A|2A|3A|SL|CC|EC|2S|AC\s*3\s*Tier|AC\s*2\s*Tier)', re.IGNORECASE),
            re.compile(r'\b(1A|2A|3A|SL|CC|EC|2S)\b', re.IGNORECASE),
            re.compile(r'AC\s*3\s*Tier\s*\(?(3A)\)?', re.IGNORECASE),
            re.compile(r'AC\s*2\s*Tier\s*\(?(2A)\)?', re.IGNORECASE),
        ]
        
        # Passenger name patterns - multiple formats
        # Format 1: "1. Gourav Chutani 33 MALE" or "1. RAHUL KUMAR M/35"
        # Format 2: "NEELAM AZAD\nFemale| 36 yrs"
        # Format 3: "Name: Gourav Chutani"
        self.passenger_name_patterns = [
            re.compile(r'(?:^\d+\.|#\s*\d+)\s+([A-Z][A-Z\s]{2,30}?)\s+(\d{1,3})\s+(MALE|FEMALE|M|F|MALE|FEMALE)', re.IGNORECASE | re.MULTILINE),
            re.compile(r'(?:^\d+\.|#\s*\d+)\s+([A-Z][A-Z\s]{2,30}?)\s+(\d{1,3})\s*[/-]?\s*(M|F|MALE|FEMALE)', re.IGNORECASE | re.MULTILINE),
            re.compile(r'([A-Z][A-Z\s]{2,30}?)\s*(?:Male|Female|M|F)\s*\|\s*(\d{1,3})\s*yrs?', re.IGNORECASE),
            re.compile(r'([A-Z][A-Z\s]{2,30}?)\s*(?:Male|Female|M|F)', re.IGNORECASE),
        ]
        
        # Passenger info patterns - combined name, age, gender
        # Format 1: "1. Gourav Chutani 33 MALE CNF/B2/21"
        # Format 2: "NEELAM AZAD\nFemale| 36 yrs\n...\nCNF/A2/31/LB"
        self.passenger_info_patterns = [
            # Pattern for "1. Name Age Gender Status/Coach/Seat"
            re.compile(r'(?:^\d+\.|#\s*\d+)\s+([A-Z][A-Z\s]{2,30}?)\s+(\d{1,3})\s+(MALE|FEMALE|M|F)\s+(?:CNF|WL|RAC|CAN)\s*[/-]?\s*([A-Z]\d{1,2})\s*[/-]?\s*(\d{1,3})\s*[/-]?\s*(LB|MB|UB|SL|SU)?', re.IGNORECASE | re.MULTILINE),
            # Pattern for "Name\nGender| Age yrs\n...\nStatus/Coach/Seat/Berth"
            re.compile(r'([A-Z][A-Z\s]{2,30}?)\s*(?:Male|Female|M|F)\s*\|\s*(\d{1,3})\s*yrs?', re.IGNORECASE),
        ]
        
        self.huggingface_model = huggingface_model
        self.use_huggingface = use_huggingface
        self.use_openai_parsing = use_openai_parsing
        self.openai_api_key = openai_api_key
        self.openai_model = openai_model
        self.huggingface_available = False
        self.tesseract_available = False
        self.openai_available = False
        self.ocr_pipeline = None  # Will be initialized if Hugging Face is available
        
        # Check OCR availability
        if self.use_huggingface and self.huggingface_model:
            self.huggingface_available = self._check_huggingface()
        
        if not self.huggingface_available:
            self.tesseract_available = self._check_tesseract(tesseract_cmd)
        
        # Check OpenAI availability for parsing
        if self.use_openai_parsing:
            self.openai_available = self._check_openai()
    
    def _check_huggingface(self) -> bool:
        """Check if Hugging Face transformers are available and model can be loaded"""
        try:
            from transformers import pipeline
            import torch
            
            # Try to initialize the OCR pipeline
            try:
                print(f"🤖 Loading Hugging Face OCR model: {self.huggingface_model}")
                print("   This may take a few minutes on first run (downloading model)...")
                
                # Determine device (GPU if available, else CPU)
                device = 0 if torch.cuda.is_available() else -1
                if device == 0:
                    print("   Using GPU acceleration")
                else:
                    print("   Using CPU (slower but works)")
                
                # Initialize pipeline with appropriate device
                self.ocr_pipeline = pipeline(
                    "image-to-text",
                    model=self.huggingface_model,
                    device=device
                )
                print("✅ Hugging Face OCR model loaded successfully")
                return True
            except Exception as e:
                error_msg = str(e)
                if "out of memory" in error_msg.lower() or "cuda" in error_msg.lower():
                    print(f"⚠️  GPU memory issue or CUDA error: {e}")
                    print("   Trying CPU mode...")
                    try:
                        self.ocr_pipeline = pipeline(
                            "image-to-text",
                            model=self.huggingface_model,
                            device=-1  # Force CPU
                        )
                        print("✅ Hugging Face OCR model loaded on CPU")
                        return True
                    except Exception as e2:
                        print(f"⚠️  Failed to load on CPU: {e2}")
                else:
                    print(f"⚠️  Failed to load Hugging Face model {self.huggingface_model}: {e}")
                print("   Falling back to Tesseract OCR")
                return False
        except ImportError:
            print("⚠️  transformers or torch not installed. Install with: pip install transformers torch")
            return False
    
    def _check_tesseract(self, tesseract_cmd: Optional[str] = None) -> bool:
        """Check if Tesseract OCR is available and configure it if needed"""
        try:
            import pytesseract
            
            # Set custom Tesseract command if provided
            if tesseract_cmd:
                pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
            
            # Try to get Tesseract version to verify it's working
            try:
                pytesseract.get_tesseract_version()
                return True
            except Exception as e:
                error_msg = str(e)
                if "tesseract is not installed" in error_msg.lower() or "not in your path" in error_msg.lower():
                    print("⚠️  Tesseract OCR is not installed or not in your PATH.")
                    print("   Please install Tesseract OCR:")
                    print("   - macOS: brew install tesseract")
                    print("   - Linux: sudo apt-get install tesseract-ocr")
                    print("   - Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki")
                    print("   See README.md for more information.")
                else:
                    print(f"⚠️  Tesseract OCR error: {error_msg}")
                return False
        except ImportError:
            print("⚠️  pytesseract is not installed. Install it with: pip install pytesseract")
            return False
    
    async def extract_ticket_data(self, file_content: bytes, content_type: str) -> Dict[str, Any]:
        """
        Extract ticket information from uploaded file
        
        Args:
            file_content: Raw file bytes
            content_type: MIME type of the file
            
        Returns:
            Dictionary containing extracted ticket data
        """
        # Convert to image if PDF
        if content_type == "application/pdf":
            text = await self._extract_from_pdf(file_content)
        else:
            text = await self._extract_from_image(file_content)
        
        # Parse extracted text
        return self._parse_ticket_text(text)
    
    async def _extract_from_image(self, image_bytes: bytes) -> str:
        """Extract text from image using OCR (tries Hugging Face first, then Tesseract)"""
        image = Image.open(BytesIO(image_bytes))
        
        # Try Hugging Face OCR first (better accuracy)
        if self.huggingface_available:
            try:
                text = await self._extract_with_huggingface(image)
                if text and len(text.strip()) > 10:  # Basic validation
                    return text
                else:
                    print("⚠️  Hugging Face OCR returned empty/insufficient text. Falling back to Tesseract...")
            except Exception as e:
                print(f"⚠️  Hugging Face OCR error: {e}. Falling back to Tesseract...")
        
        # Fallback to Tesseract
        if self.tesseract_available:
            try:
                import pytesseract
                text = pytesseract.image_to_string(image)
                return text
            except ImportError:
                print("⚠️  pytesseract is not installed. Using mock data.")
                return self._get_mock_ticket_text()
            except Exception as e:
                error_msg = str(e)
                if "tesseract is not installed" in error_msg.lower() or "not in your path" in error_msg.lower():
                    print("❌ OCR Error: tesseract is not installed or it's not in your PATH.")
                    print("   See README file for more information.")
                else:
                    print(f"❌ OCR Error: {error_msg}")
                return self._get_mock_ticket_text()
        
        # Final fallback to mock data
        print("⚠️  No OCR method available. Using mock data.")
        return self._get_mock_ticket_text()
    
    async def _extract_with_huggingface(self, image: Image.Image) -> str:
        """Extract text using Hugging Face OCR model"""
        if not self.ocr_pipeline:
            raise Exception("Hugging Face OCR pipeline not initialized")
        
        try:
            # Convert PIL image to RGB if needed
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Run OCR pipeline
            results = self.ocr_pipeline(image)
            
            # Handle different response formats
            if isinstance(results, list):
                # Some models return list of dicts with 'generated_text' key
                if results and isinstance(results[0], dict):
                    text = ' '.join([item.get('generated_text', '') for item in results if item.get('generated_text')])
                else:
                    # Some models return list of strings
                    text = ' '.join([str(item) for item in results if item])
            elif isinstance(results, dict):
                text = results.get('generated_text', '') or results.get('text', '')
            else:
                text = str(results)
            
            return text.strip()
        except Exception as e:
            print(f"Error in Hugging Face OCR: {e}")
            raise
    
    async def _extract_from_pdf(self, pdf_bytes: bytes) -> str:
        """Extract text from PDF (tries Hugging Face first, then Tesseract)"""
        try:
            from pdf2image import convert_from_bytes
            
            images = convert_from_bytes(pdf_bytes)
            text = ""
            
            for image in images:
                # Try Hugging Face first
                if self.huggingface_available:
                    try:
                        page_text = await self._extract_with_huggingface(image)
                        if page_text and len(page_text.strip()) > 10:
                            text += page_text + "\n"
                            continue
                    except Exception as e:
                        print(f"⚠️  Hugging Face OCR error on PDF page: {e}")
                
                # Fallback to Tesseract
                if self.tesseract_available:
                    try:
                        import pytesseract
                        text += pytesseract.image_to_string(image) + "\n"
                    except Exception as e:
                        print(f"⚠️  Tesseract error on PDF page: {e}")
            
            if text.strip():
                return text
            
            print("⚠️  No OCR method available for PDF. Using mock data.")
            return self._get_mock_ticket_text()
            
        except ImportError as e:
            print(f"⚠️  Missing dependency: {e}. Using mock data.")
            return self._get_mock_ticket_text()
        except Exception as e:
            error_msg = str(e)
            print(f"❌ PDF OCR Error: {error_msg}")
            return self._get_mock_ticket_text()
    
    def _parse_ticket_text(self, text: str) -> Dict[str, Any]:
        """Parse ticket text and extract structured data from multiple OCR formats
        
        Uses OpenAI parsing if enabled, otherwise falls back to regex parsing
        """
        # Try OpenAI parsing first if enabled
        if self.use_openai_parsing and self.openai_available:
            try:
                result = self._parse_with_openai(text)
                if result and result.get("confidence", 0) > 0.5:  # Only use if confidence is reasonable
                    return result
                else:
                    print("⚠️  OpenAI parsing returned low confidence, falling back to regex...")
            except Exception as e:
                print(f"⚠️  OpenAI parsing failed: {e}. Falling back to regex parsing...")
        
        # Fallback to regex parsing
        return self._parse_with_regex(text)
    
    def _parse_with_regex(self, text: str) -> Dict[str, Any]:
        """Parse ticket text using regex patterns (original method)"""
        result = {
            "pnr": None,
            "train_number": None,
            "train_name": None,
            "travel_date": None,
            "boarding_station": None,
            "destination_station": None,
            "class_type": None,
            "passengers": [],
            "confidence": 0.0,
        }
        
        # Normalize text - remove extra whitespace and newlines for better matching
        normalized_text = ' '.join(text.split())
        
        # Extract PNR - try multiple patterns
        for pattern in self.pnr_patterns:
            pnr_match = pattern.search(text)
            if pnr_match:
                pnr = pnr_match.group(1) if pnr_match.groups() else pnr_match.group()
                if len(pnr) == 10 and pnr.isdigit():
                    result["pnr"] = pnr
                    result["confidence"] += 0.2
                    break
        
        # Extract Train Number and Name - try multiple patterns
        train_number = None
        train_name = None
        
        # Try to find train number first
        for pattern in self.train_patterns:
            train_match = pattern.search(text)
            if train_match:
                train_number = train_match.group(1) if train_match.groups() else train_match.group()
                if train_number and len(train_number) >= 4:
                    result["train_number"] = train_number
                    result["confidence"] += 0.1
                    break
        
        # Try to find train name
        for pattern in self.train_name_patterns:
            name_match = pattern.search(text)
            if name_match:
                train_name = name_match.group(1).strip()
                if train_name and len(train_name) > 3:
                    result["train_name"] = train_name
                    result["confidence"] += 0.1
                    break
        
        # If we have train number but no name, try to extract from context
        if result["train_number"] and not result["train_name"]:
            # Look for pattern like "12556/GORAKHDHAM EXP" or "12556 GORAKHDHAM EXP"
            train_context = re.search(rf'{re.escape(result["train_number"])}\s*[/-]?\s*([A-Z\s]{{5,}}(?:EXP|EXPRESS|RAJDHANI|SHATABDI|DURONTO|MAIL|GKP))', text, re.IGNORECASE)
            if train_context:
                result["train_name"] = train_context.group(1).strip()
                result["confidence"] += 0.05
            else:
                # Try reverse: "GKP EXP (15058)" format
                train_context = re.search(rf'([A-Z\s]{{3,}}(?:EXP|EXPRESS|RAJDHANI|SHATABDI|DURONTO|MAIL|GKP))\s*\(?{re.escape(result["train_number"])}\)?', text, re.IGNORECASE)
                if train_context:
                    result["train_name"] = train_context.group(1).strip()
                    result["confidence"] += 0.05
        
        # Extract Date - try multiple patterns
        for pattern in self.date_patterns:
            date_match = pattern.search(text)
            if date_match:
                date_str = date_match.group(1) if date_match.groups() else date_match.group()
                # Normalize date format
                date_str = self._normalize_date(date_str)
                if date_str:
                    result["travel_date"] = date_str
                    result["confidence"] += 0.1
                    break
        
        # Extract Stations - try multiple patterns
        stations = self._extract_stations(text)
        if stations.get("boarding"):
            result["boarding_station"] = stations["boarding"]
            result["confidence"] += 0.1
        if stations.get("destination"):
            result["destination_station"] = stations["destination"]
            result["confidence"] += 0.1
        
        # Extract Class - try multiple patterns
        for pattern in self.class_patterns:
            class_match = pattern.search(text)
            if class_match:
                class_type = class_match.group(1) if class_match.groups() else class_match.group()
                # Normalize class type
                class_type = self._normalize_class(class_type)
                if class_type:
                    result["class_type"] = class_type
                    result["confidence"] += 0.1
                    break
        
        # Extract Passengers/Seats - try multiple patterns
        passengers = self._extract_passengers(text)
        result["passengers"] = passengers
        if passengers:
            result["confidence"] += min(len(passengers) * 0.05, 0.3)
        
        # Cap confidence at 1.0
        result["confidence"] = min(result["confidence"], 1.0)
        
        return result
    
    def _check_openai(self) -> bool:
        """Check if OpenAI API is available and configured"""
        try:
            from openai import OpenAI
            
            if not self.openai_api_key:
                print("⚠️  OpenAI API key not configured. Set OPENAI_API_KEY in your .env file.")
                return False
            
            # Try to initialize client (won't make API call yet)
            self.openai_client = OpenAI(api_key=self.openai_api_key)
            print(f"✅ OpenAI client initialized (model: {self.openai_model})")
            return True
        except ImportError:
            print("⚠️  openai package not installed. Install with: pip install openai")
            return False
        except Exception as e:
            print(f"⚠️  Failed to initialize OpenAI: {e}")
            return False
    
    def _parse_with_openai(self, text: str) -> Dict[str, Any]:
        """Parse ticket text using OpenAI model"""
        try:
            from openai import OpenAI
            
            if not hasattr(self, 'openai_client') or not self.openai_client:
                raise Exception("OpenAI client not initialized")
            
            # Create a structured prompt for ticket parsing
            prompt = f"""Extract ticket information from the following Indian Railways ticket text. 
Return a JSON object with the following structure:
{{
    "pnr": "10-digit PNR number or null",
    "train_number": "Train number (4-5 digits) or null",
    "train_name": "Train name or null",
    "travel_date": "Date in DD-MMM-YYYY format or null",
    "boarding_station": "Station code - Station name (e.g., 'NDLS - New Delhi') or null",
    "destination_station": "Station code - Station name (e.g., 'HWH - Howrah Junction') or null",
    "class_type": "Class code (1A, 2A, 3A, SL, CC, EC, 2S) or null",
    "passengers": [
        {{
            "name": "Passenger full name",
            "age": integer_age,
            "gender": "M, F, or O",
            "coach": "Coach code (e.g., B2, A1)",
            "seat_number": integer_seat_number,
            "berth_type": "LB, MB, UB, SL, or SU",
            "booking_status": "CNF, RAC, WL, RLWL, or PQWL",
            "current_status": "CNF, RAC, WL, RLWL, or PQWL"
        }}
    ],
    "confidence": float_between_0_and_1
}}

Ticket text:
{text}

Important:
- Extract all passenger details including name, age, gender, coach, seat number, and berth type
- Normalize gender to M, F, or O
- Normalize class type to standard codes (1A, 2A, 3A, SL, CC, EC, 2S)
- For stations, use format "CODE - Name" (e.g., "NDLS - New Delhi")
- Set confidence based on how much information was successfully extracted
- Return only valid JSON, no additional text"""

            # Call OpenAI API
            response = self.openai_client.chat.completions.create(
                model=self.openai_model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert at parsing Indian Railways ticket information. Always return valid JSON only."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.1,  # Low temperature for consistent parsing
                response_format={"type": "json_object"}  # Force JSON response
            )
            
            # Parse the response
            import json
            parsed_data = json.loads(response.choices[0].message.content)
            
            # Validate and normalize the response
            result = {
                "pnr": parsed_data.get("pnr"),
                "train_number": parsed_data.get("train_number"),
                "train_name": parsed_data.get("train_name"),
                "travel_date": parsed_data.get("travel_date"),
                "boarding_station": parsed_data.get("boarding_station"),
                "destination_station": parsed_data.get("destination_station"),
                "class_type": parsed_data.get("class_type"),
                "passengers": parsed_data.get("passengers", []),
                "confidence": float(parsed_data.get("confidence", 0.8)),
            }
            
            # Normalize passenger data
            normalized_passengers = []
            for p in result["passengers"]:
                # Normalize gender
                gender = str(p.get("gender", "M")).upper()
                if gender not in ["M", "F", "O"]:
                    gender = "M" if gender in ["MALE", "M"] else "F" if gender in ["FEMALE", "F"] else "O"
                
                # Normalize berth type
                berth = str(p.get("berth_type", "LB")).upper()
                if berth not in ["LB", "MB", "UB", "SL", "SU"]:
                    berth = "LB"
                
                # Normalize booking status
                booking_status = str(p.get("booking_status", "CNF")).upper()
                if booking_status not in ["CNF", "RAC", "WL", "RLWL", "PQWL"]:
                    booking_status = "CNF"
                
                normalized_passengers.append({
                    "name": str(p.get("name", "Unknown")).title(),
                    "age": int(p.get("age", 0)) if p.get("age") else 0,
                    "gender": gender,
                    "coach": str(p.get("coach", "")).upper(),
                    "seat_number": int(p.get("seat_number", 0)) if p.get("seat_number") else 0,
                    "berth_type": berth,
                    "booking_status": booking_status,
                    "current_status": booking_status,
                })
            
            result["passengers"] = normalized_passengers
            
            # Normalize class type
            if result["class_type"]:
                result["class_type"] = self._normalize_class(result["class_type"])
            
            print(f"✅ OpenAI parsing completed with confidence: {result['confidence']:.2f}")
            return result
            
        except Exception as e:
            print(f"❌ OpenAI parsing error: {e}")
            raise
    
    def _normalize_date(self, date_str: str) -> Optional[str]:
        """Normalize date string to standard format"""
        if not date_str:
            return None
        
        # Try to parse and normalize common date formats
        # "06-Sep-2024" -> "06-Sep-2024"
        # "14 AUG 2024" -> "14-Aug-2024"
        # "14 Aug Wednesday 2024" -> "14-Aug-2024"
        
        # Remove day names
        date_str = re.sub(r'\b(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)\b', '', date_str, flags=re.IGNORECASE)
        date_str = date_str.strip()
        
        # Normalize month abbreviations
        month_map = {
            'jan': 'Jan', 'feb': 'Feb', 'mar': 'Mar', 'apr': 'Apr',
            'may': 'May', 'jun': 'Jun', 'jul': 'Jul', 'aug': 'Aug',
            'sep': 'Sep', 'oct': 'Oct', 'nov': 'Nov', 'dec': 'Dec'
        }
        
        for abbrev, full in month_map.items():
            date_str = re.sub(rf'\b{abbrev}\b', full, date_str, flags=re.IGNORECASE)
        
        return date_str if date_str else None
    
    def _normalize_class(self, class_str: str) -> Optional[str]:
        """Normalize class string to standard format"""
        if not class_str:
            return None
        
        class_str = class_str.upper().strip()
        
        # Handle "AC 3 Tier" -> "3A"
        if 'AC 3 TIER' in class_str or 'AC3' in class_str:
            return '3A'
        if 'AC 2 TIER' in class_str or 'AC2' in class_str:
            return '2A'
        if 'AC 1 TIER' in class_str or 'AC1' in class_str:
            return '1A'
        
        # Standard class codes
        if class_str in ['1A', '2A', '3A', 'SL', 'CC', 'EC', '2S']:
            return class_str
        
        return None
    
    def _extract_stations(self, text: str) -> Dict[str, Optional[str]]:
        """Extract boarding and destination stations"""
        stations = {"boarding": None, "destination": None}
        
        # Try different patterns
        for pattern in self.station_patterns:
            matches = list(pattern.finditer(text))
            
            # Special handling for "NEW DELHI (NDLS) > KHALILABAD (KLD)" format (4 groups)
            if matches and len(matches[0].groups()) == 4:
                match = matches[0]
                boarding_name = match.group(1).strip()
                boarding_code = match.group(2).upper()
                dest_name = match.group(3).strip()
                dest_code = match.group(4).upper()
                stations["boarding"] = f"{boarding_code} - {boarding_name}"
                stations["destination"] = f"{dest_code} - {dest_name}"
                break
            
            # Handle 2-group patterns
            station_list = []
            for match in matches:
                if match.groups():
                    if len(match.groups()) == 2:
                        # Format: "NEW DELHI (NDLS)" or "NDLS - NEW DELHI"
                        if match.group(2).isupper() and len(match.group(2)) >= 2:  # Station code
                            code = match.group(2).upper()
                            name = match.group(1).strip()
                            station_list.append(f"{code} - {name}")
                        elif match.group(1).isupper() and len(match.group(1)) >= 2:  # Code first format
                            code = match.group(1).upper()
                            name = match.group(2).strip()
                            station_list.append(f"{code} - {name}")
                        else:
                            station_list.append(match.group(0))
                    else:
                        station_list.append(match.group(0))
                else:
                    station_list.append(match.group(0))
            
            if len(station_list) >= 2:
                stations["boarding"] = station_list[0]
                stations["destination"] = station_list[1]
                break
            elif len(station_list) == 1 and not stations["boarding"]:
                stations["boarding"] = station_list[0]
        
        # Try to find "FROM" and "TO" keywords separately
        if not stations["boarding"] or not stations["destination"]:
            from_match = re.search(r'(?:From|Boarding)\s*:?\s*([A-Z\s]+)\s*\(([A-Z]{2,5})\)', text, re.IGNORECASE)
            to_match = re.search(r'(?:To|Destination)\s*:?\s*([A-Z\s]+)\s*\(([A-Z]{2,5})\)', text, re.IGNORECASE)
            
            if from_match:
                stations["boarding"] = f"{from_match.group(2).upper()} - {from_match.group(1).strip()}"
            if to_match:
                stations["destination"] = f"{to_match.group(2).upper()} - {to_match.group(1).strip()}"
        
        # Fallback: Look for "FROM ... TO" pattern with codes only
        if not stations["boarding"] or not stations["destination"]:
            from_to_match = re.search(r'([A-Z]{2,5})\s+(?:TO|>|FROM)\s+([A-Z]{2,5})', text, re.IGNORECASE)
            if from_to_match:
                boarding_code = from_to_match.group(1).upper()
                dest_code = from_to_match.group(2).upper()
                stations["boarding"] = boarding_code
                stations["destination"] = dest_code
        
        return stations
    
    def _extract_passengers(self, text: str) -> List[Dict[str, Any]]:
        """Extract passenger details with name, age, gender, coach, seat, and berth information"""
        passengers = []
        
        # First, try to extract complete passenger info (name, age, gender, seat) together
        # This is more reliable as it matches all info for the same passenger
        
        # Pattern 1: "1. Name Age Gender Status/Coach/Seat/Berth"
        pattern1 = re.compile(
            r'(?:^\d+\.|#\s*\d+)\s+([A-Z][A-Z\s]{2,30}?)\s+(\d{1,3})\s+(MALE|FEMALE|M|F)\s+(?:CNF|WL|RAC|CAN)\s*[/-]?\s*([A-Z]\d{1,2})\s*[/-]?\s*(\d{1,3})\s*[/-]?\s*(LB|MB|UB|SL|SU)?',
            re.IGNORECASE | re.MULTILINE
        )
        
        for match in pattern1.finditer(text):
            name = match.group(1).strip().title()  # Convert to Title Case
            age = int(match.group(2))
            gender_str = match.group(3).upper()
            coach = match.group(4).upper()
            seat_number = int(match.group(5))
            berth = (match.group(6).upper() if match.group(6) else "LB")
            
            # Normalize gender
            gender = "M" if gender_str in ["M", "MALE"] else "F" if gender_str in ["F", "FEMALE"] else "O"
            
            passengers.append({
                "name": name,
                "age": age,
                "gender": gender,
                "coach": coach,
                "seat_number": seat_number,
                "berth_type": berth,
                "booking_status": "CNF",  # Default, can be extracted if available
                "current_status": "CNF",
            })
        
        # Pattern 2: Multi-line format "Name\nGender| Age yrs\n...\nStatus/Coach/Seat/Berth"
        # Extract names with gender and age first
        name_age_gender_matches = []
        pattern2_name = re.compile(
            r'^([A-Z][A-Z\s]{2,30}?)\s*(?:Male|Female|M|F)\s*\|\s*(\d{1,3})\s*yrs?',
            re.IGNORECASE | re.MULTILINE
        )
        
        for match in pattern2_name.finditer(text):
            name = match.group(1).strip().title()
            age = int(match.group(2))
            # Find gender from the line
            gender_match = re.search(r'(?:Male|Female|M|F)', match.group(0), re.IGNORECASE)
            gender_str = gender_match.group(0).upper() if gender_match else "M"
            gender = "M" if gender_str in ["M", "MALE"] else "F" if gender_str in ["F", "FEMALE"] else "O"
            
            name_age_gender_matches.append({
                "name": name,
                "age": age,
                "gender": gender,
                "position": match.start(),
            })
        
        # Now find seat information near each name
        seat_matches = []
        for pattern in self.seat_patterns:
            for match in pattern.finditer(text):
                if match.groups():
                    coach = match.group(1).upper()
                    seat_num = match.group(2)
                    berth = (match.group(3).upper() if len(match.groups()) > 2 and match.group(3) else "LB")
                    
                    if coach and seat_num:
                        try:
                            seat_number = int(seat_num)
                            seat_matches.append({
                                "coach": coach,
                                "seat_number": seat_number,
                                "berth_type": berth,
                                "position": match.start(),
                            })
                        except ValueError:
                            continue
        
        # Match names with seats (closest seat to each name)
        if name_age_gender_matches and seat_matches:
            for name_info in name_age_gender_matches:
                # Find closest seat match
                closest_seat = None
                min_distance = float('inf')
                
                for seat_info in seat_matches:
                    distance = abs(seat_info["position"] - name_info["position"])
                    if distance < min_distance:
                        min_distance = distance
                        closest_seat = seat_info
                
                if closest_seat and min_distance < 500:  # Reasonable distance threshold
                    passengers.append({
                        "name": name_info["name"],
                        "age": name_info["age"],
                        "gender": name_info["gender"],
                        "coach": closest_seat["coach"],
                        "seat_number": closest_seat["seat_number"],
                        "berth_type": closest_seat["berth_type"],
                        "booking_status": "CNF",
                        "current_status": "CNF",
                    })
        
        # Fallback: If we couldn't extract names, at least extract seat information
        if not passengers:
            for pattern in self.seat_patterns:
                matches = pattern.finditer(text)
                for match in matches:
                    if match.groups():
                        coach = match.group(1).upper()
                        seat_num = match.group(2)
                        berth = (match.group(3).upper() if len(match.groups()) > 2 and match.group(3) else "LB")
                        
                        if coach and seat_num:
                            try:
                                seat_number = int(seat_num)
                                passengers.append({
                                    "name": "Unknown",  # Placeholder
                                    "age": 0,
                                    "gender": "M",
                                    "coach": coach,
                                    "seat_number": seat_number,
                                    "berth_type": berth,
                                    "booking_status": "CNF",
                                    "current_status": "CNF",
                                })
                            except ValueError:
                                continue
        
        # Remove duplicates based on coach and seat number
        seen = set()
        unique_passengers = []
        for p in passengers:
            key = (p["coach"], p["seat_number"])
            if key not in seen:
                seen.add(key)
                unique_passengers.append(p)
        
        return unique_passengers
    
    def _get_mock_ticket_text(self) -> str:
        """Return mock ticket text for development/testing"""
        return """
        INDIAN RAILWAYS E-TICKET (ERS)
        PNR: 4521678901
        Train: 12301 HOWRAH RAJDHANI EXPRESS
        Date: 15-Jan-2025
        From: NDLS - NEW DELHI
        To: HWH - HOWRAH JUNCTION
        Class: 3A
        
        Passenger Details:
        # Name Age Gender Booking Status Current Status
        1. RAHUL KUMAR 35 MALE CNF/B2/45/LB CNF/B2/45/LB
        2. PRIYA KUMAR 32 FEMALE CNF/B2/47/MB CNF/B2/47/MB
        3. ARYAN KUMAR 8 MALE CNF/B3/12/UB CNF/B3/12/UB
        
        Booking Status: CNF
        """

