import { useState, useEffect, useCallback } from 'react'
import { useParams, Link } from 'react-router-dom'
import { ArrowLeft, Send, Loader2 } from 'lucide-react'
import { Button } from '@/components/ui/Button'
import { exchangeApi, chatApi } from '@/services/api'
import { useAuthStore } from '@/store/authStore'

interface ChatMessage {
  id: string
  senderId: string
  content: string
  createdAt: Date
}

export function ChatPage() {
  const { exchangeId } = useParams()
  const { user } = useAuthStore()
  const [message, setMessage] = useState('')
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [otherUserName, setOtherUserName] = useState('Exchange partner')
  const [trainLabel, setTrainLabel] = useState('')
  const [canSend, setCanSend] = useState(true)
  const [isLoading, setIsLoading] = useState(true)
  const [isSending, setIsSending] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const loadChat = useCallback(async () => {
    if (!exchangeId) return

    try {
      const [exchangeRes, chatRes] = await Promise.all([
        exchangeApi.getRequest(exchangeId),
        chatApi.getMessages(exchangeId),
      ])

      setOtherUserName(exchangeRes.data.other_user?.name || 'Exchange partner')
      setTrainLabel(
        `${exchangeRes.data.train_number} · ${new Date(exchangeRes.data.travel_date).toLocaleDateString('en-IN')} · ${exchangeRes.data.status}`
      )
      setCanSend(chatRes.data.can_send ?? exchangeRes.data.can_chat)

      setMessages(
        (chatRes.data.messages || []).map((m: any) => ({
          id: m.id,
          senderId: m.sender_id,
          content: m.content,
          createdAt: new Date(m.created_at),
        }))
      )
      setError(null)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load chat')
    } finally {
      setIsLoading(false)
    }
  }, [exchangeId])

  useEffect(() => {
    loadChat()
    const interval = setInterval(loadChat, 5000)
    return () => clearInterval(interval)
  }, [loadChat])

  const handleSend = async () => {
    if (!message.trim() || !exchangeId || !canSend) return

    setIsSending(true)
    try {
      const response = await chatApi.sendMessage(exchangeId, message.trim())
      const sent = response.data
      setMessages((prev) => [
        ...prev,
        {
          id: sent.id,
          senderId: sent.sender_id,
          content: sent.content,
          createdAt: new Date(sent.created_at),
        },
      ])
      setMessage('')
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to send message')
    } finally {
      setIsSending(false)
    }
  }

  const isOwnMessage = (senderId: string) => user?.id === senderId

  if (isLoading) {
    return (
      <div className="max-w-2xl mx-auto px-4 py-12 text-center text-slate-600">
        <Loader2 className="w-8 h-8 animate-spin mx-auto mb-3" />
        Loading chat...
      </div>
    )
  }

  return (
    <div className="max-w-2xl mx-auto w-full min-h-[calc(100dvh-4rem)] flex flex-col px-4 sm:px-0">
      <div className="bg-white border-b px-4 py-3 flex items-center gap-3 sm:gap-4 shrink-0">
        <Link to="/exchange/requests">
          <ArrowLeft className="w-5 h-5 text-slate-600" />
        </Link>
        <div className="min-w-0">
          <h2 className="font-semibold truncate">{otherUserName}</h2>
          <p className="text-sm text-slate-500 truncate">{trainLabel}</p>
        </div>
      </div>

      {error && (
        <div className="bg-red-50 text-red-700 text-sm px-4 py-2 border-b border-red-100">{error}</div>
      )}

      <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-slate-50">
        {messages.length === 0 ? (
          <p className="text-center text-slate-500 text-sm py-8">
            No messages yet. Coordinate your seat exchange here.
          </p>
        ) : (
          messages.map((msg) => (
            <div
              key={msg.id}
              className={`flex ${isOwnMessage(msg.senderId) ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-[85%] sm:max-w-[70%] rounded-2xl px-4 py-2 ${
                  isOwnMessage(msg.senderId)
                    ? 'bg-railway-blue text-white rounded-br-md'
                    : 'bg-white text-slate-900 rounded-bl-md shadow-sm'
                }`}
              >
                <p className="break-words">{msg.content}</p>
                <p
                  className={`text-xs mt-1 ${
                    isOwnMessage(msg.senderId) ? 'text-blue-200' : 'text-slate-400'
                  }`}
                >
                  {msg.createdAt.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                </p>
              </div>
            </div>
          ))
        )}
      </div>

      <div className="bg-white border-t p-3 sm:p-4 shrink-0 pb-[max(0.75rem,env(safe-area-inset-bottom))]">
        {!canSend && (
          <p className="text-xs text-slate-500 mb-2 text-center">
            This exchange is closed — you can read past messages only.
          </p>
        )}
        <div className="flex gap-2">
          <input
            type="text"
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && !isSending && handleSend()}
            placeholder={canSend ? 'Type a message...' : 'Chat closed'}
            disabled={!canSend || isSending}
            className="flex-1 px-4 py-3 rounded-xl border border-slate-200 focus:border-primary-500 outline-none disabled:bg-slate-50"
          />
          <Button onClick={handleSend} disabled={!canSend || isSending || !message.trim()}>
            <Send className="w-5 h-5" />
          </Button>
        </div>
      </div>
    </div>
  )
}
