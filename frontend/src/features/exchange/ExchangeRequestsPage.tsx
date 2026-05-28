import { useState, useEffect, useCallback } from 'react'
import { Link } from 'react-router-dom'
import {
  Inbox,
  CheckCircle,
  XCircle,
  MessageCircle,
  Loader2,
  Train,
} from 'lucide-react'
import { Button } from '@/components/ui/Button'
import { Card, CardContent } from '@/components/ui/Card'
import { exchangeApi } from '@/services/api'
import type { ExchangeStatus, SeatInfo } from '@/types'

type TabType = 'received' | 'sent'

interface ExchangeRequestItem {
  id: string
  role: 'requester' | 'target'
  otherUser: { id: string; name: string; rating: number } | null
  trainNumber: string
  travelDate: string
  proposal: { give: SeatInfo[]; receive: SeatInfo[] }
  status: ExchangeStatus
  message?: string
  requesterConfirmed: boolean
  targetConfirmed: boolean
  canChat: boolean
  createdAt: string
}

function mapRequest(raw: any): ExchangeRequestItem {
  return {
    id: raw.id,
    role: raw.role,
    otherUser: raw.other_user
      ? {
          id: raw.other_user.id,
          name: raw.other_user.name,
          rating: raw.other_user.rating,
        }
      : null,
    trainNumber: raw.train_number,
    travelDate: raw.travel_date,
    proposal: {
      give: (raw.proposal?.give || []).map((s: any) => ({
        passengerId: s.passenger_id,
        passengerName: s.passenger_name,
        coach: s.coach,
        seatNumber: s.seat_number,
        berthType: s.berth_type,
      })),
      receive: (raw.proposal?.receive || []).map((s: any) => ({
        passengerId: s.passenger_id,
        passengerName: s.passenger_name,
        coach: s.coach,
        seatNumber: s.seat_number,
        berthType: s.berth_type,
      })),
    },
    status: raw.status,
    message: raw.message,
    requesterConfirmed: raw.requester_confirmed,
    targetConfirmed: raw.target_confirmed,
    canChat: raw.can_chat,
    createdAt: raw.created_at,
  }
}

function formatSeats(seats: SeatInfo[]) {
  return seats.map((s) => `${s.coach}/${s.seatNumber} ${s.berthType}`).join(', ')
}

function statusClass(status: ExchangeStatus) {
  switch (status) {
    case 'pending':
      return 'bg-yellow-100 text-yellow-800'
    case 'accepted':
      return 'bg-green-100 text-green-800'
    case 'declined':
      return 'bg-red-100 text-red-700'
    case 'completed':
      return 'bg-blue-100 text-blue-800'
    case 'expired':
      return 'bg-slate-100 text-slate-600'
    default:
      return 'bg-slate-100 text-slate-600'
  }
}

export function ExchangeRequestsPage() {
  const [activeTab, setActiveTab] = useState<TabType>('received')
  const [requests, setRequests] = useState<{ received: ExchangeRequestItem[]; sent: ExchangeRequestItem[] }>({
    received: [],
    sent: [],
  })
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [actionId, setActionId] = useState<string | null>(null)

  const loadRequests = useCallback(async () => {
    try {
      setIsLoading(true)
      setError(null)
      const response = await exchangeApi.getRequests()
      setRequests({
        received: (response.data.received || []).map(mapRequest),
        sent: (response.data.sent || []).map(mapRequest),
      })
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load exchange requests')
    } finally {
      setIsLoading(false)
    }
  }, [])

  useEffect(() => {
    loadRequests()
  }, [loadRequests])

  const runAction = async (id: string, action: () => Promise<unknown>) => {
    try {
      setActionId(id)
      setError(null)
      await action()
      await loadRequests()
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Action failed')
    } finally {
      setActionId(null)
    }
  }

  const list = requests[activeTab]

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 py-6 sm:py-8">
      <h1 className="page-title mb-6 sm:mb-8">Exchange Requests</h1>

      {error && (
        <Card className="mb-4 border-red-200 bg-red-50">
          <CardContent className="p-4 text-red-700 text-sm">{error}</CardContent>
        </Card>
      )}

      <div className="flex flex-wrap gap-2 mb-6">
        {(['received', 'sent'] as const).map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`px-4 py-2 rounded-lg font-medium transition-colors ${
              activeTab === tab
                ? 'bg-railway-blue text-white'
                : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
            }`}
          >
            {tab === 'received' ? 'Received' : 'Sent'}
            <span className="ml-2 bg-white/20 px-2 py-0.5 rounded-full text-sm">
              {requests[tab].length}
            </span>
          </button>
        ))}
      </div>

      {isLoading ? (
        <Card>
          <CardContent className="py-12 text-center text-slate-600">
            <Loader2 className="w-8 h-8 animate-spin mx-auto mb-3" />
            Loading requests...
          </CardContent>
        </Card>
      ) : list.length === 0 ? (
        <Card>
          <CardContent className="py-12 text-center">
            <Inbox className="w-16 h-16 text-slate-300 mx-auto mb-4" />
            <h3 className="font-semibold text-xl mb-2">No requests yet</h3>
            <p className="text-slate-600">
              {activeTab === 'received'
                ? "You haven't received any exchange requests"
                : "You haven't sent any exchange requests"}
            </p>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-4">
          {list.map((req) => {
            const busy = actionId === req.id
            return (
              <Card key={req.id}>
                <CardContent className="p-4 sm:p-6 space-y-4">
                  <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-3">
                    <div className="min-w-0">
                      <div className="flex flex-wrap items-center gap-2 mb-1">
                        <p className="font-semibold text-base sm:text-lg">
                          {activeTab === 'received' ? 'From' : 'To'}: {req.otherUser?.name || 'User'}
                        </p>
                        <span className={`text-xs px-2 py-0.5 rounded-full capitalize ${statusClass(req.status)}`}>
                          {req.status}
                        </span>
                      </div>
                      <p className="text-slate-600 text-sm flex items-center gap-1">
                        <Train className="w-4 h-4" />
                        {req.trainNumber} · {new Date(req.travelDate).toLocaleDateString('en-IN')}
                      </p>
                      {req.message && (
                        <p className="text-sm text-slate-500 mt-2 italic">"{req.message}"</p>
                      )}
                    </div>
                    {req.canChat && (
                      <Link to={`/chat/${req.id}`}>
                        <Button variant="ghost" size="sm">
                          <MessageCircle className="w-4 h-4 mr-1" /> Chat
                        </Button>
                      </Link>
                    )}
                  </div>

                  <div className="grid sm:grid-cols-2 gap-3 text-sm">
                    <div className="bg-slate-50 rounded-lg p-3">
                      <p className="font-medium text-slate-700 mb-1">You give</p>
                      <p className="text-slate-600 font-mono">
                        {formatSeats(activeTab === 'received' ? req.proposal.receive : req.proposal.give)}
                      </p>
                    </div>
                    <div className="bg-green-50 rounded-lg p-3">
                      <p className="font-medium text-green-800 mb-1">You get</p>
                      <p className="text-green-900 font-mono">
                        {formatSeats(activeTab === 'received' ? req.proposal.give : req.proposal.receive)}
                      </p>
                    </div>
                  </div>

                  <div className="flex flex-wrap gap-2">
                    {activeTab === 'received' && req.status === 'pending' && (
                      <>
                        <Button
                          size="sm"
                          variant="outline"
                          disabled={busy}
                          onClick={() => runAction(req.id, () => exchangeApi.respondToRequest(req.id, 'decline'))}
                        >
                          <XCircle className="w-4 h-4 mr-1" /> Decline
                        </Button>
                        <Button
                          size="sm"
                          disabled={busy}
                          onClick={() => runAction(req.id, () => exchangeApi.respondToRequest(req.id, 'accept'))}
                        >
                          <CheckCircle className="w-4 h-4 mr-1" /> Accept
                        </Button>
                      </>
                    )}
                    {activeTab === 'sent' && req.status === 'pending' && (
                      <Button
                        size="sm"
                        variant="outline"
                        disabled={busy}
                        onClick={() => runAction(req.id, () => exchangeApi.cancelRequest(req.id))}
                      >
                        Cancel request
                      </Button>
                    )}
                    {req.status === 'accepted' && (
                      <Button
                        size="sm"
                        disabled={busy}
                        onClick={() => runAction(req.id, () => exchangeApi.markCompleted(req.id))}
                      >
                        {req.role === 'requester'
                          ? req.requesterConfirmed
                            ? 'Waiting for partner'
                            : 'Confirm exchange done'
                          : req.targetConfirmed
                            ? 'Waiting for partner'
                            : 'Confirm exchange done'}
                      </Button>
                    )}
                  </div>
                </CardContent>
              </Card>
            )
          })}
        </div>
      )}
    </div>
  )
}
