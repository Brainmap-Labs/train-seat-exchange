import { create } from 'zustand'
import { Ticket } from '@/types'

interface TicketState {
  tickets: Ticket[]
  isLoading: boolean
  error: string | null
  setTickets: (tickets: Ticket[]) => void
  addTicket: (ticket: Ticket) => void
  updateTicket: (id: string, updates: Partial<Ticket>) => void
  removeTicket: (id: string) => void
  setLoading: (loading: boolean) => void
  setError: (error: string | null) => void
}

export const useTicketStore = create<TicketState>((set) => ({
  tickets: [],
  isLoading: false,
  error: null,

  setTickets: (tickets) => set({ tickets }),
  
  addTicket: (ticket) =>
    set((state) => ({ tickets: [ticket, ...state.tickets] })),
  
  updateTicket: (id, updates) =>
    set((state) => ({
      tickets: state.tickets.map((t) =>
        t.id === id ? { ...t, ...updates } : t
      ),
    })),
  
  removeTicket: (id) =>
    set((state) => ({
      tickets: state.tickets.filter((t) => t.id !== id),
    })),
  
  setLoading: (isLoading) => set({ isLoading }),
  
  setError: (error) => set({ error }),
}))

