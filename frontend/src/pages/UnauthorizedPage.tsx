import { Link } from 'react-router-dom';
import { ShieldX } from 'lucide-react';
import { usePermissions } from '../hooks/usePermissions';
import './../components/Layout.css';

export default function UnauthorizedPage() {
  const { defaultRoute } = usePermissions();

  return (
    <div className="login-page">
      <div className="login-card" style={{ textAlign: 'center' }}>
        <ShieldX size={48} color="#dc2626" style={{ margin: '0 auto 16px' }} />
        <h1>Access Denied</h1>
        <p className="subtitle">You do not have permission to view this page.</p>
        <Link to={defaultRoute} className="btn btn-primary" style={{ display: 'inline-block', marginTop: 16, textDecoration: 'none' }}>
          Go to My Dashboard
        </Link>
      </div>
    </div>
  );
}
