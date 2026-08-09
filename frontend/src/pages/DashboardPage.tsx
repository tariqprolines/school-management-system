import { useEffect, useState } from 'react';
import api, { type ApiResponse } from '../services/api';
import type { DashboardSummary, TimetableSlot } from '../types';
import { usePermissions } from '../hooks/usePermissions';

function AdminDashboard({ summary }: { summary: DashboardSummary }) {
  return (
    <div className="stats-grid">
      <div className="stat-card">
        <div className="stat-label">Total Students</div>
        <div className="stat-value">{summary.total_students}</div>
        <div className="stat-sub">{summary.active_enrollments} active enrollments</div>
      </div>
      <div className="stat-card">
        <div className="stat-label">Total Teachers</div>
        <div className="stat-value">{summary.total_teachers}</div>
      </div>
      <div className="stat-card">
        <div className="stat-label">Class Sections</div>
        <div className="stat-value">{summary.total_classes}</div>
        <div className="stat-sub">{summary.class_occupancy_rate}% occupancy</div>
      </div>
      <div className="stat-card">
        <div className="stat-label">Fee Collected</div>
        <div className="stat-value">${summary.total_fee_collected.toLocaleString()}</div>
        <div className="stat-sub">{summary.fee_collection_rate}% collection rate</div>
      </div>
      <div className="stat-card">
        <div className="stat-label">Pending Fees</div>
        <div className="stat-value" style={{ color: '#dc2626' }}>
          ${summary.total_fee_pending.toLocaleString()}
        </div>
      </div>
    </div>
  );
}

function FinanceDashboard({ summary }: { summary: DashboardSummary }) {
  return (
    <div className="stats-grid">
      <div className="stat-card">
        <div className="stat-label">Total Collected</div>
        <div className="stat-value">${summary.total_fee_collected.toLocaleString()}</div>
        <div className="stat-sub">{summary.fee_collection_rate}% collection rate</div>
      </div>
      <div className="stat-card">
        <div className="stat-label">Outstanding Fees</div>
        <div className="stat-value" style={{ color: '#dc2626' }}>
          ${summary.total_fee_pending.toLocaleString()}
        </div>
      </div>
      <div className="stat-card">
        <div className="stat-label">Active Students</div>
        <div className="stat-value">{summary.active_enrollments}</div>
        <div className="stat-sub">For billing reference</div>
      </div>
    </div>
  );
}

function TeacherDashboard({ slots }: { slots: TimetableSlot[] }) {
  const today = new Date().getDay();
  const dayIndex = today === 0 ? 6 : today - 1;
  const todaySlots = slots.filter((s) => s.day_of_week === dayIndex);

  return (
    <div>
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-label">Classes Today</div>
          <div className="stat-value">{todaySlots.length}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Weekly Periods</div>
          <div className="stat-value">{slots.length}</div>
        </div>
      </div>
      <div className="card">
        <div className="card-header"><h2>Today's Schedule</h2></div>
        {todaySlots.length === 0 ? (
          <div className="empty-state">No classes scheduled for today</div>
        ) : (
          <table>
            <thead><tr><th>Time</th><th>Subject</th><th>Class</th><th>Room</th></tr></thead>
            <tbody>
              {todaySlots.map((s) => (
                <tr key={s.id}>
                  <td>{s.start_time?.slice(0, 5)} - {s.end_time?.slice(0, 5)}</td>
                  <td>{s.subject_name}</td>
                  <td>{s.class_section_name}</td>
                  <td>{s.room || '-'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}

export default function DashboardPage() {
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [teacherSlots, setTeacherSlots] = useState<TimetableSlot[]>([]);
  const [portalStudents, setPortalStudents] = useState<import('../types').Student[]>([]);
  const [portalInvoices, setPortalInvoices] = useState<import('../types').FeeInvoice[]>([]);
  const [loading, setLoading] = useState(true);
  const { isAdmin, isAccountant, isTeacher, isParent, isStudent, portalTitle } = usePermissions();

  useEffect(() => {
    const load = async () => {
      try {
        if (isAdmin || isAccountant) {
          const res = await api.get<ApiResponse<DashboardSummary>>('/dashboard/summary');
          setSummary(res.data.data!);
        }
        if (isTeacher) {
          const meRes = await api.get<ApiResponse<{ id: string }>>('/teachers/me');
          const teacherId = meRes.data.data?.id;
          if (teacherId) {
            const slotsRes = await api.get<ApiResponse<TimetableSlot[]>>('/timetable/slots', {
              params: { teacher_id: teacherId },
            });
            setTeacherSlots(slotsRes.data.data || []);
          }
        }
        if (isParent || isStudent) {
          const [studentsRes, invoicesRes] = await Promise.all([
            api.get<ApiResponse<{ data: import('../types').Student[] }>>('/students'),
            api.get<ApiResponse<import('../types').FeeInvoice[]>>('/fees/invoices'),
          ]);
          setPortalStudents(studentsRes.data.data?.data || []);
          setPortalInvoices(invoicesRes.data.data || []);
        }
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    load();
  }, [isAdmin, isAccountant, isTeacher, isParent, isStudent]);

  if (loading) return <div className="page-header"><h1>Loading...</h1></div>;

  const subtitle = isAdmin
    ? 'School-wide overview and key metrics'
    : isAccountant
    ? 'Financial overview and fee collection status'
    : isTeacher
    ? 'Your teaching schedule and class overview'
    : isParent
    ? 'Your children\'s academic information'
    : isStudent
    ? 'Your academic overview'
    : 'Welcome';

  return (
    <div>
      <div className="page-header">
        <h1>{portalTitle}</h1>
        <p>{subtitle}</p>
      </div>

      {isAdmin && summary && <AdminDashboard summary={summary} />}
      {isAccountant && summary && <FinanceDashboard summary={summary} />}
      {isTeacher && <TeacherDashboard slots={teacherSlots} />}
      {isParent && (
        <div>
          <div className="stats-grid">
            <div className="stat-card">
              <div className="stat-label">Children</div>
              <div className="stat-value">{portalStudents.length}</div>
            </div>
            <div className="stat-card">
              <div className="stat-label">Pending Fees</div>
              <div className="stat-value">{portalInvoices.filter((i) => i.status !== 'paid').length}</div>
            </div>
          </div>
          <div className="card">
            <div className="card-header"><h2>My Children</h2></div>
            {portalStudents.length === 0 ? (
              <div className="empty-state">No children linked to your account.</div>
            ) : (
              <table>
                <thead><tr><th>Name</th><th>Class</th><th>Status</th></tr></thead>
                <tbody>
                  {portalStudents.map((s) => (
                    <tr key={s.id}>
                      <td>{s.first_name} {s.last_name}</td>
                      <td>{s.class_section_name || '-'}</td>
                      <td><span className={`badge badge-${s.status === 'active' ? 'success' : 'warning'}`}>{s.status}</span></td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        </div>
      )}
      {isStudent && (
        <div>
          <div className="stats-grid">
            <div className="stat-card">
              <div className="stat-label">Class</div>
              <div className="stat-value" style={{ fontSize: '1.25rem' }}>{portalStudents[0]?.class_section_name || 'Not enrolled'}</div>
            </div>
            <div className="stat-card">
              <div className="stat-label">Fee Invoices</div>
              <div className="stat-value">{portalInvoices.length}</div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
