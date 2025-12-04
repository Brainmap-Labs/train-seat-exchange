import { useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { ArrowLeft, Send } from 'lucide-react'
import { Button } from '@/components/ui/Button'

export function ChatPage() {
  const { exchangeId } = useParams()
  const [message, setMessage] = useState('')
  const [messages, setMessages] = useState([
    { id: '1', senderId: '2', content: 'Hi! I saw your exchange request.', timestamp: new Date() },
    { id: '2', senderId: '1', content: 'Yes! Would you be willing to exchange?', timestamp: new Date() },
  ])

  const handleSend = () => {
    if (!message.trim()) return
    setMessages([...messages, { id: Date.now().toString(), senderId: '1', content: message, timestamp: new Date() }])
    setMessage('')
  }

  return (
    <div className="max-w-2xl mx-auto h-[calc(100vh-4rem)] flex flex-col">
      {/* Header */}
      <div className="bg-white border-b px-4 py-3 flex items-center gap-4">
        <Link to="/exchange/requests">
          <ArrowLeft className="w-5 h-5 text-slate-600" />
        </Link>
        <div>
          <h2 className="font-semibold">Amit Sharma</h2>
          <p className="text-sm text-slate-500">Exchange Request #{exchangeId}</p>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-slate-50">
        {messages.map((msg) => (
          <div key={msg.id} className={`flex ${msg.senderId === '1' ? 'justify-end' : 'justify-start'}`}>
            <div className={`max-w-[70%] rounded-2xl px-4 py-2 ${
              msg.senderId === '1' 
                ? 'bg-railway-blue text-white rounded-br-md' 
                : 'bg-white text-slate-900 rounded-bl-md shadow-sm'
            }`}>
              <p>{msg.content}</p>
              <p className={`text-xs mt-1 ${msg.senderId === '1' ? 'text-blue-200' : 'text-slate-400'}`}>
                {msg.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
              </p>
            </div>
          </div>
        ))}
      </div>

      {/* Input */}
      <div className="bg-white border-t p-4">
        <div className="flex gap-2">
          <input
            type="text"
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSend()}
            placeholder="Type a message..."
            className="flex-1 px-4 py-3 rounded-xl border border-slate-200 focus:border-primary-500 outline-none"
          />
          <Button onClick={handleSend}>
            <Send className="w-5 h-5" />
          </Button>
        </div>
      </div>
    </div>
  )
}

