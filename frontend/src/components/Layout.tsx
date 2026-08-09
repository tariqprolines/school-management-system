import { NavLink, Outlet, useNavigate } from 'react-router-dom';
import { School, LogOut } from 'lucide-react';
import { useAppDispatch } from '../redux/hooks';
import { logout } from '../redux/authSlice';
import { usePermissions } from '../hooks/usePermissions';
import './Layout.css';

export default function Layout() {
  const dispatch = useAppDispatch();
  const navigate = useNavigate();
  const { user, navItems, portalTitle, roleLabel } = usePermissions();

  const handleLogout = () => {
    dispatch(logout());
    navigate('/login');
  };

  return (
    <div className="layout">
      <aside className={`sidebar sidebar-${user?.role || 'admin'}`}>
        <div className="sidebar-header">
          <School size={28} />
          <div className="sidebar-brand">
            <span>School SMS</span>
            <small>{portalTitle}</small>
          </div>
        </div>
        <nav className="sidebar-nav">
          {navItems.map(({ to, label, icon: Icon }) => (
            <NavLink key={to} to={to} className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
              <Icon size={18} />
              {label}
            </NavLink>
          ))}
        </nav>
        <div className="sidebar-footer">
          <div className="user-info">
            <span className="user-name">{user?.first_name} {user?.last_name}</span>
            <span className="user-role">{roleLabel}</span>
          </div>
          <button onClick={handleLogout} className="logout-btn">
            <LogOut size={16} />
            Logout
          </button>
        </div>
      </aside>
      <main className="main-content">
        <Outlet />
      </main>
    </div>
  );
}
