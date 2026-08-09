import type { LucideIcon } from 'lucide-react';
import {
  LayoutDashboard,
  Users,
  GraduationCap,
  School,
  Calendar,
  DollarSign,
  BookOpen,
} from 'lucide-react';
import type { UserRole } from '../types';

export type Permission =
  | 'dashboard.admin'
  | 'dashboard.teacher'
  | 'dashboard.accountant'
  | 'dashboard.parent'
  | 'dashboard.student'
  | 'teachers.view'
  | 'teachers.manage'
  | 'students.view'
  | 'students.manage'
  | 'classes.view'
  | 'classes.manage'
  | 'timetable.view'
  | 'timetable.manage'
  | 'fees.view'
  | 'fees.manage';

export interface NavItem {
  to: string;
  label: string;
  icon: LucideIcon;
  permission: Permission;
}

export const ROLE_LABELS: Record<UserRole, string> = {
  super_admin: 'Super Admin',
  admin: 'Administrator',
  teacher: 'Teacher',
  accountant: 'Accountant',
  parent: 'Parent',
  student: 'Student',
};

export const ROLE_PORTAL_TITLE: Record<UserRole, string> = {
  super_admin: 'Admin Portal',
  admin: 'Admin Portal',
  teacher: 'Teacher Portal',
  accountant: 'Finance Portal',
  parent: 'Parent Portal',
  student: 'Student Portal',
};

/** Industry-standard RBAC matrix (Fedena / PowerSchool style) */
export const ROLE_PERMISSIONS: Record<UserRole, Permission[]> = {
  super_admin: [
    'dashboard.admin',
    'teachers.view', 'teachers.manage',
    'students.view', 'students.manage',
    'classes.view', 'classes.manage',
    'timetable.view', 'timetable.manage',
    'fees.view', 'fees.manage',
  ],
  admin: [
    'dashboard.admin',
    'teachers.view', 'teachers.manage',
    'students.view', 'students.manage',
    'classes.view', 'classes.manage',
    'timetable.view', 'timetable.manage',
    'fees.view', 'fees.manage',
  ],
  teacher: [
    'dashboard.teacher',
    'students.view',
    'timetable.view',
  ],
  accountant: [
    'dashboard.accountant',
    'fees.view', 'fees.manage',
  ],
  parent: [
    'dashboard.parent',
    'students.view',
    'timetable.view',
    'fees.view',
  ],
  student: [
    'dashboard.student',
    'timetable.view',
    'fees.view',
  ],
};

export const ALL_NAV_ITEMS: NavItem[] = [
  { to: '/dashboard', label: 'Dashboard', icon: LayoutDashboard, permission: 'dashboard.admin' },
  { to: '/teachers', label: 'Teachers', icon: Users, permission: 'teachers.view' },
  { to: '/students', label: 'Students', icon: GraduationCap, permission: 'students.view' },
  { to: '/classes', label: 'Classes', icon: School, permission: 'classes.view' },
  { to: '/timetable', label: 'Timetable', icon: Calendar, permission: 'timetable.view' },
  { to: '/fees', label: 'Fees', icon: DollarSign, permission: 'fees.view' },
];

/** Role-specific dashboard route uses same path but different widgets */
export const TEACHER_NAV: NavItem[] = [
  { to: '/dashboard', label: 'Dashboard', icon: LayoutDashboard, permission: 'dashboard.teacher' },
  { to: '/students', label: 'My Students', icon: GraduationCap, permission: 'students.view' },
  { to: '/timetable', label: 'My Timetable', icon: Calendar, permission: 'timetable.view' },
];

export const ACCOUNTANT_NAV: NavItem[] = [
  { to: '/dashboard', label: 'Dashboard', icon: LayoutDashboard, permission: 'dashboard.accountant' },
  { to: '/fees', label: 'Fee Management', icon: DollarSign, permission: 'fees.view' },
];

export const PARENT_NAV: NavItem[] = [
  { to: '/dashboard', label: 'Dashboard', icon: LayoutDashboard, permission: 'dashboard.parent' },
  { to: '/students', label: 'My Children', icon: GraduationCap, permission: 'students.view' },
  { to: '/timetable', label: 'Timetable', icon: Calendar, permission: 'timetable.view' },
  { to: '/fees', label: 'Fees', icon: DollarSign, permission: 'fees.view' },
];

export const STUDENT_NAV: NavItem[] = [
  { to: '/dashboard', label: 'Dashboard', icon: LayoutDashboard, permission: 'dashboard.student' },
  { to: '/timetable', label: 'My Timetable', icon: BookOpen, permission: 'timetable.view' },
  { to: '/fees', label: 'My Fees', icon: DollarSign, permission: 'fees.view' },
];

export const ADMIN_NAV: NavItem[] = ALL_NAV_ITEMS;

export function getNavItemsForRole(role: UserRole): NavItem[] {
  switch (role) {
    case 'super_admin':
    case 'admin':
      return ADMIN_NAV;
    case 'teacher':
      return TEACHER_NAV;
    case 'accountant':
      return ACCOUNTANT_NAV;
    case 'parent':
      return PARENT_NAV;
    case 'student':
      return STUDENT_NAV;
    default:
      return [];
  }
}

export function getDefaultRoute(_role: UserRole): string {
  return '/dashboard';
}

export function hasPermission(role: UserRole | undefined, permission: Permission): boolean {
  if (!role) return false;
  return ROLE_PERMISSIONS[role]?.includes(permission) ?? false;
}

export function canAccessRoute(role: UserRole | undefined, path: string): boolean {
  if (!role) return false;
  const navItems = getNavItemsForRole(role);
  if (navItems.some((item) => path === item.to || path.startsWith(`${item.to}/`))) {
    return true;
  }
  if (role === 'teacher' && /^\/teachers\/[^/]+$/.test(path)) {
    return true;
  }
  return false;
}
