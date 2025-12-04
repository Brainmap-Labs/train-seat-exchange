import { BerthType, ClassType } from '@/types'

/**
 * Get berth type for a seat number based on class
 */
export function getBerthType(seatNumber: number, classType: ClassType): BerthType {
  const posInBay = seatNumber % 8 || 8

  if (classType === '2A') {
    const posIn6 = seatNumber % 6 || 6
    const map: Record<number, BerthType> = { 1: 'LB', 2: 'UB', 3: 'LB', 4: 'UB', 5: 'SL', 6: 'SU' }
    return map[posIn6] || 'LB'
  }

  // SL and 3A
  const map: Record<number, BerthType> = {
    1: 'LB', 2: 'MB', 3: 'UB',
    4: 'LB', 5: 'MB', 6: 'UB',
    7: 'SL', 8: 'SU'
  }
  return map[posInBay] || 'LB'
}

/**
 * Get bay number for a seat
 */
export function getBayNumber(seatNumber: number, classType: ClassType): number {
  const baySize = classType === '2A' ? 6 : 8
  return Math.ceil(seatNumber / baySize)
}

/**
 * Check if two seats are in the same bay
 */
export function areSameBay(seat1: number, seat2: number, classType: ClassType): boolean {
  return getBayNumber(seat1, classType) === getBayNumber(seat2, classType)
}

/**
 * Get berth type display name
 */
export function getBerthDisplayName(type: BerthType): string {
  const names: Record<BerthType, string> = {
    LB: 'Lower Berth',
    MB: 'Middle Berth',
    UB: 'Upper Berth',
    SL: 'Side Lower',
    SU: 'Side Upper',
  }
  return names[type] || type
}

/**
 * Get berth preference score (higher = more preferred)
 */
export function getBerthPreferenceScore(type: BerthType): number {
  const scores: Record<BerthType, number> = {
    LB: 5,
    SL: 4,
    MB: 3,
    SU: 2,
    UB: 1,
  }
  return scores[type] || 0
}

