import React, { useState } from 'react';
import { Route, Routes, useLocation } from 'react-router-dom';
import Sidebar from './components/Sidebar.jsx';
import Header from './components/Header.jsx';
import ProtectedRoute from './components/ProtectedRoute.jsx';
import { AuthProvider } from './context/AuthContext.jsx';
import Dashboard from './pages/Dashboard.jsx';
import Alliances from './pages/Alliances.jsx';
import Members from './pages/Members.jsx';
import GiftCodes from './pages/GiftCodes.jsx';
import Events from './pages/Events.jsx';
import Ministers from './pages/Ministers.jsx';
import Settings from './pages/Settings.jsx';
import Login from './pages/Login.jsx';

const Shell = ({ children }) => {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const toggleSidebar = () => setSidebarOpen((open) => !open);
  const location = useLocation();

  return (
    <div className="flex min-h-screen bg-slate-950 text-slate-100">
      <Sidebar variant="desktop" />
      {sidebarOpen ? (
        <div className="fixed inset-0 z-40 bg-black/50 lg:hidden" onClick={() => setSidebarOpen(false)} />
      ) : null}
      <div
        className={`fixed inset-y-0 left-0 z-50 w-64 transform bg-slate-950 p-4 transition-transform lg:hidden ${
          sidebarOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        <Sidebar variant="mobile" />
      </div>
      <div className="flex min-h-screen flex-1 flex-col">
        <Header onToggleSidebar={toggleSidebar} />
        <main className="flex-1 bg-slate-900/40 p-6">
          <div className="mx-auto max-w-6xl space-y-8">
            <div className="flex flex-col gap-1">
              <p className="text-sm uppercase tracking-wide text-slate-500">{location.pathname}</p>
              <h1 className="text-3xl font-semibold text-white">
                {(() => {
                  switch (location.pathname) {
                    case '/alliances':
                      return 'Alliance Management';
                    case '/members':
                      return 'Members';
                    case '/gift-codes':
                      return 'Gift Codes';
                    case '/events':
                      return 'Events & Attendance';
                    case '/ministers':
                      return 'Minister Schedule';
                    case '/settings':
                      return 'Settings & Logs';
                    default:
                      return 'Command Dashboard';
                  }
                })()}
              </h1>
            </div>
            {children}
          </div>
        </main>
      </div>
    </div>
  );
};

const AppRoutes = () => (
  <Routes>
    <Route path="/login" element={<Login />} />
    <Route
      path="/*"
      element={
        <ProtectedRoute>
          <Shell>
            <Routes>
              <Route index element={<Dashboard />} />
              <Route path="alliances" element={<Alliances />} />
              <Route path="members" element={<Members />} />
              <Route path="gift-codes" element={<GiftCodes />} />
              <Route path="events" element={<Events />} />
              <Route path="ministers" element={<Ministers />} />
              <Route path="settings" element={<Settings />} />
            </Routes>
          </Shell>
        </ProtectedRoute>
      }
    />
  </Routes>
);

const App = () => (
  <AuthProvider>
    <AppRoutes />
  </AuthProvider>
);

export default App;
