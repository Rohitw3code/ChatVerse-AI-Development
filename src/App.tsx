import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { useAuthStore } from './stores';
import LandingPage from './pages/landing/LandingPageNew2';
import GetStartedPage from './pages/get-started/GetStartedPage';
import PlatformSelectionPage from './pages/platform-selection/PlatformSelectionPage';
import InstagramDashboard from './pages/instagram-dashboard/InstagramDashboard';
import GmailDashboard from './pages/gmail-dashboard/GmailDashboard';
import PrivacyPage from './pages/landing/PrivacyPage';
import TermsAndConditionsPage from './pages/landing/TermsAndConditionsPage';
import PricingPage from './pages/pricing/PricingPage';
import NotificationSystem from './components/common/NotificationSystem';
import AIAssistantChat from './pages/chat/chat';


const ProtectedRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { isLoading, isAuthenticated } = useAuthStore();

  if (isLoading) {
    return (
      <div className="min-h-screen text-white relative overflow-hidden flex items-center justify-center" style={{backgroundColor: '#0a0a0a'}}>
        <div className="absolute inset-0" style={{
          backgroundColor: '#0a0a0a',
          backgroundImage: `
            radial-gradient(circle at 1px 1px, rgba(255,255,255,0.15) 1px, transparent 0),
            radial-gradient(circle at 3px 3px, rgba(255,255,255,0.08) 1px, transparent 0),
            radial-gradient(circle at 5px 5px, rgba(255,255,255,0.04) 1px, transparent 0)
          `,
          backgroundSize: '20px 20px, 40px 40px, 60px 60px'
        }}></div>

        <div className="relative z-10">
          <div className="w-10 h-10 border-4 border-white/20 border-t-white rounded-full animate-spin"></div>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/" replace />;
  }

  return <>{children}</>;
};

function App() {
  const { initialize, isLoading } = useAuthStore();

  React.useEffect(() => {
    initialize();
  }, [initialize]);

  if (isLoading) {
    return (
      <div className="min-h-screen text-white relative overflow-hidden flex items-center justify-center" style={{backgroundColor: '#0a0a0a'}}>
        <div className="absolute inset-0" style={{
          backgroundColor: '#0a0a0a',
          backgroundImage: `
            radial-gradient(circle at 1px 1px, rgba(255,255,255,0.15) 1px, transparent 0),
            radial-gradient(circle at 3px 3px, rgba(255,255,255,0.08) 1px, transparent 0),
            radial-gradient(circle at 5px 5px, rgba(255,255,255,0.04) 1px, transparent 0)
          `,
          backgroundSize: '20px 20px, 40px 40px, 60px 60px'
        }}></div>
        <div className="relative z-10">
          <div className="w-10 h-10 border-4 border-white/20 border-t-white rounded-full animate-spin"></div>
        </div>
      </div>
    );
  }

  return (
    <Router>
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/get-started" element={<GetStartedPage />} />
        <Route path="/pricing" element={
          <ProtectedRoute>
            <PricingPage />
          </ProtectedRoute>
        } />
        <Route path="/privacy" element={<PrivacyPage />} />
        <Route path="/terms" element={<TermsAndConditionsPage />} />
        
        <Route path="/platforms" element={
          <ProtectedRoute>
            <PlatformSelectionPage />
          </ProtectedRoute>
        } />
        <Route path="/instagram/*" element={
          <ProtectedRoute>
            <InstagramDashboard />
          </ProtectedRoute>
        } />
        <Route path="/gmail" element={
          <ProtectedRoute>
            <GmailDashboard />
          </ProtectedRoute>
        } />
        {/** Removed Google Sheets Dashboard route; Sheets flows handled via chat + connect */}
        <Route path="/chat/:chatId" element={
          <ProtectedRoute>
            <AIAssistantChat />
          </ProtectedRoute>
        } />
        
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
      <NotificationSystem />
    </Router>
  );
}

export default App;