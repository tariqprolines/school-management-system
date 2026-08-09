import { useAppSelector } from '../redux/hooks';
import {
  hasPermission,
  type Permission,
  getNavItemsForRole,
  getDefaultRoute,
  ROLE_LABELS,
  ROLE_PORTAL_TITLE,
} from '../config/roles';
import type { UserRole } from '../types';

export function usePermissions() {
  const { user } = useAppSelector((state) => state.auth);
  const role = user?.role as UserRole | undefined;

  return {
    role,
    user,
    roleLabel: role ? ROLE_LABELS[role] : '',
    portalTitle: role ? ROLE_PORTAL_TITLE[role] : 'School SMS',
    navItems: role ? getNavItemsForRole(role) : [],
    defaultRoute: role ? getDefaultRoute(role) : '/login',
    can: (permission: Permission) => hasPermission(role, permission),
    isAdmin: role === 'super_admin' || role === 'admin',
    isTeacher: role === 'teacher',
    isAccountant: role === 'accountant',
    isParent: role === 'parent',
    isStudent: role === 'student',
  };
}
