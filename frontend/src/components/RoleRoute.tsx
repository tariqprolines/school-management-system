import { Navigate, Outlet, useLocation } from 'react-router-dom';
import { usePermissions } from '../hooks/usePermissions';
import { canAccessRoute } from '../config/roles';

export default function RoleRoute() {
  const { role, defaultRoute } = usePermissions();
  const location = useLocation();

  if (!role) {
    return <Navigate to="/login" replace />;
  }

  if (!canAccessRoute(role, location.pathname)) {
    return <Navigate to={defaultRoute} replace state={{ forbidden: true }} />;
  }

  return <Outlet />;
}
