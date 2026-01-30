import { Routes, Route } from 'react-router-dom'
import { Layout } from './components/layout/Layout'
import { HomePage } from './features/home/HomePage'
import { LoginPage } from './features/auth/LoginPage'
import { SignUpPage } from './features/auth/SignUpPage'
import { DashboardPage } from './features/dashboard/DashboardPage'
import { AboutPage } from './features/info/AboutPage'
import { HowItWorksPage } from './features/info/HowItWorksPage'
import { FAQPage } from './features/info/FAQPage'
import { ContactPage } from './features/info/ContactPage'
import { PrivacyPolicyPage } from './features/info/PrivacyPolicyPage'
import { TermsOfServicePage } from './features/info/TermsOfServicePage'
import { RefundPolicyPage } from './features/info/RefundPolicyPage'
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
        <Route path="signup" element={<SignUpPage />} />
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
        <Route path="about" element={<AboutPage />} />
        <Route path="how-it-works" element={<HowItWorksPage />} />
        <Route path="faq" element={<FAQPage />} />
        <Route path="contact" element={<ContactPage />} />
        <Route path="privacy" element={<PrivacyPolicyPage />} />
        <Route path="terms" element={<TermsOfServicePage />} />
        <Route path="refunds" element={<RefundPolicyPage />} />
        <Route path="admin" element={<AdminPage />} />
      </Route>
    </Routes>
  )
}

export default App

