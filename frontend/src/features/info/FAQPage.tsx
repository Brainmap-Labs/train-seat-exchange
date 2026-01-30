export function FAQPage() {
  return (
    <div className="max-w-4xl mx-auto py-20 px-4">
      <header className="text-center mb-12">
        <h1 className="font-display text-4xl font-bold mb-4">Frequently Asked Questions</h1>
        <p className="text-slate-600">Quick answers to common questions about SeatSwap.</p>
      </header>

      <section className="space-y-4">
        <details className="bg-white p-6 rounded-lg shadow-sm">
          <summary className="font-semibold cursor-pointer">Is SeatSwap free to use?</summary>
          <div className="mt-3 text-slate-600">Yes — basic features including uploading tickets, searching for matches and messaging are free.</div>
        </details>

        <details className="bg-white p-6 rounded-lg shadow-sm">
          <summary className="font-semibold cursor-pointer">How do you verify users?</summary>
          <div className="mt-3 text-slate-600">We use profile checks and allow users to mark themselves verified. Always confirm before meeting or swapping seats.</div>
        </details>

        <details className="bg-white p-6 rounded-lg shadow-sm">
          <summary className="font-semibold cursor-pointer">What if someone doesn't show up?</summary>
          <div className="mt-3 text-slate-600">SeatSwap facilitates introductions but cannot enforce exchanges. We recommend confirming timing and seat specifics in chat beforehand.</div>
        </details>

        <details className="bg-white p-6 rounded-lg shadow-sm">
          <summary className="font-semibold cursor-pointer">Can I cancel an accepted exchange?</summary>
          <div className="mt-3 text-slate-600">Yes — you can cancel, but please communicate via chat to avoid inconvenience. Repeated cancellations may affect trust with other users.</div>
        </details>
      </section>
    </div>
  )
}

export default FAQPage
