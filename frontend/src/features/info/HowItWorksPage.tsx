import { Upload, Search, MessageCircle } from 'lucide-react'

export function HowItWorksPage() {
  return (
    <div className="max-w-5xl mx-auto py-20 px-4">
      <header className="text-center mb-12">
        <h1 className="font-display text-4xl md:text-5xl font-bold mb-4">How It Works</h1>
        <p className="text-lg text-slate-600 max-w-2xl mx-auto">
          A simple, three-step flow to help you find matching passengers and swap seats safely.
        </p>
      </header>

      <section className="grid md:grid-cols-3 gap-8">
        <div className="bg-white rounded-2xl p-8 shadow-sm">
          <div className="bg-blue-500 w-14 h-14 rounded-xl flex items-center justify-center mb-6">
            <Upload className="w-7 h-7 text-white" />
          </div>
          <h3 className="font-display text-xl font-bold mb-3">Upload Your Ticket</h3>
          <p className="text-slate-600">Take a photo or upload your e-ticket. Our OCR extracts PNR, coach and seat details automatically.</p>
        </div>

        <div className="bg-white rounded-2xl p-8 shadow-sm">
          <div className="bg-primary-500 w-14 h-14 rounded-xl flex items-center justify-center mb-6">
            <Search className="w-7 h-7 text-white" />
          </div>
          <h3 className="font-display text-xl font-bold mb-3">Find Matches</h3>
          <p className="text-slate-600">We search for passengers on the same train who might be willing to exchange seats based on preferences and coach layout.</p>
        </div>

        <div className="bg-white rounded-2xl p-8 shadow-sm">
          <div className="bg-green-500 w-14 h-14 rounded-xl flex items-center justify-center mb-6">
            <MessageCircle className="w-7 h-7 text-white" />
          </div>
          <h3 className="font-display text-xl font-bold mb-3">Connect & Confirm</h3>
          <p className="text-slate-600">Chat securely in-app to agree on the exchange. Accept or decline requests — you stay in control.</p>
        </div>
      </section>

      <section className="mt-12 prose text-slate-700">
        <h2 className="font-display text-2xl">Tips</h2>
        <ul>
          <li>Verify coach and seat numbers before confirming an exchange.</li>
          <li>Prefer exchanges with verified profiles or repeat users.</li>
          <li>Use our chat to clarify timings and meet-up locations inside the coach.</li>
        </ul>
      </section>
    </div>
  )
}

export default HowItWorksPage
