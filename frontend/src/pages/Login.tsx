import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';
import { useAuth } from '../context/AuthContext';

export default function Login() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const { login } = useAuth();

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      const res = await api.post('/auth/login', { email, password });
      const token = res.data.access_token;
      const meRes = await api.get('/auth/me', { headers: { Authorization: `Bearer ${token}` } });
      login(token, meRes.data);
      navigate('/dashboard');
    } catch (err: any) {
      const msg = err.response?.data?.error?.message || err.response?.data?.detail || 'Login failed. Check your credentials.';
      setError(typeof msg === 'string' ? msg : JSON.stringify(msg));
    } finally {
      setLoading(false);
    }
  };

  const useSeedLogin = (emailStr: string, pwd: string) => {
    setEmail(emailStr);
    setPassword(pwd);
  };

  return (
    <div className="min-h-screen bg-bg-primary flex items-center justify-center overflow-hidden relative font-sans">
      <div className="absolute top-[-20%] left-[-10%] w-[60%] h-[60%] rounded-full bg-accent-purple/20 blur-[150px]" />
      <div className="absolute bottom-[-20%] right-[-10%] w-[60%] h-[60%] rounded-full bg-accent-blue/20 blur-[150px]" />

      <div className="relative z-10 w-full max-w-md p-10 glass-card">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold tracking-tight mb-2">Vaultix<span className="text-accent-blue">.</span></h1>
          <p className="text-text-secondary text-sm">Secure Institutional Ledger</p>
        </div>

        {error && (
          <div className="mb-6 p-3 rounded-lg bg-accent-red/10 border border-accent-red/20 text-accent-red text-sm flex items-center gap-2">
            <div className="w-2 h-2 rounded-full bg-accent-red shrink-0" />
            {error}
          </div>
        )}

        <form onSubmit={handleLogin} className="space-y-5">
          <div>
            <label className="block text-xs uppercase tracking-wider font-semibold mb-2 text-text-secondary">Email Address</label>
            <input type="email" className="input-field" value={email} onChange={(e) => setEmail(e.target.value)} placeholder="treasurer@vaultix.dev" required />
          </div>
          <div>
            <label className="block text-xs uppercase tracking-wider font-semibold mb-2 text-text-secondary">Password</label>
            <input type="password" className="input-field" value={password} onChange={(e) => setPassword(e.target.value)} placeholder="••••••••" required />
          </div>
          <button type="submit" disabled={loading} className="w-full btn-primary h-12 text-md mt-6">
            {loading ? 'Authenticating…' : 'Sign In'}
          </button>
        </form>

        <div className="mt-8 pt-6 border-t border-border-layer">
          <div className="text-xs text-text-secondary mb-3">Quick Access</div>
          <div className="flex gap-2 flex-wrap">
            <button onClick={() => useSeedLogin('faculty@vaultix.dev', 'faculty123')} className="text-xs px-2 py-1 bg-accent-purple/15 text-accent-purple border border-accent-purple/20 hover:bg-accent-purple/25 rounded transition-colors">Faculty (Admin)</button>
            <button onClick={() => useSeedLogin('treasurer@vaultix.dev', 'treasurer123')} className="text-xs px-2 py-1 bg-accent-purple/15 text-accent-purple border border-accent-purple/20 hover:bg-accent-purple/25 rounded transition-colors">Treasurer (Admin)</button>
            <button onClick={() => useSeedLogin('secretary@vaultix.dev', 'secretary123')} className="text-xs px-2 py-1 bg-accent-blue/15 text-accent-blue border border-accent-blue/20 hover:bg-accent-blue/25 rounded transition-colors">Secretary (Analyst)</button>
            <button onClick={() => useSeedLogin('hackathon@vaultix.dev', 'hackathon123')} className="text-xs px-2 py-1 bg-accent-blue/15 text-accent-blue border border-accent-blue/20 hover:bg-accent-blue/25 rounded transition-colors">Hackathon Lead</button>
            <button onClick={() => useSeedLogin('karan@vaultix.dev', 'karan123')} className="text-xs px-2 py-1 bg-border-layer text-text-secondary hover:bg-bg-card-hover rounded transition-colors">Member (Viewer)</button>
          </div>
        </div>
      </div>
    </div>
  );
}
