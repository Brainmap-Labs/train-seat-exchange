import { format } from 'date-fns'
import { Train, Calendar, Users, ArrowRight, Trash2 } from 'lucide-react'
import { Link } from 'react-router-dom'
import { Ticket } from '@/types'
import { Card } from '@/components/ui/Card'
import { clsx } from 'clsx'

interface TicketCardProps {
  ticket: Ticket
  showActions?: boolean
  onDelete?: (ticketId: string) => void
}

export function TicketCard({ ticket, showActions = true, onDelete }: TicketCardProps) {
  const isScattered = new Set(ticket.passengers.map(p => p.coach)).size > 1

  return (
    <Card className="overflow-hidden hover:shadow-xl transition-shadow">
      {/* Header */}
      <div className="bg-gradient-to-r from-railway-blue to-blue-800 text-white px-4 sm:px-6 py-4">
        <div className="flex items-start justify-between gap-3">
          <div className="flex-1 min-w-0">
            <div className="flex items-start gap-2">
              <Train className="w-5 h-5 text-primary-400 shrink-0 mt-0.5" />
              <span className="font-display font-bold text-base sm:text-lg break-words">
                {ticket.trainNumber} {ticket.trainName}
              </span>
            </div>
            <div className="flex items-center gap-2 mt-1 text-blue-200 text-sm">
              <Calendar className="w-4 h-4" />
              <span>{format(new Date(ticket.travelDate), 'EEE, dd MMM yyyy')}</span>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <div className="bg-primary-500 text-railway-blue px-3 py-1 rounded-full text-sm font-bold">
              {ticket.classType}
            </div>
            {onDelete && (
              <button
                onClick={() => onDelete(ticket.id)}
                className="p-1.5 hover:bg-white/20 rounded-lg transition-colors"
                title="Delete ticket"
              >
                <Trash2 className="w-4 h-4 text-white" />
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Route */}
      <div className="px-4 sm:px-6 py-4 border-b border-slate-100">
        <div className="flex flex-col sm:flex-row sm:items-center gap-3 sm:gap-4">
          <div className="flex-1 min-w-0">
            <p className="text-sm text-slate-500">From</p>
            <p className="font-semibold">{ticket.boardingStation.code}</p>
            <p className="text-sm text-slate-600 truncate">{ticket.boardingStation.name}</p>
          </div>
          <ArrowRight className="w-5 h-5 text-slate-400 hidden sm:block shrink-0" />
          <div className="flex-1 sm:text-right min-w-0">
            <p className="text-sm text-slate-500">To</p>
            <p className="font-semibold">{ticket.destinationStation.code}</p>
            <p className="text-sm text-slate-600 truncate">{ticket.destinationStation.name}</p>
          </div>
        </div>
      </div>

      {/* Passengers */}
      <div className="px-4 sm:px-6 py-4">
        <div className="flex items-center gap-2 mb-3">
          <Users className="w-4 h-4 text-slate-400" />
          <span className="text-sm font-medium text-slate-700">
            {ticket.passengers.length} Passenger{ticket.passengers.length > 1 ? 's' : ''}
          </span>
          {isScattered && (
            <span className="bg-red-100 text-red-700 text-xs px-2 py-0.5 rounded-full">
              Scattered
            </span>
          )}
        </div>

        <div className="space-y-2">
          {ticket.passengers.map((passenger) => (
            <div
              key={passenger.id}
              className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-1 bg-slate-50 rounded-lg px-3 py-2"
            >
              <div>
                <p className="font-medium text-sm">{passenger.name}</p>
                <p className="text-xs text-slate-500">
                  {passenger.age}yr  {passenger.gender === 'M' ? 'Male' : 'Female'}
                </p>
              </div>
              <div className="text-right">
                <p className="font-mono font-bold text-sm">
                  {passenger.coach}/{passenger.seatNumber}
                </p>
                <p className={clsx(
                  'text-xs font-medium',
                  passenger.berthType === 'LB' && 'text-berth-lower',
                  passenger.berthType === 'MB' && 'text-berth-middle',
                  passenger.berthType === 'UB' && 'text-berth-upper',
                  (passenger.berthType === 'SL' || passenger.berthType === 'SU') && 'text-berth-side',
                )}>
                  {passenger.berthType}
                </p>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Actions */}
      {showActions && (
        <div className="px-4 sm:px-6 py-4 bg-slate-50 flex flex-col sm:flex-row gap-2 sm:gap-3">
          <Link
            to={`/tickets/${ticket.id}`}
            className="flex-1 text-center py-2.5 text-sm font-medium text-slate-600 hover:text-railway-blue transition-colors rounded-lg border border-slate-200 sm:border-0"
          >
            View Details
          </Link>
          <Link
            to={`/exchange/find/${ticket.id}`}
            className="flex-1 text-center py-2.5 bg-railway-blue text-white rounded-lg text-sm font-medium hover:bg-blue-900 transition-colors"
          >
            Find Exchange
          </Link>
        </div>
      )}
    </Card>
  )
}

