import { useEffect, useState, type FormEvent } from 'react';
import api, { type ApiResponse } from '../services/api';
import type { ClassSection, Subject, Teacher, TimetableSlot } from '../types';
import { DAYS } from '../types';
import { usePermissions } from '../hooks/usePermissions';
import { getApiErrorMessage } from '../utils/apiError';

export default function TimetablePage() {
  const { can, isTeacher, isParent, isStudent } = usePermissions();
  const canManage = can('timetable.manage');
  const [slots, setSlots] = useState<TimetableSlot[]>([]);
  const [sections, setSections] = useState<ClassSection[]>([]);
  const [subjects, setSubjects] = useState<Subject[]>([]);
  const [teachers, setTeachers] = useState<Teacher[]>([]);
  const [teacherId, setTeacherId] = useState<string | null>(null);
  const [selectedSection, setSelectedSection] = useState('');
  const [showModal, setShowModal] = useState(false);
  const [editingSlot, setEditingSlot] = useState<TimetableSlot | null>(null);
  const [loading, setLoading] = useState(true);
  const [form, setForm] = useState({
    class_section_id: '', subject_id: '', teacher_id: '', day_of_week: 0,
    start_time: '09:00', end_time: '10:00', room: '',
  });

  useEffect(() => {
    const loadMeta = async () => {
      if (isTeacher) {
        const meRes = await api.get<ApiResponse<{ id: string }>>('/teachers/me');
        setTeacherId(meRes.data.data?.id || null);
        return;
      }
      if (canManage) {
        const [sectionsRes, subjectsRes, teachersRes] = await Promise.all([
          api.get<ApiResponse<ClassSection[]>>('/academic/class-sections'),
          api.get<ApiResponse<Subject[]>>('/academic/subjects'),
          api.get<ApiResponse<{ data: Teacher[] }>>('/teachers'),
        ]);
        setSections(sectionsRes.data.data || []);
        setSubjects(subjectsRes.data.data || []);
        setTeachers(teachersRes.data.data?.data || []);
      }
    };
    loadMeta().catch(console.error);
  }, [isTeacher, canManage]);

  const fetchSlots = () => {
    setLoading(true);
    const params: Record<string, string> = {};
    if (isTeacher && teacherId) {
      params.teacher_id = teacherId;
    } else if (selectedSection) {
      params.class_section_id = selectedSection;
    }
    api.get<ApiResponse<TimetableSlot[]>>('/timetable/slots', { params })
      .then((res) => setSlots(res.data.data || []))
      .catch(console.error)
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    if (isTeacher && !teacherId) return;
    if (!isTeacher || teacherId) fetchSlots();
  }, [selectedSection, teacherId, isTeacher, isParent, isStudent]);

  const openCreate = () => {
    setEditingSlot(null);
    setForm({
      class_section_id: selectedSection || '',
      subject_id: '', teacher_id: '', day_of_week: 0,
      start_time: '09:00', end_time: '10:00', room: '',
    });
    setShowModal(true);
  };

  const openEdit = (slot: TimetableSlot) => {
    setEditingSlot(slot);
    setForm({
      class_section_id: slot.class_section_id,
      subject_id: slot.subject_id,
      teacher_id: slot.teacher_id,
      day_of_week: slot.day_of_week,
      start_time: slot.start_time.slice(0, 5),
      end_time: slot.end_time.slice(0, 5),
      room: slot.room || '',
    });
    setShowModal(true);
  };

  const handleDeleteSlot = async (slot: TimetableSlot) => {
    if (!confirm(`Delete ${slot.subject_name} slot?`)) return;
    try {
      await api.delete(`/timetable/slots/${slot.id}`);
      fetchSlots();
    } catch (err) {
      alert(getApiErrorMessage(err, 'Failed to delete slot'));
    }
  };

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    try {
      const conflictRes = await api.post<ApiResponse<{ has_conflict: boolean; conflicts: string[] }>>(
        '/timetable/check-conflicts', form
      );
      if (conflictRes.data.data?.has_conflict) {
        if (!confirm(`Conflicts detected:\n${conflictRes.data.data.conflicts.join('\n')}\nProceed anyway?`)) return;
      }
      if (editingSlot) {
        await api.patch(`/timetable/slots/${editingSlot.id}`, form);
      } else {
        await api.post('/timetable/slots', form);
      }
      setShowModal(false);
      setEditingSlot(null);
      fetchSlots();
    } catch (err: unknown) {
      alert(getApiErrorMessage(err, 'Failed to save slot'));
    }
  };

  const periods = ['08:00', '09:00', '10:00', '11:00', '12:00', '13:00', '14:00', '15:00'];

  const getSlotForDayPeriod = (day: number, period: string) => {
    return slots.filter((s) => s.day_of_week === day && s.start_time.startsWith(period.slice(0, 2)));
  };

  return (
    <div>
      <div className="page-header">
        <h1>{isTeacher ? 'My Timetable' : isStudent ? 'My Timetable' : isParent ? 'Children Timetable' : 'Timetable'}</h1>
        <p>
          {canManage
            ? 'Manage class schedules and period assignments'
            : 'View your weekly class schedule'}
        </p>
      </div>

      <div className="card">
        <div className="card-header">
          <h2>Weekly Schedule</h2>
          <div style={{ display: 'flex', gap: 12 }}>
            {canManage && (
              <select value={selectedSection} onChange={(e) => setSelectedSection(e.target.value)} style={{ padding: '8px 12px', borderRadius: 8, border: '1px solid #e2e8f0' }}>
                <option value="">All Sections</option>
                {sections.map((s) => <option key={s.id} value={s.id}>{s.name}</option>)}
              </select>
            )}
            {canManage && (
              <button className="btn btn-primary" onClick={openCreate} disabled={subjects.length === 0}>
                Add Slot
              </button>
            )}
          </div>
        </div>

        {canManage && subjects.length === 0 && (
          <div className="empty-state">
            No subjects found. Go to <strong>Classes → Subjects</strong> and click <strong>Add Subject</strong> first.
          </div>
        )}

        {loading ? <p>Loading...</p> : subjects.length === 0 && canManage ? null : (
          <div className="timetable-grid">
            <table>
              <thead>
                <tr>
                  <th>Time</th>
                  {DAYS.slice(0, 5).map((day) => <th key={day}>{day}</th>)}
                </tr>
              </thead>
              <tbody>
                {periods.map((period) => (
                  <tr key={period}>
                    <td><strong>{period}</strong></td>
                    {DAYS.slice(0, 5).map((_, dayIndex) => (
                      <td key={dayIndex}>
                        {getSlotForDayPeriod(dayIndex, period).map((slot) => (
                          <div key={slot.id} className="timetable-slot" style={{ marginBottom: 4 }}>
                            <div className="subject">{slot.subject_name}</div>
                            {!isTeacher && <div className="teacher">{slot.teacher_name}</div>}
                            {isTeacher && <div className="teacher">{slot.class_section_name}</div>}
                            {slot.room && <div className="teacher">Room: {slot.room}</div>}
                            {canManage && (
                              <div className="table-actions" style={{ marginTop: 6 }}>
                                <button type="button" className="btn btn-secondary btn-sm" onClick={() => openEdit(slot)}>Edit</button>
                                <button type="button" className="btn btn-danger btn-sm" onClick={() => handleDeleteSlot(slot)}>Delete</button>
                              </div>
                            )}
                          </div>
                        ))}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {canManage && showModal && (
        <div className="modal-overlay" onClick={() => setShowModal(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <h2>{editingSlot ? 'Edit Timetable Slot' : 'Add Timetable Slot'}</h2>
            <form onSubmit={handleSubmit}>
              <div className="form-grid">
                <div className="form-group">
                  <label>Class Section</label>
                  <select required value={form.class_section_id} onChange={(e) => setForm({ ...form, class_section_id: e.target.value })}>
                    <option value="">Select section</option>
                    {sections.map((s) => <option key={s.id} value={s.id}>{s.name}</option>)}
                  </select>
                </div>
                <div className="form-group">
                  <label>Subject</label>
                  <select required value={form.subject_id} onChange={(e) => setForm({ ...form, subject_id: e.target.value })}>
                    <option value="">Select subject</option>
                    {subjects.map((s) => <option key={s.id} value={s.id}>{s.name}</option>)}
                  </select>
                </div>
                <div className="form-group">
                  <label>Teacher</label>
                  <select required value={form.teacher_id} onChange={(e) => setForm({ ...form, teacher_id: e.target.value })}>
                    <option value="">Select teacher</option>
                    {teachers.map((t) => <option key={t.id} value={t.id}>{t.first_name} {t.last_name}</option>)}
                  </select>
                </div>
                <div className="form-group">
                  <label>Day</label>
                  <select value={form.day_of_week} onChange={(e) => setForm({ ...form, day_of_week: +e.target.value })}>
                    {DAYS.map((day, i) => <option key={day} value={i}>{day}</option>)}
                  </select>
                </div>
                <div className="form-group">
                  <label>Start Time</label>
                  <input type="time" required value={form.start_time} onChange={(e) => setForm({ ...form, start_time: e.target.value })} />
                </div>
                <div className="form-group">
                  <label>End Time</label>
                  <input type="time" required value={form.end_time} onChange={(e) => setForm({ ...form, end_time: e.target.value })} />
                </div>
                <div className="form-group">
                  <label>Room</label>
                  <input value={form.room} onChange={(e) => setForm({ ...form, room: e.target.value })} />
                </div>
              </div>
              <div className="modal-actions">
                <button type="button" className="btn btn-secondary" onClick={() => setShowModal(false)}>Cancel</button>
                <button type="submit" className="btn btn-primary">{editingSlot ? 'Save Changes' : 'Add Slot'}</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
