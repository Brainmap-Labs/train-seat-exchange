export function TermsOfServicePage() {
  return (
    <div className="max-w-4xl mx-auto py-20 px-4">
      <header className="text-center mb-8">
        <h1 className="font-display text-4xl font-bold mb-2">Terms of Service</h1>
        <p className="text-slate-600">The rules and guidelines for using SeatSwap.</p>
      </header>

      <section className="prose text-slate-700">
        <h2>Acceptance</h2>
        <p>By using SeatSwap you agree to these terms. Please read them carefully.</p>

        <h2>User Conduct</h2>
        <p>Users must behave respectfully, provide accurate information, and not misuse the platform. SeatSwap may suspend or remove accounts that violate rules.</p>

        <h2>Limitations</h2>
        <p>SeatSwap facilitates introductions and messaging but is not responsible for exchanges or travel outcomes. Use discretion when meeting or swapping seats.</p>

        <h2>Contact</h2>
        <p>For TOS questions: <a href="mailto:tos@seatswap.in" className="text-primary-600">tos@seatswap.in</a>.</p>
      </section>
    </div>
  )
}

export default TermsOfServicePage
