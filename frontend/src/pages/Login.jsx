import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../api/client';

function Login() {
  const navigate = useNavigate();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [isRegister, setIsRegister] = useState(false);

  const handleLogin = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const response = await api.login(username.trim(), password);
      const user = response.user;
      
      // Update App.jsx user state by reloading the page
      // Redirect based on role
      if (user.role === 'admin') {
        window.location.href = '/admin';
      } else {
        window.location.href = '/';
      }
    } catch (err) {
      setError(err.message || 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  const handleRegister = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      // Always register as student - admin accounts are created separately
      await api.register(username.trim(), password, 'student');
      // After registration, automatically login
      const response = await api.login(username.trim(), password);
      const user = response.user;
      
      // Students always go to home page
      window.location.href = '/';
    } catch (err) {
      setError(err.message || 'Registration failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container">
      <div className="card" style={{ maxWidth: '400px', margin: '2rem auto' }}>
        <h2>{isRegister ? 'Register' : 'Login'}</h2>
        <p style={{ marginBottom: '20px', color: '#666' }}>
          {isRegister 
            ? 'Create a new account to start taking quizzes'
            : 'Enter your username and password to continue'}
        </p>

        {error && <div className="error">{error}</div>}

        <form onSubmit={isRegister ? handleRegister : handleLogin}>
          <div className="form-group">
            <label htmlFor="username">Username</label>
            <input
              id="username"
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="Enter your username"
              required
              autoFocus
            />
          </div>

          <div className="form-group">
            <label htmlFor="password">Password</label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Enter your password"
              required
            />
          </div>


          <button
            type="submit"
            className="btn"
            disabled={loading}
            style={{ width: '100%', marginTop: '1rem' }}
          >
            {loading ? 'Loading...' : (isRegister ? 'Register' : 'Login')}
          </button>
        </form>

        <div style={{ marginTop: '1rem', textAlign: 'center' }}>
          <button
            type="button"
            className="btn btn-secondary"
            onClick={() => {
              setIsRegister(!isRegister);
              setError(null);
            }}
            style={{ background: 'none', border: 'none', color: '#007bff', cursor: 'pointer', textDecoration: 'underline' }}
          >
            {isRegister 
              ? 'Already have an account? Login'
              : "Don't have an account? Register"}
          </button>
        </div>
      </div>
    </div>
  );
}

export default Login;
