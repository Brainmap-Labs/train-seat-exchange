import { useEffect } from 'react'
import { useTicketStore } from '@/store/ticketStore'
import { ticketApi } from '@/services/api'

export function useTickets() {
  const { tickets, isLoading, error, setTickets, setLoading, setError } = useTicketStore()

  const fetchTickets = async () => {
    setLoading(true)
    setError(null)
    try {
      const response = await ticketApi.getAll()
      setTickets(response.data)
    } catch (err) {
      setError('Failed to fetch tickets')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchTickets()
  }, [])

  return {
    tickets,
    isLoading,
    error,
    refetch: fetchTickets,
  }
}

