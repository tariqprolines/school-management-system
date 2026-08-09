export type UserRole = 'super_admin' | 'admin' | 'teacher' | 'accountant' | 'parent' | 'student';

export interface User {
  id: string;
  email: string;
  first_name: string;
  last_name: string;
  phone?: string;
  role: UserRole;
  is_active: boolean;
}

export interface Teacher {
  id: string;
  employee_id: string;
  department: string;
  qualification?: string;
  joining_date: string;
  address?: string;
  first_name?: string;
  last_name?: string;
  email?: string;
  phone?: string;
}

export interface Guardian {
  id: string;
  name: string;
  relationship_type: string;
  phone: string;
  email?: string;
  occupation?: string;
  is_primary: boolean;
}

export interface Student {
  id: string;
  admission_no: string;
  first_name?: string;
  last_name?: string;
  email?: string;
  date_of_birth: string;
  gender: string;
  blood_group?: string;
  address?: string;
  status: string;
  admission_date: string;
  guardians: Guardian[];
  class_section_name?: string;
}

export interface AcademicYear {
  id: string;
  name: string;
  start_date: string;
  end_date: string;
  is_current: boolean;
}

export interface Grade {
  id: string;
  name: string;
  level: number;
  description?: string;
}

export interface Subject {
  id: string;
  name: string;
  code: string;
  subject_type: string;
  description?: string;
}

export interface ClassSection {
  id: string;
  name: string;
  capacity: number;
  academic_year_id: string;
  grade_id: string;
  class_teacher_id?: string;
  grade_name?: string;
  academic_year_name?: string;
}

export interface TimetableSlot {
  id: string;
  class_section_id: string;
  subject_id: string;
  teacher_id: string;
  day_of_week: number;
  start_time: string;
  end_time: string;
  room?: string;
  subject_name?: string;
  teacher_name?: string;
  class_section_name?: string;
}

export interface FeeCategory {
  id: string;
  name: string;
  description?: string;
}

export interface FeeStructure {
  id: string;
  category_id: string;
  class_section_id: string;
  amount: number;
  due_date: string;
  academic_year_id: string;
  category_name?: string;
  class_section_name?: string;
}

export interface FeeInvoice {
  id: string;
  student_id: string;
  fee_structure_id: string;
  invoice_no: string;
  amount: number;
  paid_amount: number;
  status: string;
  due_date: string;
  student_name?: string;
  category_name?: string;
  outstanding?: number;
}

export interface DashboardSummary {
  total_students: number;
  total_teachers: number;
  total_classes: number;
  active_enrollments: number;
  total_fee_collected: number;
  total_fee_pending: number;
  fee_collection_rate: number;
  class_occupancy_rate: number;
}

export const DAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];
