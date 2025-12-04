import { useState } from 'react'
import { Link } from 'react-router-dom'
import { Inbox, CheckCircle, XCircle, MessageCircle } from 'lucide-react'
import { Button } from '@/components/ui/Button'
import { Card, CardContent } from '@/components/ui/Card'

type TabType = 'received' | 'sent'

export function ExchangeRequestsPage() {
  const [activeTab, setActiveTab] = useState<TabType>('received')

  const requests = {
    received: [
      { id: '1', from: 'Amit Sharma', train: '12301 Rajdhani', seat: 'B2/46 LB', status: 'pending' },
    ],
    sent: [
      { id: '2', to: 'Sneha Patel', train: '12301 Rajdhani', seat: 'B2/48 UB', status: 'pending' },
    ],
  }

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      <h1 className="font-display text-3xl font-bold text-slate-900 mb-8">Exchange Requests</h1>

      {/* Tabs */}
      <div className="flex gap-2 mb-6">
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

      {/* Requests List */}
      {requests[activeTab].length === 0 ? (
        <Card>
          <CardContent className="py-12 text-center">
            <Inbox className="w-16 h-16 text-slate-300 mx-auto mb-4" />
            <h3 className="font-semibold text-xl mb-2">No requests yet</h3>
            <p className="text-slate-600">
              {activeTab === 'received' 
                ? "You haven't received any exchange requests"
                : "You haven't sent any exchange requests"
              }
            </p>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-4">
          {requests[activeTab].map((req) => (
            <Card key={req.id}>
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-semibold text-lg">
                      {activeTab === 'received' ? `From: ${req.from}` : `To: ${req.to}`}
                    </p>
                    <p className="text-slate-600">{req.train}</p>
                    <p className="text-sm text-slate-500">Seat: {req.seat}</p>
                  </div>
                  <div className="flex gap-2">
                    {activeTab === 'received' && req.status === 'pending' && (
                      <>
                        <Button variant="outline" size="sm">
                          <XCircle className="w-4 h-4 mr-1" /> Decline
                        </Button>
                        <Button size="sm">
                          <CheckCircle className="w-4 h-4 mr-1" /> Accept
                        </Button>
                      </>
                    )}
                    <Link to={`/chat/${req.id}`}>
                      <Button variant="ghost" size="sm">
                        <MessageCircle className="w-4 h-4" />
                      </Button>
                    </Link>
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

