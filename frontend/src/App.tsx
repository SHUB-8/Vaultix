import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import { ToastProvider } from './context/ToastContext';
import RoleGuard from './components/RoleGuard';
import Layout from './components/Layout';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import Records from './pages/Records';
import RecordForm from './pages/RecordForm';
import Events from './pages/Events';
import EventForm from './pages/EventForm';
import Users from './pages/Users';
import Audit from './pages/Audit';
import Profile from './pages/Profile';
import NotFound from './pages/NotFound';

const ProtectedRoute = ({ children }: { children: React.ReactNode }) => {
  const { user, loading } = useAuth();
  if (loading) {
    return (
      <div className="h-screen w-screen flex items-center justify-center bg-bg-primary text-text-primary">
        <div className="text-center">
          <div className="w-8 h-8 border-2 border-accent-blue border-t-transparent rounded-full animate-spin mx-auto mb-4" />
          <p className="text-text-secondary text-sm">Loading Vaultix…</p>
        </div>
      </div>
    );
  }
  if (!user) return <Navigate to="/login" replace />;
  return <>{children}</>;
};

function App() {
  return (
    <AuthProvider>
      <ToastProvider>
        <Router>
          <Routes>
            {/* Public */}
            <Route path="/login" element={<Login />} />

            {/* Protected */}
            <Route element={<ProtectedRoute><Layout /></ProtectedRoute>}>
              {/* All roles */}
              <Route path="/dashboard" element={<Dashboard />} />
              <Route path="/profile" element={<Profile />} />

              {/* Admin + Analyst */}
              <Route path="/records" element={<RoleGuard allowedRoles={['admin', 'analyst']}><Records /></RoleGuard>} />
              <Route path="/events" element={<RoleGuard allowedRoles={['admin', 'analyst']}><Events /></RoleGuard>} />
              <Route path="/audit" element={<RoleGuard allowedRoles={['admin', 'analyst']}><Audit /></RoleGuard>} />

              {/* Admin only */}
              <Route path="/records/new" element={<RoleGuard allowedRoles={['admin']}><RecordForm /></RoleGuard>} />
              <Route path="/records/:id/edit" element={<RoleGuard allowedRoles={['admin']}><RecordForm /></RoleGuard>} />
              <Route path="/events/new" element={<RoleGuard allowedRoles={['admin']}><EventForm /></RoleGuard>} />
              <Route path="/events/:id/edit" element={<RoleGuard allowedRoles={['admin']}><EventForm /></RoleGuard>} />
              <Route path="/users" element={<RoleGuard allowedRoles={['admin']}><Users /></RoleGuard>} />

              <Route path="/" element={<Navigate to="/dashboard" replace />} />
            </Route>

            {/* 404 */}
            <Route path="*" element={<NotFound />} />
          </Routes>
        </Router>
      </ToastProvider>
    </AuthProvider>
  );
}

export default App;
