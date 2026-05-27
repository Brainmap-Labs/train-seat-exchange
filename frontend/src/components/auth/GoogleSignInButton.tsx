import { useEffect, useRef, useState } from 'react'
import { GoogleLogin } from '@react-oauth/google'
import { isGoogleAuthConfigured } from '@/hooks/useGoogleAuth'

interface GoogleSignInButtonProps {
  onSuccess: Parameters<typeof GoogleLogin>[0]['onSuccess']
  onError?: Parameters<typeof GoogleLogin>[0]['onError']
  text?: 'signin_with' | 'signup_with' | 'continue_with' | 'signin'
}

export function GoogleSignInButton({
  onSuccess,
  onError,
  text = 'continue_with',
}: GoogleSignInButtonProps) {
  const containerRef = useRef<HTMLDivElement>(null)
  const [buttonWidth, setButtonWidth] = useState(320)

  useEffect(() => {
    const el = containerRef.current
    if (!el) return

    const updateWidth = () => {
      setButtonWidth(Math.min(Math.max(el.offsetWidth, 240), 400))
    }

    updateWidth()
    const observer = new ResizeObserver(updateWidth)
    observer.observe(el)
    return () => observer.disconnect()
  }, [])

  if (!isGoogleAuthConfigured) {
    return null
  }

  return (
    <div ref={containerRef} className="w-full">
      <GoogleLogin
        onSuccess={onSuccess}
        onError={onError}
        useOneTap={false}
        theme="outline"
        size="large"
        text={text}
        shape="rectangular"
        width={buttonWidth}
      />
    </div>
  )
}
