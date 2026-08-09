import { useEffect, useState, type FormEvent } from 'react';
import { Link, useParams } from 'react-router-dom';
import api, { type ApiResponse } from '../services/api';
import type { ClassSection, Subject, Teacher } from '../types';
import { usePermissions } from '../hooks/usePermissions';
import { getApiErrorMessage } from '../utils/apiError';

interface SubjectAssignment {
  id: string;
  subject_id: string;
  class_section_id: string;
  subject_name: string;
  class_section_name: string;
}

export default function TeacherDetailPage() {
  const { id } = useParams<{ id: string }>();
  const { can } = usePermissions();
  const canManage = can('teachers.manage');
  const [teacher, setTeacher] = useState<Teacher | null>(null);
  const [assignments, setAssignments] = useState<SubjectAssignment[]>([]);
  const [subjects, setSubjects] = useState<Subject[]>([]);
  const [sections, setSections] = useState<ClassSection[]>([]);
  const [showAssign, setShowAssign] = useState(false);
  const [assignForm, setAssignForm] = useState({ subject_id: '', class_section_id: '' });
  const [error, setError] = useState('');

  const load = async () => {
    if (!id) return;
    const [teacherRes, assignRes] = await Promise.all([
      api.get<ApiResponse<Teacher>>(`/teachers/${id}`),
      api.get<ApiResponse<SubjectAssignment[]>>(`/teachers/${id}/subjects`),
    ]);
    setTeacher(teacherRes.data.data || null);
    setAssignments(assignRes.data.data || []);
  };

  useEffect(() => {
    load().catch(console.error);
    if (canManage) {
      Promise.all([
        api.get<ApiResponse<Subject[]>>('/academic/subjects'),
        api.get<ApiResponse<ClassSection[]>>('/academic/class-sections'),
      ]).then(([s, sec]) => {
        setSubjects(s.data.data || []);
        setSections(sec.data.data || []);
      });
    }
  }, [id, canManage]);

  const handleAssign = async (e: FormEvent) => {
    e.preventDefault();
    setError('');
    try {
      await api.post(`/teachers/${id}/subjects`, assignForm);
      setShowAssign(false);
      setAssignForm({ subject_id: '', class_section_id: '' });
      load();
    } catch (err) {
      setError(getApiErrorMessage(err, 'Failed to assign subject'));
    }
  };

  const handleRemove = async (assignmentId: string) => {
    if (!confirm('Remove this subject assignment?')) return;
    try {
      await api.delete(`/teachers/${id}/subjects/${assignmentId}`);
      load();
    } catch (err) {
      alert(getApiErrorMessage(err, 'Failed to remove assignment'));
    }
  };

  if (!teacher) return <div className="page-header"><h1>Loading...</h1></div>;

  return (
    <div>
      <div className="page-header">
        <h1>{teacher.first_name} {teacher.last_name}</h1>
        <p>Employee ID: {teacher.employee_id} · {teacher.department}</p>
        <Link to="/teachers" className="btn btn-secondary" style={{ marginTop: 12, display: 'inline-block' }}>← Back to Teachers</Link>
      </div>

      <div className="card">
        <div className="card-header"><h2>Profile</h2></div>
        <table>
          <tbody>
            <tr><td><strong>Email</strong></td><td>{teacher.email}</td></tr>
            <tr><td><strong>Phone</strong></td><td>{teacher.phone || '-'}</td></tr>
            <tr><td><strong>Qualification</strong></td><td>{teacher.qualification || '-'}</td></tr>
            <tr><td><strong>Joining Date</strong></td><td>{teacher.joining_date}</td></tr>
            <tr><td><strong>Address</strong></td><td>{teacher.address || '-'}</td></tr>
          </tbody>
        </table>
      </div>

      <div className="card">
        <div className="card-header">
          <h2>Subject Assignments</h2>
          {canManage && <button className="btn btn-primary" onClick={() => setShowAssign(true)}>Assign Subject</button>}
        </div>
        {assignments.length === 0 ? (
          <div className="empty-state">No subject assignments yet.</div>
        ) : (
          <table>
            <thead><tr><th>Subject</th><th>Class Section</th>{canManage && <th>Actions</th>}</tr></thead>
            <tbody>
              {assignments.map((a) => (
                <tr key={a.id}>
                  <td>{a.subject_name}</td>
                  <td>{a.class_section_name}</td>
                  {canManage && (
                    <td><button className="btn btn-danger btn-sm" onClick={() => handleRemove(a.id)}>Remove</button></td>
                  )}
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {showAssign && (
        <div className="modal-overlay" onClick={() => setShowAssign(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <h2>Assign Subject</h2>
            {error && <div className="error" style={{ marginBottom: 16 }}>{error}</div>}
            <form onSubmit={handleAssign}>
              <div className="form-grid">
                <div className="form-group">
                  <label>Subject</label>
                  <select required value={assignForm.subject_id} onChange={(e) => setAssignForm({ ...assignForm, subject_id: e.target.value })}>
                    <option value="">Select subject</option>
                    {subjects.map((s) => <option key={s.id} value={s.id}>{s.name}</option>)}
                  </select>
                </div>
                <div className="form-group">
                  <label>Class Section</label>
                  <select required value={assignForm.class_section_id} onChange={(e) => setAssignForm({ ...assignForm, class_section_id: e.target.value })}>
                    <option value="">Select section</option>
                    {sections.map((s) => <option key={s.id} value={s.id}>{s.name}</option>)}
                  </select>
                </div>
              </div>
              <div className="modal-actions">
                <button type="button" className="btn btn-secondary" onClick={() => setShowAssign(false)}>Cancel</button>
                <button type="submit" className="btn btn-primary">Assign</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
