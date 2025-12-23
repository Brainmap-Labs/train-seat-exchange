import { Routes, Route } from 'react-router-dom'
import { Layout } from './components/layout/Layout'
import { HomePage } from './features/home/HomePage'
import { LoginPage } from './features/auth/LoginPage'
import { DashboardPage } from './features/dashboard/DashboardPage'
import { UploadTicketPage } from './features/tickets/UploadTicketPage'
import { TicketDetailsPage } from './features/tickets/TicketDetailsPage'
import { FindExchangePage } from './features/exchange/FindExchangePage'
import { ExchangeRequestsPage } from './features/exchange/ExchangeRequestsPage'
import { ChatPage } from './features/chat/ChatPage'
import { ProfilePage } from './features/profile/ProfilePage'
import { AdminPage } from './features/admin/AdminPage'

function App() {
  return (
    <Routes>
      <Route path="/" element={<Layout />}>
        <Route index element={<HomePage />} />
        <Route path="login" element={<LoginPage />} />
        <Route path="dashboard" element={<DashboardPage />} />
        <Route path="tickets">
          <Route path="upload" element={<UploadTicketPage />} />
          <Route path=":ticketId" element={<TicketDetailsPage />} />
        </Route>
        <Route path="exchange">
          <Route path="find/:ticketId" element={<FindExchangePage />} />
          <Route path="requests" element={<ExchangeRequestsPage />} />
        </Route>
        <Route path="chat/:exchangeId" element={<ChatPage />} />
        <Route path="profile" element={<ProfilePage />} />
        <Route path="admin" element={<AdminPage />} />
      </Route>
    </Routes>
  )
}

export default App

