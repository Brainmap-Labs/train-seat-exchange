// User Types
export interface User {
  id: string;
  phone: string;
  email?: string;
  name: string;
  avatarUrl?: string;
  rating: number;
  totalExchanges: number;
  createdAt: Date;
}

// Ticket Types
export interface Ticket {
  id: string;
  userId: string;
  pnr: string;
  trainNumber: string;
  trainName: string;
  travelDate: Date;
  boardingStation: Station;
  destinationStation: Station;
  classType: ClassType;
  quota: QuotaType;
  passengers: Passenger[];
  status: TicketStatus;
  rawImageUrl?: string;
  createdAt: Date;
  updatedAt: Date;
}

export interface Passenger {
  id: string;
  name: string;
  age: number;
  gender: 'M' | 'F' | 'O';
  coach: string;
  seatNumber: number;
  berthType: BerthType;
  bookingStatus: BookingStatus;
  currentStatus: BookingStatus;
}

export interface Station {
  code: string;
  name: string;
}

export type ClassType = 'SL' | '3A' | '2A' | '1A' | 'CC' | 'EC' | '2S';
export type QuotaType = 'GN' | 'TQ' | 'LD' | 'SS' | 'HP';
export type BerthType = 'LB' | 'MB' | 'UB' | 'SL' | 'SU';
export type BookingStatus = 'CNF' | 'RAC' | 'WL' | 'RLWL' | 'PQWL';
export type TicketStatus = 'active' | 'completed' | 'cancelled';

// Exchange Types
export interface ExchangeRequest {
  id: string;
  requesterId: string;
  requesterTicketId: string;
  targetUserId: string;
  targetTicketId: string;
  proposedExchange: ExchangeProposal;
  status: ExchangeStatus;
  message?: string;
  createdAt: Date;
  updatedAt: Date;
}

export interface ExchangeProposal {
  give: SeatInfo[];
  receive: SeatInfo[];
  improvementScore: number;
}

export interface SeatInfo {
  passengerId: string;
  passengerName: string;
  coach: string;
  seatNumber: number;
  berthType: BerthType;
}

export type ExchangeStatus = 'pending' | 'accepted' | 'declined' | 'completed' | 'expired';

// Chat Types
export interface Message {
  id: string;
  exchangeId: string;
  senderId: string;
  content: string;
  timestamp: Date;
  read: boolean;
}

// Coach Layout Types
export interface CoachLayout {
  classType: ClassType;
  totalBerths: number;
  baySize: number;
  bays: Bay[];
}

export interface Bay {
  bayNumber: number;
  berths: Berth[];
}

export interface Berth {
  number: number;
  type: BerthType;
  position: 'main' | 'side';
  occupied?: boolean;
  passengerId?: string;
  isFamily?: boolean;
}

// Exchange Match Types
export interface ExchangeMatch {
  userId: string;
  userName: string;
  userRating: number;
  ticketId: string;
  availableSeats: SeatInfo[];
  matchScore: number;
  benefitDescription: string;
}

