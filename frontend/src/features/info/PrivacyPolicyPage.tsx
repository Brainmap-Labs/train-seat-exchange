export function PrivacyPolicyPage() {
  return (
    <div className="max-w-4xl mx-auto py-20 px-4">
      <header className="text-center mb-8">
        <h1 className="font-display text-4xl font-bold mb-2">Privacy Policy</h1>
        <p className="text-slate-600">How SeatSwap collects, uses, and protects your information.</p>
      </header>

      <section className="prose text-slate-700">
        <h2>Information We Collect</h2>
        <p>We collect details you provide such as profile information, uploaded ticket data (PNR, coach, seat), and messages exchanged with other users.</p>

        <h2>How We Use Data</h2>
        <p>Data is used to provide matching services, power OCR and coach layouts, enable messaging, and improve the platform. We do not sell personal data to third parties.</p>

        <h2>Security</h2>
        <p>We take reasonable measures to secure your data, but no system is completely secure. Please keep sensitive information private and report any concerns via the contact page.</p>

        <h2>Contact</h2>
        <p>Questions about privacy can be sent to <a href="mailto:privacy@seatswap.in" className="text-primary-600">privacy@seatswap.in</a>.</p>
      </section>
    </div>
  )
}

export default PrivacyPolicyPage
