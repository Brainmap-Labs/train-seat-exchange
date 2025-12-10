import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import { ArrowLeft, Search, Star, Users, MapPin, Calendar, Train, TrendingUp } from 'lucide-react'
import { Button } from '@/components/ui/Button'
import { Card, CardContent, CardHeader } from '@/components/ui/Card'
import { ExchangeMatch, Ticket } from '@/types'
import { exchangeApi, ticketApi } from '@/services/api'
import { CoachVisualizer } from '@/components/coach/CoachVisualizer'

export function FindExchangePage() {
  const { ticketId } = useParams()
  const [isSearching, setIsSearching] = useState(false)
  const [matches, setMatches] = useState<ExchangeMatch[]>([])
  const [error, setError] = useState<string | null>(null)
  const [currentTicket, setCurrentTicket] = useState<Ticket | null>(null)
  const [isLoadingTicket, setIsLoadingTicket] = useState(true)
  const [selectedMatch, setSelectedMatch] = useState<ExchangeMatch | null>(null)

  useEffect(() => {
    if (ticketId) {
      loadCurrentTicket()
    }
  }, [ticketId])

  const loadCurrentTicket = async () => {
    if (!ticketId) return
    
    try {
      setIsLoadingTicket(true)
      const response = await ticketApi.getById(ticketId)
      const t = response.data
      
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
        passengers: (t.passengers || []).map((p: any) => ({
          id: p.id,
          name: p.name,
          age: p.age,
          gender: p.gender,
          coach: p.coach || p.coach,
          seatNumber: p.seatNumber !== undefined ? p.seatNumber : p.seat_number,
          berthType: p.berthType || p.berth_type,
          bookingStatus: p.bookingStatus || p.booking_status,
          currentStatus: p.currentStatus || p.current_status,
        })),
        createdAt: new Date(t.created_at || Date.now()),
        updatedAt: new Date(t.updated_at || Date.now()),
      }
      setCurrentTicket(transformedTicket)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load ticket')
      console.error('Error loading ticket:', err)
    } finally {
      setIsLoadingTicket(false)
    }
  }

  const handleSearch = async () => {
    if (!ticketId) return
    
    setIsSearching(true)
    setError(null)
    setSelectedMatch(null)
    
    try {
      const response = await exchangeApi.findMatches(ticketId)
      // Transform API response to ExchangeMatch format
      const transformedMatches: ExchangeMatch[] = (response.data.matches || []).map((m: any) => ({
        userId: m.user_id,
        userName: m.user_name || 'User',
        userRating: m.user_rating || 0,
        ticketId: m.ticket_id,
        matchScore: m.match_score || 0,
        benefitDescription: m.benefit_description || 'Potential exchange available',
        availableSeats: (m.available_seats || []).map((s: any) => ({
          passengerId: s.passengerId || s.passenger_id,
          passengerName: s.passengerName || s.passenger_name,
          coach: s.coach,
          seatNumber: s.seatNumber !== undefined ? s.seatNumber : s.seat_number,
          berthType: s.berthType || s.berth_type,
        })),
      }))
      setMatches(transformedMatches)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to find matches. Please try again.')
      console.error('Error finding matches:', err)
    } finally {
      setIsSearching(false)
    }
  }

  if (isLoadingTicket) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-8">
        <Card>
          <CardContent className="py-12 text-center">
            <p className="text-slate-600">Loading ticket...</p>
          </CardContent>
        </Card>
      </div>
    )
  }

  if (!currentTicket) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-8">
        <Card className="border-red-200 bg-red-50">
          <CardContent className="py-12 text-center">
            <p className="text-red-700 mb-4">Ticket not found</p>
            <Link to="/dashboard">
              <Button>Back to Dashboard</Button>
            </Link>
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      <Link to="/dashboard" className="inline-flex items-center text-slate-600 hover:text-railway-blue mb-6">
        <ArrowLeft className="w-4 h-4 mr-2" />
        Back to Dashboard
      </Link>

      {/* Ticket Header */}
      <Card className="mb-6 overflow-hidden">
        <div className="bg-gradient-to-r from-railway-blue to-blue-800 text-white p-6">
          <div className="flex items-start justify-between">
            <div>
              <div className="flex items-center gap-2 mb-2">
                <Train className="w-6 h-6 text-primary-400" />
                <span className="font-display text-2xl font-bold">
                  {currentTicket.trainNumber} {currentTicket.trainName}
                </span>
              </div>
              <div className="flex items-center gap-4 text-blue-200">
                <span className="flex items-center gap-1">
                  <Calendar className="w-4 h-4" />
                  {currentTicket.travelDate.toLocaleDateString('en-IN', { weekday: 'short', day: 'numeric', month: 'short', year: 'numeric' })}
                </span>
                <span className="flex items-center gap-1">
                  <MapPin className="w-4 h-4" />
                  {currentTicket.boardingStation.code} → {currentTicket.destinationStation.code}
                </span>
                <span className="flex items-center gap-1">
                  <Users className="w-4 h-4" />
                  {currentTicket.passengers.length} passenger{currentTicket.passengers.length !== 1 ? 's' : ''}
                </span>
              </div>
            </div>
            <div className="text-right">
              <p className="text-sm text-blue-200">PNR</p>
              <p className="font-mono text-xl font-bold">{currentTicket.pnr}</p>
            </div>
          </div>
        </div>
      </Card>

      <h1 className="font-display text-3xl font-bold text-slate-900 mb-2">Find Seat Exchange</h1>
      <p className="text-slate-600 mb-8">Find passengers willing to exchange seats to help your family sit together</p>

      {error && (
        <Card className="mb-6 border-red-200 bg-red-50">
          <CardContent className="p-4">
            <p className="text-red-700">{error}</p>
          </CardContent>
        </Card>
      )}

      {matches.length === 0 ? (
        <Card>
          <CardContent className="py-12 text-center">
            <Search className="w-16 h-16 text-slate-300 mx-auto mb-4" />
            <h3 className="font-semibold text-xl mb-2">Ready to Find Matches</h3>
            <p className="text-slate-600 mb-6">Click below to search for exchange opportunities on your train</p>
            <Button onClick={handleSearch} isLoading={isSearching} size="lg">
              <Search className="w-5 h-5 mr-2" />
              Search for Matches
            </Button>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-lg font-semibold text-slate-900">{matches.length} potential {matches.length === 1 ? 'match' : 'matches'} found</p>
              <p className="text-sm text-slate-600">Sorted by best match score</p>
            </div>
            <Button variant="outline" size="sm" onClick={handleSearch} isLoading={isSearching}>
              <Search className="w-4 h-4 mr-2" />
              Refresh
            </Button>
          </div>

          <div className="grid lg:grid-cols-2 gap-6">
            {/* Current Ticket View */}
            <Card>
              <CardHeader>
                <h3 className="font-display text-lg font-bold">Your Current Seats</h3>
                <p className="text-sm text-slate-600">Passengers are scattered across coaches</p>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {currentTicket.passengers.map((p) => (
                    <div key={p.id} className="flex items-center justify-between bg-slate-50 rounded-lg px-4 py-3">
                      <div>
                        <p className="font-medium">{p.name}</p>
                        <p className="text-sm text-slate-500">{p.age}yrs • {p.gender === 'M' ? 'Male' : 'Female'}</p>
                      </div>
                      <div className="text-right">
                        <p className="font-mono font-bold text-lg">{p.coach}/{p.seatNumber}</p>
                        <p className="text-sm text-slate-500">{p.berthType}</p>
                      </div>
                    </div>
                  ))}

                  {/* Coach Visualizations for all coaches */}
                  {Array.from(new Set(currentTicket.passengers.map(p => p.coach))).map(coach => (
                    <div className="mt-6" key={coach}>
                      <p className="text-sm font-medium text-slate-700 mb-2">Coach Layout - {coach}</p>
                      <div className="mb-2 flex items-center gap-4 text-xs text-slate-600">
                        <div className="flex items-center gap-2">
                          <div className="w-3 h-3 rounded bg-railway-blue ring-2 ring-primary-400" />
                          <span>Your seats</span>
                        </div>
                        {selectedMatch && (
                          <div className="flex items-center gap-2">
                            <div className="w-3 h-3 rounded bg-primary-400 ring-2 ring-primary-600" />
                            <span>Potential exchange seats</span>
                          </div>
                        )}
                      </div>
                      <CoachVisualizer
                        classType={currentTicket.classType as '3A' | 'SL' | '2A'}
                        passengers={currentTicket.passengers.filter(p => p.coach === coach)}
                        highlightSeats={
                          selectedMatch
                            ? selectedMatch.availableSeats
                                .filter(s => s.coach === coach)
                                .map(s => s.seatNumber)
                            : []
                        }
                      />
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* Matches List */}
            <div className="space-y-4">
              {matches.map((match) => (
                <Card 
                  key={match.userId} 
                  className={`hover:shadow-lg transition-all cursor-pointer ${
                    selectedMatch?.userId === match.userId ? 'ring-2 ring-railway-blue' : ''
                  }`}
                  onClick={() => setSelectedMatch(match)}
                >
                  <CardContent className="p-6">
                    <div className="flex items-start justify-between mb-4">
                      <div className="flex items-center gap-3">
                        <div className="w-12 h-12 bg-primary-100 rounded-full flex items-center justify-center">
                          <span className="font-bold text-primary-700 text-lg">{match.userName[0]}</span>
                        </div>
                        <div>
                          <h3 className="font-semibold text-lg">{match.userName}</h3>
                          <div className="flex items-center gap-1 text-sm text-slate-500">
                            <Star className="w-4 h-4 text-yellow-500 fill-yellow-500" />
                            <span>{match.userRating.toFixed(1)}</span>
                            <span className="text-slate-400">•</span>
                            <span>{match.availableSeats.length} seat{match.availableSeats.length !== 1 ? 's' : ''} available</span>
                          </div>
                        </div>
                      </div>
                      <div className="text-right">
                        <div className={`px-3 py-1 rounded-full text-sm font-bold ${
                          match.matchScore >= 70 ? 'bg-green-500 text-white' :
                          match.matchScore >= 50 ? 'bg-yellow-500 text-white' :
                          'bg-slate-400 text-white'
                        }`}>
                          {match.matchScore}% match
                        </div>
                      </div>
                    </div>
                    
                    <div className="bg-green-50 border border-green-200 rounded-lg p-3 mb-4">
                      <div className="flex items-start gap-2">
                        <TrendingUp className="w-5 h-5 text-green-600 mt-0.5" />
                        <p className="text-green-800 font-medium text-sm">{match.benefitDescription}</p>
                      </div>
                    </div>
                    
                    <div className="space-y-2 mb-4">
                      <p className="text-sm font-medium text-slate-700">Available Seats:</p>
                      <div className="flex flex-wrap gap-2">
                        {match.availableSeats.map((seat, idx) => (
                          <div key={idx} className="bg-blue-50 border border-blue-200 rounded-lg px-3 py-2">
                            <p className="font-mono font-bold text-blue-900">{seat.coach}/{seat.seatNumber}</p>
                            <p className="text-xs text-blue-600">{seat.berthType}</p>
                          </div>
                        ))}
                      </div>
                    </div>
                    
                    <Button 
                      className="w-full" 
                      size="sm"
                      onClick={(e) => {
                        e.stopPropagation()
                        // TODO: Navigate to send exchange request
                        console.log('Send exchange request to:', match.userId)
                      }}
                    >
                      Send Exchange Request
                    </Button>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>

          {/* Selected Match Detail View */}
          {selectedMatch && (
            <Card className="mt-6 border-2 border-railway-blue">
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="font-display text-lg font-bold">Exchange Preview with {selectedMatch.userName}</h3>
                    <p className="text-sm text-slate-600">Compare your seats with potential exchange</p>
                  </div>
                  <Button 
                    variant="outline" 
                    size="sm"
                    onClick={() => setSelectedMatch(null)}
                  >
                    Close
                  </Button>
                </div>
              </CardHeader>
              <CardContent>
                <div className="grid md:grid-cols-2 gap-6 mb-6">
                  <div>
                    <p className="text-sm font-medium text-slate-700 mb-3 flex items-center gap-2">
                      <span className="w-3 h-3 rounded bg-railway-blue"></span>
                      Your Current Seats
                    </p>
                    <div className="space-y-2">
                      {currentTicket.passengers.map((p) => (
                        <div key={p.id} className="flex items-center justify-between bg-slate-50 rounded-lg px-3 py-2 border border-slate-200">
                          <div>
                            <span className="text-sm font-medium">{p.name}</span>
                            <p className="text-xs text-slate-500">{p.age}yrs • {p.gender === 'M' ? 'Male' : 'Female'}</p>
                          </div>
                          <span className="font-mono font-bold">{p.coach}/{p.seatNumber} ({p.berthType})</span>
                        </div>
                      ))}
                    </div>
                  </div>
                  <div>
                    <p className="text-sm font-medium text-slate-700 mb-3 flex items-center gap-2">
                      <span className="w-3 h-3 rounded bg-primary-400"></span>
                      Available Seats for Exchange
                    </p>
                    <div className="space-y-2">
                      {selectedMatch.availableSeats.map((seat, idx) => {
                        // Check if this seat would help (same coach as any of your passengers)
                        const wouldHelp = currentTicket.passengers.some(p => p.coach === seat.coach)
                        return (
                          <div 
                            key={idx} 
                            className={`flex items-center justify-between rounded-lg px-3 py-2 border ${
                              wouldHelp 
                                ? 'bg-green-50 border-green-200' 
                                : 'bg-blue-50 border-blue-200'
                            }`}
                          >
                            <div>
                              <span className="text-sm font-medium">{seat.passengerName}</span>
                              {wouldHelp && (
                                <p className="text-xs text-green-600">✓ Same coach as your family</p>
                              )}
                            </div>
                            <span className="font-mono font-bold text-green-700">{seat.coach}/{seat.seatNumber} ({seat.berthType})</span>
                          </div>
                        )
                      })}
                    </div>
                  </div>
                </div>
                
                {/* Exchange Benefit Summary */}
                <div className="bg-gradient-to-r from-green-50 to-blue-50 rounded-lg p-4 border border-green-200">
                  <div className="flex items-start gap-3">
                    <TrendingUp className="w-6 h-6 text-green-600 mt-0.5" />
                    <div className="flex-1">
                      <p className="font-semibold text-green-900 mb-1">Exchange Benefit</p>
                      <p className="text-sm text-green-800">{selectedMatch.benefitDescription}</p>
                      <div className="mt-3 flex items-center gap-4 text-sm">
                        <span className="text-slate-600">Match Score: <span className="font-bold text-railway-blue">{selectedMatch.matchScore}%</span></span>
                        <span className="text-slate-400">•</span>
                        <span className="text-slate-600">User Rating: <span className="font-bold">{selectedMatch.userRating.toFixed(1)}</span></span>
                      </div>
                    </div>
                  </div>
                </div>
                
                <div className="mt-6 flex gap-3">
                  <Button 
                    className="flex-1"
                    onClick={() => {
                      // TODO: Navigate to send exchange request
                      console.log('Send exchange request to:', selectedMatch.userId)
                    }}
                  >
                    Send Exchange Request
                  </Button>
                  <Button 
                    variant="outline"
                    onClick={() => setSelectedMatch(null)}
                  >
                    Cancel
                  </Button>
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      )}
    </div>
  )
}

