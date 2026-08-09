import { useEffect, useState, type FormEvent } from 'react';
import { Link, useParams } from 'react-router-dom';
import api, { type ApiResponse } from '../services/api';
import type { ClassSection, Guardian, Student } from '../types';
import { usePermissions } from '../hooks/usePermissions';
import { getApiErrorMessage } from '../utils/apiError';

export default function StudentDetailPage() {
  const { id } = useParams<{ id: string }>();
  const { can } = usePermissions();
  const canManage = can('students.manage');
  const [student, setStudent] = useState<Student | null>(null);
  const [sections, setSections] = useState<ClassSection[]>([]);
  const [showEnroll, setShowEnroll] = useState(false);
  const [showGuardian, setShowGuardian] = useState(false);
  const [enrollForm, setEnrollForm] = useState({ class_section_id: '', enrollment_date: new Date().toISOString().split('T')[0] });
  const [guardianForm, setGuardianForm] = useState({ name: '', relationship_type: 'father', phone: '', email: '', occupation: '' });
  const [error, setError] = useState('');

  const load = async () => {
    if (!id) return;
    const res = await api.get<ApiResponse<Student>>(`/students/${id}`);
    setStudent(res.data.data || null);
  };

  useEffect(() => {
    load().catch(console.error);
    if (canManage) {
      api.get<ApiResponse<ClassSection[]>>('/academic/class-sections').then((res) => setSections(res.data.data || []));
    }
  }, [id, canManage]);

  const handleEnroll = async (e: FormEvent) => {
    e.preventDefault();
    setError('');
    try {
      await api.post(`/students/${id}/enroll`, enrollForm);
      setShowEnroll(false);
      load();
    } catch (err) {
      setError(getApiErrorMessage(err, 'Failed to enroll student'));
    }
  };

  const handleAddGuardian = async (e: FormEvent) => {
    e.preventDefault();
    setError('');
    try {
      await api.post(`/students/${id}/guardians`, { ...guardianForm, email: guardianForm.email || undefined });
      setShowGuardian(false);
      load();
    } catch (err) {
      setError(getApiErrorMessage(err, 'Failed to add guardian'));
    }
  };

  if (!student) return <div className="page-header"><h1>Loading...</h1></div>;

  return (
    <div>
      <div className="page-header">
        <h1>{student.first_name} {student.last_name}</h1>
        <p>Admission No: {student.admission_no} · <span className={`badge badge-${student.status === 'active' ? 'success' : 'warning'}`}>{student.status}</span></p>
        {canManage && <Link to="/students" className="btn btn-secondary" style={{ marginTop: 12, display: 'inline-block' }}>← Back to Students</Link>}
      </div>

      <div className="card">
        <div className="card-header"><h2>Profile</h2></div>
        <table>
          <tbody>
            <tr><td><strong>Email</strong></td><td>{student.email || '-'}</td></tr>
            <tr><td><strong>Date of Birth</strong></td><td>{student.date_of_birth}</td></tr>
            <tr><td><strong>Gender</strong></td><td>{student.gender}</td></tr>
            <tr><td><strong>Blood Group</strong></td><td>{student.blood_group || '-'}</td></tr>
            <tr><td><strong>Class Section</strong></td><td>{student.class_section_name || 'Not enrolled'}</td></tr>
            <tr><td><strong>Admission Date</strong></td><td>{student.admission_date}</td></tr>
            <tr><td><strong>Address</strong></td><td>{student.address || '-'}</td></tr>
          </tbody>
        </table>
        {canManage && (
          <div style={{ padding: 16 }}>
            <button className="btn btn-primary" onClick={() => setShowEnroll(true)}>Enroll in Class</button>
          </div>
        )}
      </div>

      <div className="card">
        <div className="card-header">
          <h2>Guardians</h2>
          {canManage && <button className="btn btn-primary" onClick={() => setShowGuardian(true)}>Add Guardian</button>}
        </div>
        {student.guardians.length === 0 ? (
          <div className="empty-state">No guardians linked.</div>
        ) : (
          <table>
            <thead><tr><th>Name</th><th>Relationship</th><th>Phone</th><th>Email</th></tr></thead>
            <tbody>
              {student.guardians.map((g: Guardian) => (
                <tr key={g.id}>
                  <td>{g.name}</td>
                  <td>{g.relationship_type}</td>
                  <td>{g.phone}</td>
                  <td>{g.email || '-'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {showEnroll && (
        <div className="modal-overlay" onClick={() => setShowEnroll(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <h2>Enroll Student</h2>
            {error && <div className="error" style={{ marginBottom: 16 }}>{error}</div>}
            <form onSubmit={handleEnroll}>
              <div className="form-grid">
                <div className="form-group">
                  <label>Class Section</label>
                  <select required value={enrollForm.class_section_id} onChange={(e) => setEnrollForm({ ...enrollForm, class_section_id: e.target.value })}>
                    <option value="">Select section</option>
                    {sections.map((s) => <option key={s.id} value={s.id}>{s.name}</option>)}
                  </select>
                </div>
                <div className="form-group">
                  <label>Enrollment Date</label>
                  <input type="date" required value={enrollForm.enrollment_date} onChange={(e) => setEnrollForm({ ...enrollForm, enrollment_date: e.target.value })} />
                </div>
              </div>
              <div className="modal-actions">
                <button type="button" className="btn btn-secondary" onClick={() => setShowEnroll(false)}>Cancel</button>
                <button type="submit" className="btn btn-primary">Enroll</button>
              </div>
            </form>
          </div>
        </div>
      )}

      {showGuardian && (
        <div className="modal-overlay" onClick={() => setShowGuardian(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <h2>Add Guardian</h2>
            {error && <div className="error" style={{ marginBottom: 16 }}>{error}</div>}
            <form onSubmit={handleAddGuardian}>
              <div className="form-grid">
                <div className="form-group"><label>Name</label><input required value={guardianForm.name} onChange={(e) => setGuardianForm({ ...guardianForm, name: e.target.value })} /></div>
                <div className="form-group"><label>Relationship</label><input required value={guardianForm.relationship_type} onChange={(e) => setGuardianForm({ ...guardianForm, relationship_type: e.target.value })} /></div>
                <div className="form-group"><label>Phone</label><input required value={guardianForm.phone} onChange={(e) => setGuardianForm({ ...guardianForm, phone: e.target.value })} /></div>
                <div className="form-group"><label>Email</label><input type="email" value={guardianForm.email} onChange={(e) => setGuardianForm({ ...guardianForm, email: e.target.value })} /></div>
              </div>
              <div className="modal-actions">
                <button type="button" className="btn btn-secondary" onClick={() => setShowGuardian(false)}>Cancel</button>
                <button type="submit" className="btn btn-primary">Add Guardian</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
