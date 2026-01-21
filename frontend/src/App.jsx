import { BrowserRouter as Router, Routes, Route, Navigate, useNavigate } from 'react-router-dom';
import { useState, useEffect } from 'react';
import StartQuiz from './pages/StartQuiz';
import TakeQuiz from './pages/TakeQuiz';
import QuizResults from './pages/QuizResults';
import StudentHistory from './pages/StudentHistory';
import Login from './pages/Login';
import AdminDashboard from './pages/AdminDashboard';
import api from './api/client';

function ProtectedRoute({ children, requireAdmin = false }) {
  const [checking, setChecking] = useState(true);
  const [authorized, setAuthorized] = useState(false);

  useEffect(() => {
    const checkAuth = async () => {
      const user = api.getCurrentUserFromStorage();
      if (!user) {
        setAuthorized(false);
        setChecking(false);
        return;
      }

      if (requireAdmin && user.role !== 'admin') {
        setAuthorized(false);
        setChecking(false);
        return;
      }

      // Verify token is still valid
      try {
        await api.getCurrentUser();
        setAuthorized(true);
      } catch (e) {
        api.logout();
        setAuthorized(false);
      }
      setChecking(false);
    };

    checkAuth();
  }, [requireAdmin]);

  if (checking) {
    return (
      <div className="container">
        <div className="loading">Loading...</div>
      </div>
    );
  }

  return authorized ? children : <Navigate to="/login" replace />;
}

function App() {
  const [user, setUser] = useState(null);

  useEffect(() => {
    const updateUser = () => {
      const currentUser = api.getCurrentUserFromStorage();
      setUser(currentUser);
    };
    
    // Check user on mount
    updateUser();
    
    // Listen for storage changes (when user logs in/out)
    const handleStorageChange = (e) => {
      if (e.key === 'user' || e.key === 'session_token') {
        updateUser();
      }
    };
    
    window.addEventListener('storage', handleStorageChange);
    
    // Also check periodically (in case storage event doesn't fire in same window)
    const interval = setInterval(updateUser, 500);
    
    return () => {
      window.removeEventListener('storage', handleStorageChange);
      clearInterval(interval);
    };
  }, []);

  const handleLogout = async () => {
    await api.logout();
    setUser(null);
    // Force redirect to login page
    window.location.href = '/login';
  };

  return (
    <Router future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
      <div className="app">
        <div className="header">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div>
              <h1>GradeMaster</h1>
              <p>Adaptive Remediation Quiz System</p>
            </div>
            {user && (
              <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                <span>Welcome, {user.username} ({user.role})</span>
                <button className="btn btn-secondary" onClick={handleLogout} style={{ padding: '0.5rem 1rem' }}>
                  Logout
                </button>
              </div>
            )}
          </div>
        </div>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route
            path="/admin"
            element={
              <ProtectedRoute requireAdmin={true}>
                <AdminDashboard />
              </ProtectedRoute>
            }
          />
          <Route
            path="/"
            element={
              <ProtectedRoute>
                <StartQuiz />
              </ProtectedRoute>
            }
          />
          <Route path="/quiz/:quizId" element={<TakeQuiz />} />
          <Route path="/results/:attemptId" element={<QuizResults />} />
          <Route path="/history/:studentId/:gradeLevel?" element={<StudentHistory />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;

