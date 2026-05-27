import { useState } from 'react'
import { Button } from '@/components/ui/Button'

export function ContactPage() {
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [message, setMessage] = useState('')

  return (
    <div className="max-w-3xl mx-auto py-20 px-4">
      <header className="text-center mb-12">
        <h1 className="font-display text-4xl font-bold mb-2">Contact Us</h1>
        <p className="text-slate-600">Have a question or feedback? Send us a message and we'll respond as soon as we can.</p>
      </header>

      <form className="space-y-4 bg-white p-6 rounded-lg shadow-sm">
        <label className="block">
          <span className="text-sm font-medium text-slate-700">Name</span>
          <input value={name} onChange={e => setName(e.target.value)} className="mt-1 block w-full rounded-md border-gray-200" />
        </label>

        <label className="block">
          <span className="text-sm font-medium text-slate-700">Email</span>
          <input value={email} onChange={e => setEmail(e.target.value)} className="mt-1 block w-full rounded-md border-gray-200" />
        </label>

        <label className="block">
          <span className="text-sm font-medium text-slate-700">Message</span>
          <textarea value={message} onChange={e => setMessage(e.target.value)} rows={6} className="mt-1 block w-full rounded-md border-gray-200" />
        </label>

        <div className="text-right">
          <Button type="button">Send Message</Button>
        </div>
      </form>

      <div className="mt-8 text-slate-600">
        <p>If you'd rather email us directly: <a href="mailto:support@seatswap.in" className="text-primary-600 hover:underline">support@seatswap.in</a></p>
      </div>
    </div>
  )
}

export default ContactPage
