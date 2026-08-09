import { Navigate, Outlet } from 'react-router-dom';
import { useAppSelector } from '../redux/hooks';

export default function ProtectedRoute() {
  const { token } = useAppSelector((state) => state.auth);
  if (!token) {
    return <Navigate to="/login" replace />;
  }
  return <Outlet />;
}
