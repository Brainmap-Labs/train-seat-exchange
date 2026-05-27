export function RefundPolicyPage() {
  return (
    <div className="max-w-4xl mx-auto py-20 px-4">
      <header className="text-center mb-8">
        <h1 className="font-display text-4xl font-bold mb-2">Refund Policy</h1>
        <p className="text-slate-600">Information about refunds for SeatSwap services.</p>
      </header>

      <section className="prose text-slate-700">
        <p>SeatSwap's core features are free. Paid features or credits, if any, will follow the refund rules described here and at purchase time.</p>

        <h2>Refund Eligibility</h2>
        <p>Refunds (where applicable) are evaluated on a case-by-case basis. Please contact support with your purchase details.</p>

        <h2>Contact</h2>
        <p>For refund requests: <a href="mailto:billing@seatswap.in" className="text-primary-600">billing@seatswap.in</a>.</p>
      </section>
    </div>
  )
}

export default RefundPolicyPage
