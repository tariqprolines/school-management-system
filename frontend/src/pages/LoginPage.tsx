import { useEffect, useState, type FormEvent } from 'react';
import { useNavigate } from 'react-router-dom';
import { School } from 'lucide-react';
import { useAppDispatch, useAppSelector } from '../redux/hooks';
import { login } from '../redux/authSlice';
import { getDefaultRoute } from '../config/roles';
import type { UserRole } from '../types';
import '../components/Layout.css';

export default function LoginPage() {
  const [email, setEmail] = useState('admin@school.com');
  const [password, setPassword] = useState('admin123');
  const dispatch = useAppDispatch();
  const navigate = useNavigate();
  const { loading, error, user, token } = useAppSelector((state) => state.auth);

  useEffect(() => {
    if (token && user?.role) {
      navigate(getDefaultRoute(user.role as UserRole), { replace: true });
    }
  }, [token, user, navigate]);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    const result = await dispatch(login({ email, password }));
    if (login.fulfilled.match(result)) {
      const role = result.payload!.user.role as UserRole;
      navigate(getDefaultRoute(role), { replace: true });
    }
  };

  return (
    <div className="login-page">
      <div className="login-card">
        <div style={{ textAlign: 'center', marginBottom: 24 }}>
          <School size={48} color="#3b82f6" />
        </div>
        <h1>School Management System</h1>
        <p className="subtitle">Please, Sign in to your portal</p>
        {error && <div className="error">{error}</div>}
        <form onSubmit={handleSubmit}>
          <div className="form-group" style={{ marginBottom: 16 }}>
            <label>Email</label>
            <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} required />
          </div>
          <div className="form-group" style={{ marginBottom: 24 }}>
            <label>Password</label>
            <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} required />
          </div>
          <button type="submit" className="btn btn-primary" disabled={loading}>
            {loading ? 'Signing in...' : 'Sign In'}
          </button>
        </form>
        <p className="login-hint">
          Demo accounts (password <code>demo123</code> unless noted):
          <br />
          Super Admin: admin@school.com / admin123
          <br />
          Principal: principal@school.com · Teacher: teacher@school.com
          <br />
          Accountant: finance@school.com · Parent: parent@school.com · Student: student@school.com
        </p>
      </div>
    </div>
  );
}
