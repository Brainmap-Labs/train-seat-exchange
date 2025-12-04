import { useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { ArrowLeft, Search, Star, ArrowRight } from 'lucide-react'
import { Button } from '@/components/ui/Button'
import { Card, CardContent, CardHeader } from '@/components/ui/Card'
import { ExchangeMatch } from '@/types'

export function FindExchangePage() {
  const { ticketId } = useParams()
  const [isSearching, setIsSearching] = useState(false)
  const [matches, setMatches] = useState<ExchangeMatch[]>([])

  const handleSearch = async () => {
    setIsSearching(true)
    // TODO: API call
    await new Promise(r => setTimeout(r, 1500))
    setMatches([
      {
        userId: '2',
        userName: 'Amit Sharma',
        userRating: 4.8,
        ticketId: '2',
        matchScore: 95,
        benefitDescription: 'Get seat 46 (LB) in B2 - Adjacent to your family!',
        availableSeats: [{ passengerId: '4', passengerName: 'Amit', coach: 'B2', seatNumber: 46, berthType: 'LB' }],
      },
      {
        userId: '3',
        userName: 'Sneha Patel',
        userRating: 4.5,
        ticketId: '3',
        matchScore: 80,
        benefitDescription: 'Get seat 48 (UB) in B2 - Same bay as your family',
        availableSeats: [{ passengerId: '5', passengerName: 'Sneha', coach: 'B2', seatNumber: 48, berthType: 'UB' }],
      },
    ])
    setIsSearching(false)
  }

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      <Link to="/dashboard" className="inline-flex items-center text-slate-600 hover:text-railway-blue mb-6">
        <ArrowLeft className="w-4 h-4 mr-2" />
        Back to Dashboard
      </Link>

      <h1 className="font-display text-3xl font-bold text-slate-900 mb-2">Find Seat Exchange</h1>
      <p className="text-slate-600 mb-8">We'll find passengers who might exchange seats with you</p>

      {matches.length === 0 ? (
        <Card>
          <CardContent className="py-12 text-center">
            <Search className="w-16 h-16 text-slate-300 mx-auto mb-4" />
            <h3 className="font-semibold text-xl mb-2">Ready to Find Matches</h3>
            <p className="text-slate-600 mb-6">Click below to search for exchange opportunities</p>
            <Button onClick={handleSearch} isLoading={isSearching}>
              <Search className="w-5 h-5 mr-2" />
              Search for Matches
            </Button>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <p className="text-slate-600">{matches.length} potential matches found</p>
            <Button variant="outline" size="sm" onClick={handleSearch} isLoading={isSearching}>
              Refresh
            </Button>
          </div>

          {matches.map((match) => (
            <Card key={match.userId} className="hover:shadow-lg transition-shadow">
              <CardContent className="p-6">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <div className="w-12 h-12 bg-primary-100 rounded-full flex items-center justify-center">
                        <span className="font-bold text-primary-700">{match.userName[0]}</span>
                      </div>
                      <div>
                        <h3 className="font-semibold text-lg">{match.userName}</h3>
                        <div className="flex items-center gap-1 text-sm text-slate-500">
                          <Star className="w-4 h-4 text-yellow-500 fill-yellow-500" />
                          <span>{match.userRating}</span>
                        </div>
                      </div>
                    </div>
                    <div className="bg-green-50 border border-green-200 rounded-lg p-3 mb-4">
                      <p className="text-green-800 font-medium">{match.benefitDescription}</p>
                    </div>
                    <div className="flex items-center gap-2 text-sm text-slate-600">
                      <span className="font-mono bg-slate-100 px-2 py-1 rounded">
                        {match.availableSeats[0].coach}/{match.availableSeats[0].seatNumber}
                      </span>
                      <ArrowRight className="w-4 h-4" />
                      <span>Exchange for your B3/12</span>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="bg-railway-blue text-white px-3 py-1 rounded-full text-sm font-bold mb-4">
                      {match.matchScore}% match
                    </div>
                    <Button size="sm">Send Request</Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  )
}

