import { clsx } from 'clsx'
import { BerthType, Passenger } from '@/types'

interface CoachVisualizerProps {
  classType: '3A' | 'SL' | '2A'
  passengers: Passenger[]
  highlightSeats?: number[]
  onSeatClick?: (seatNumber: number) => void
}

export function CoachVisualizer({ 
  classType, 
  passengers, 
  highlightSeats = [],
  onSeatClick 
}: CoachVisualizerProps) {
  const totalBerths = classType === '2A' ? 48 : classType === '3A' ? 64 : 72
  const baySize = classType === '2A' ? 6 : 8
  const totalBays = Math.ceil(totalBerths / baySize)

  const getBerthType = (seatNum: number): BerthType => {
    const posInBay = seatNum % baySize || baySize
    if (classType === '2A') {
      if (posInBay === 1 || posInBay === 4) return 'LB'
      if (posInBay === 2 || posInBay === 5) return 'UB'
      if (posInBay === 3) return 'SL'
      return 'SU'
    }
    if (posInBay === 1 || posInBay === 4) return 'LB'
    if (posInBay === 2 || posInBay === 5) return 'MB'
    if (posInBay === 3 || posInBay === 6) return 'UB'
    if (posInBay === 7) return 'SL'
    return 'SU'
  }

  const isPassengerSeat = (seatNum: number) => 
    passengers.some(p => p.seatNumber === seatNum)

  const isHighlighted = (seatNum: number) => 
    highlightSeats.includes(seatNum)

  const getBerthColor = (type: BerthType) => {
    const colors = {
      LB: 'bg-berth-lower',
      MB: 'bg-berth-middle',
      UB: 'bg-berth-upper',
      SL: 'bg-berth-side',
      SU: 'bg-berth-side',
    }
    return colors[type]
  }

  return (
    <div className="bg-slate-100 rounded-2xl p-4 overflow-x-auto">
      <div className="flex items-center gap-4 mb-4">
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 rounded bg-berth-lower" />
          <span className="text-xs text-slate-600">Lower</span>
        </div>
        {classType !== '2A' && (
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded bg-berth-middle" />
            <span className="text-xs text-slate-600">Middle</span>
          </div>
        )}
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 rounded bg-berth-upper" />
          <span className="text-xs text-slate-600">Upper</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 rounded bg-berth-side" />
          <span className="text-xs text-slate-600">Side</span>
        </div>
      </div>

      <div className="space-y-3">
        {Array.from({ length: totalBays }, (_, bayIndex) => {
          const bayStart = bayIndex * baySize + 1
          return (
            <div key={bayIndex} className="flex items-center gap-2">
              <span className="text-xs text-slate-400 w-12">Bay {bayIndex + 1}</span>
              <div className="flex gap-1">
                {/* Main berths */}
                <div className="grid grid-cols-3 gap-1">
                  {[0, 1, 2].map(col => {
                    const seatNum = bayStart + col
                    if (seatNum > totalBerths) return null
                    const berthType = getBerthType(seatNum)
                    return (
                      <button
                        key={seatNum}
                        onClick={() => onSeatClick?.(seatNum)}
                        className={clsx(
                          'w-10 h-10 rounded-lg text-xs font-bold transition-all',
                          isPassengerSeat(seatNum)
                            ? 'bg-railway-blue text-white ring-2 ring-primary-400'
                            : isHighlighted(seatNum)
                            ? 'bg-primary-400 text-railway-blue ring-2 ring-primary-600'
                            : `${getBerthColor(berthType)} text-white opacity-50`,
                          onSeatClick && 'cursor-pointer hover:opacity-100'
                        )}
                      >
                        {seatNum}
                      </button>
                    )
                  })}
                </div>
                <div className="grid grid-cols-3 gap-1">
                  {[3, 4, 5].map(col => {
                    const seatNum = bayStart + col
                    if (seatNum > totalBerths || (classType === '2A' && col > 4)) return null
                    const berthType = getBerthType(seatNum)
                    return (
                      <button
                        key={seatNum}
                        onClick={() => onSeatClick?.(seatNum)}
                        className={clsx(
                          'w-10 h-10 rounded-lg text-xs font-bold transition-all',
                          isPassengerSeat(seatNum)
                            ? 'bg-railway-blue text-white ring-2 ring-primary-400'
                            : isHighlighted(seatNum)
                            ? 'bg-primary-400 text-railway-blue ring-2 ring-primary-600'
                            : `${getBerthColor(berthType)} text-white opacity-50`,
                          onSeatClick && 'cursor-pointer hover:opacity-100'
                        )}
                      >
                        {seatNum}
                      </button>
                    )
                  })}
                </div>

                {/* Aisle */}
                <div className="w-6 flex items-center justify-center">
                  <div className="w-1 h-8 bg-slate-300 rounded" />
                </div>

                {/* Side berths */}
                <div className="grid grid-cols-1 gap-1">
                  {[6, 7].map(col => {
                    const seatNum = bayStart + col
                    if (seatNum > totalBerths || (classType === '2A' && col > 5)) return null
                    const berthType = getBerthType(seatNum)
                    return (
                      <button
                        key={seatNum}
                        onClick={() => onSeatClick?.(seatNum)}
                        className={clsx(
                          'w-10 h-5 rounded text-xs font-bold transition-all',
                          isPassengerSeat(seatNum)
                            ? 'bg-railway-blue text-white ring-2 ring-primary-400'
                            : isHighlighted(seatNum)
                            ? 'bg-primary-400 text-railway-blue ring-2 ring-primary-600'
                            : `${getBerthColor(berthType)} text-white opacity-50`,
                          onSeatClick && 'cursor-pointer hover:opacity-100'
                        )}
                      >
                        {seatNum}
                      </button>
                    )
                  })}
                </div>
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}

