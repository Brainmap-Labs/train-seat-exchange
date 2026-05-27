import { Link } from 'react-router-dom'
import { Users, Heart, Map } from 'lucide-react'

export function AboutPage() {
  return (
    <div className="max-w-5xl mx-auto py-20 px-4">
      <header className="text-center mb-12">
        <h1 className="font-display text-4xl md:text-5xl font-bold mb-4">About SeatSwap</h1>
        <p className="text-lg text-slate-600 max-w-2xl mx-auto">
          SeatSwap helps families and groups travel together by making it easy to exchange train seats with verified fellow passengers.
        </p>
      </header>

      <section className="grid md:grid-cols-3 gap-8 mb-12">
        <div className="bg-white rounded-xl p-6 shadow-sm">
          <Users className="w-8 h-8 text-railway-blue mb-4" />
          <h3 className="font-semibold text-lg mb-2">Community Driven</h3>
          <p className="text-slate-600 text-sm">Built for passengers helping passengers — we connect people traveling on the same train to swap seats safely.</p>
        </div>

        <div className="bg-white rounded-xl p-6 shadow-sm">
          <Heart className="w-8 h-8 text-railway-blue mb-4" />
          <h3 className="font-semibold text-lg mb-2">Family First</h3>
          <p className="text-slate-600 text-sm">Our mission is simple: keep families and companions together during rail journeys.</p>
        </div>

        <div className="bg-white rounded-xl p-6 shadow-sm">
          <Map className="w-8 h-8 text-railway-blue mb-4" />
          <h3 className="font-semibold text-lg mb-2">India-focused</h3>
          <p className="text-slate-600 text-sm">SeatSwap is tailored for Indian Railways features like coach layouts and PNR details.</p>
        </div>
      </section>

      <section className="prose max-w-none text-slate-700">
        <h2 className="font-display text-2xl font-bold mb-4">Our Story</h2>
        <p>
          SeatSwap started as a small idea to help a family sit together on a long journey. It grew into a lightweight platform that combines simple uploads, smart matching and secure in-app chat so passengers can coordinate exchanges reliably.
        </p>

        <h2 className="font-display text-2xl font-bold mt-8 mb-4">Safety & Trust</h2>
        <p>
          We prioritize safety — profiles, in-app messaging, and the ability to accept or decline requests put control in the hands of passengers. Always confirm details before agreeing to any exchange.
        </p>

        <div className="mt-8">
          <Link to="/contact" className="text-primary-600 hover:underline">Contact our team</Link>
        </div>
      </section>
    </div>
  )
}

export default AboutPage
