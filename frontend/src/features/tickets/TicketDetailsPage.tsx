import { useParams, Link, useNavigate } from 'react-router-dom'
import { useEffect, useState } from 'react'
import { ArrowLeft, Train, Calendar, MapPin } from 'lucide-react'
import { Button } from '@/components/ui/Button'
import { Card, CardContent, CardHeader } from '@/components/ui/Card'
import { CoachVisualizer } from '@/components/coach/CoachVisualizer'
import { ticketApi } from '@/services/api'
import { Ticket } from '@/types'

export function TicketDetailsPage() {
  const { ticketId } = useParams()
  const navigate = useNavigate()
  const [ticket, setTicket] = useState<Ticket | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (ticketId) {
      loadTicket()
    }
  }, [ticketId])

  const loadTicket = async () => {
    if (!ticketId) return
    
    try {
      setIsLoading(true)
      setError(null)
      const response = await ticketApi.getById(ticketId)
      const t = response.data
      
      // Transform API response to Ticket format
      const transformedTicket: Ticket = {
        id: t.id,
        userId: '',
        pnr: t.pnr,
        trainNumber: t.train_number,
        trainName: t.train_name,
        travelDate: new Date(t.travel_date),
        boardingStation: t.boarding_station,
        destinationStation: t.destination_station,
        classType: t.class_type,
        quota: t.quota || 'GN',
        status: t.status || 'active',
        passengers: t.passengers || [],
        createdAt: new Date(t.created_at || Date.now()),
        updatedAt: new Date(t.updated_at || Date.now()),
      }
      setTicket(transformedTicket)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load ticket')
      console.error('Error loading ticket:', err)
    } finally {
      setIsLoading(false)
    }
  }

  if (isLoading) {
    return (
      <div className="max-w-5xl mx-auto px-4 py-8">
        <Card>
          <CardContent className="py-12 text-center">
            <p className="text-slate-600">Loading ticket...</p>
          </CardContent>
        </Card>
      </div>
    )
  }

  if (error || !ticket) {
    return (
      <div className="max-w-5xl mx-auto px-4 py-8">
        <Card className="border-red-200 bg-red-50">
          <CardContent className="py-12 text-center">
            <p className="text-red-700 mb-4">{error || 'Ticket not found'}</p>
            <Button onClick={() => navigate('/dashboard')}>Back to Dashboard</Button>
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="max-w-5xl mx-auto px-4 py-8">
      <Link to="/dashboard" className="inline-flex items-center text-slate-600 hover:text-railway-blue mb-6">
        <ArrowLeft className="w-4 h-4 mr-2" />
        Back to Dashboard
      </Link>

      {/* Header Card */}
      <Card className="mb-6 overflow-hidden">
        <div className="bg-gradient-to-r from-railway-blue to-blue-800 text-white p-6">
          <div className="flex items-start justify-between">
            <div>
              <div className="flex items-center gap-2 mb-2">
                <Train className="w-6 h-6 text-primary-400" />
                <span className="font-display text-2xl font-bold">
                  {ticket.trainNumber} {ticket.trainName}
                </span>
              </div>
              <div className="flex items-center gap-4 text-blue-200">
                <span className="flex items-center gap-1">
                  <Calendar className="w-4 h-4" />
                  {ticket.travelDate.toLocaleDateString('en-IN', { weekday: 'short', day: 'numeric', month: 'short', year: 'numeric' })}
                </span>
                <span className="flex items-center gap-1">
                  <MapPin className="w-4 h-4" />
                  {ticket.boardingStation.code} → {ticket.destinationStation.code}
                </span>
              </div>
            </div>
            <div className="text-right">
              <p className="text-sm text-blue-200">PNR</p>
              <p className="font-mono text-xl font-bold">{ticket.pnr}</p>
            </div>
          </div>
        </div>
      </Card>

      <div className="grid lg:grid-cols-2 gap-6">
        {/* Passengers */}
        <Card>
          <CardHeader>
            <h3 className="font-display text-lg font-bold">Passengers</h3>
          </CardHeader>
          <CardContent className="space-y-3">
            {ticket.passengers.map((p) => (
              <div key={p.id} className="flex items-center justify-between bg-slate-50 rounded-lg px-4 py-3">
                <div>
                  <p className="font-medium">{p.name}</p>
                  <p className="text-sm text-slate-500">{p.age}yrs • {p.gender === 'M' ? 'Male' : 'Female'}</p>
                </div>
                <div className="text-right">
                  <p className="font-mono font-bold">{p.coach}/{p.seatNumber}</p>
                  <p className="text-sm text-slate-500">{p.berthType}</p>
                </div>
              </div>
            ))}
          </CardContent>
        </Card>

        {/* Coach Layout */}
        <Card>
          <CardHeader>
            <h3 className="font-display text-lg font-bold">Coach Layout - B2</h3>
          </CardHeader>
          <CardContent>
            <CoachVisualizer 
              classType={ticket.classType}
              passengers={ticket.passengers.filter(p => p.coach === 'B2')}
            />
          </CardContent>
        </Card>
      </div>

      {/* Actions */}
      <div className="mt-6 flex gap-4">
        <Link to={`/exchange/find/${ticketId}`} className="flex-1">
          <Button className="w-full">Find Seat Exchange</Button>
        </Link>
      </div>
    </div>
  )
}

