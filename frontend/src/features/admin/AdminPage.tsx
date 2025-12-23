import React, { useState } from 'react'

export function AdminPage() {
  const [train, setTrain] = useState('12301')
  const [date, setDate] = useState('')
  const [timeLimit, setTimeLimit] = useState(30)
  const [adminKey, setAdminKey] = useState('')
  const [output, setOutput] = useState('')
  const [authorized, setAuthorized] = useState(false)
  const [trips, setTrips] = useState<Array<{train_number: string; dates: string[]}>>([])

  async function preview() {
    if (!train || !date) {
      alert('Provide train and date')
      return
    }
    try {
      const res = await fetch(
        `/api/admin/preview-global-matching?train_number=${encodeURIComponent(train)}&travel_date=${encodeURIComponent(
          date,
        )}&time_limit=${timeLimit}`,
        {
          method: 'POST',
          headers: {
            'X-Admin-Key': adminKey,
            'Content-Type': 'application/json',
          },
        },
      )
      const j = await res.json()
      setOutput(JSON.stringify(j, null, 2))
    } catch (e) {
      setOutput(String(e))
    }
  }

  async function runGlobal() {
    if (!train || !date) {
      alert('Provide train and date')
      return
    }
    try {
      const res = await fetch(
        `/api/admin/run-global-matching?train_number=${encodeURIComponent(train)}&travel_date=${encodeURIComponent(
          date,
        )}&time_limit=${timeLimit}`,
        {
          method: 'POST',
          headers: {
            'X-Admin-Key': adminKey,
            'Content-Type': 'application/json',
          },
        },
      )
      const j = await res.json()
      setOutput(JSON.stringify(j, null, 2))
    } catch (e) {
      setOutput(String(e))
    }
  }

  async function viewTicket() {
    const ticketId = prompt('Ticket ID to view stored matches')
    if (!ticketId) return
    try {
      const res = await fetch(`/api/admin/matches/${encodeURIComponent(ticketId)}`, {
        headers: { 'X-Admin-Key': adminKey },
      })
      const j = await res.json()
      setOutput(JSON.stringify(j, null, 2))
    } catch (e) {
      setOutput(String(e))
    }
  }

  async function authorize() {
    if (!adminKey) {
      alert('Enter admin key')
      return
    }
    try {
      const res = await fetch('/api/admin/available-trips', { headers: { 'X-Admin-Key': adminKey } })
      if (!res.ok) {
        setAuthorized(false)
        setOutput('Authorization failed')
        return
      }
      const j = await res.json()
      setTrips(j.trips || [])
      // Preselect first trip if available
      if (j.trips && j.trips.length) {
        setTrain(j.trips[0].train_number)
        setDate(j.trips[0].dates && j.trips[0].dates.length ? j.trips[0].dates[0] : '')
      }
      setAuthorized(true)
      setOutput('Authorized')
    } catch (e) {
      setAuthorized(false)
      setOutput(String(e))
    }
  }

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-4">Admin Matching Console</h1>

      {!authorized ? (
        <div className="mb-4">
          <label className="block mb-1">Admin Key</label>
          <input
            className="border rounded px-2 py-1 w-full"
            value={adminKey}
            onChange={(e) => setAdminKey(e.target.value)}
            placeholder="X-Admin-Key"
          />
          <div className="mt-2">
            <button onClick={authorize} className="bg-blue-600 text-white px-4 py-2 rounded">Unlock</button>
          </div>
        </div>
      ) : (
        <>
          <div className="mb-4">
            <label className="block mb-1">Train number</label>
            <select className="border rounded px-2 py-1" value={train} onChange={(e) => setTrain(e.target.value)}>
              {trips.map((t) => (
                <option key={t.train_number} value={t.train_number}>
                  {t.train_number}
                </option>
              ))}
            </select>
          </div>

          <div className="mb-4">
            <label className="block mb-1">Travel date</label>
            <select className="border rounded px-2 py-1 w-full" value={date} onChange={(e) => setDate(e.target.value)}>
              {trips
                .filter((t) => t.train_number === train)
                .flatMap((t) => t.dates)
                .map((d) => (
                  <option key={d} value={d}>
                    {d}
                  </option>
                ))}
            </select>
          </div>
        </>
      )}

      <div className="mb-4">
        <label className="block mb-1">ILP Time Limit (s)</label>
        <input
          type="number"
          className="border rounded px-2 py-1 w-32"
          value={timeLimit}
          onChange={(e) => setTimeLimit(Number(e.target.value))}
        />
      </div>

      <div className="flex gap-2 mb-6">
        <button onClick={preview} className="bg-blue-600 text-white px-4 py-2 rounded">Preview ILP</button>
        <button onClick={runGlobal} className="bg-green-600 text-white px-4 py-2 rounded">Run & Persist ILP</button>
        <button onClick={viewTicket} className="bg-gray-600 text-white px-4 py-2 rounded">View Stored Matches</button>
      </div>

      <pre className="whitespace-pre-wrap bg-gray-100 p-4 rounded">{output}</pre>
    </div>
  )
}
