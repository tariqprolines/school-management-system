import { useEffect, useState, type FormEvent } from 'react';
import { Link } from 'react-router-dom';
import api, { type ApiResponse, type PaginatedResponse } from '../services/api';
import type { Student } from '../types';
import { usePermissions } from '../hooks/usePermissions';
import RowActions from '../components/RowActions';
import Pagination from '../components/Pagination';
import { getApiErrorMessage } from '../utils/apiError';

const emptyForm = {
  first_name: '', last_name: '', email: '', date_of_birth: '', gender: 'male',
  blood_group: '', address: '', admission_date: new Date().toISOString().split('T')[0],
  status: 'active', guardian_name: '', guardian_phone: '', guardian_relationship: 'father',
};

export default function StudentsPage() {
  const { can, isTeacher, isParent } = usePermissions();
  const canManage = can('students.manage');
  const [students, setStudents] = useState<Student[]>([]);
  const [search, setSearch] = useState('');
  const [showModal, setShowModal] = useState(false);
  const [editing, setEditing] = useState<Student | null>(null);
  const [loading, setLoading] = useState(true);
  const [formError, setFormError] = useState('');
  const [form, setForm] = useState(emptyForm);
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);
  const perPage = 20;

  const fetchStudents = () => {
    setLoading(true);
    api.get<ApiResponse<PaginatedResponse<Student>>>('/students', { params: { search: search || undefined, page, per_page: perPage } })
      .then((res) => {
        setStudents(res.data.data?.data || []);
        setTotal(res.data.data?.total_records || 0);
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  };

  useEffect(() => { fetchStudents(); }, [page]);

  const openCreate = () => {
    setEditing(null);
    setForm(emptyForm);
    setFormError('');
    setShowModal(true);
  };

  const openEdit = (student: Student) => {
    setEditing(student);
    setForm({
      first_name: student.first_name || '',
      last_name: student.last_name || '',
      email: student.email || '',
      date_of_birth: student.date_of_birth,
      gender: student.gender,
      blood_group: student.blood_group || '',
      address: student.address || '',
      admission_date: student.admission_date,
      status: student.status,
      guardian_name: student.guardians?.[0]?.name || '',
      guardian_phone: student.guardians?.[0]?.phone || '',
      guardian_relationship: student.guardians?.[0]?.relationship_type || 'father',
    });
    setFormError('');
    setShowModal(true);
  };

  const handleDelete = async (student: Student) => {
    if (!confirm(`Delete student ${student.first_name} ${student.last_name}?`)) return;
    try {
      await api.delete(`/students/${student.id}`);
      fetchStudents();
    } catch (err) {
      alert(getApiErrorMessage(err, 'Failed to delete student'));
    }
  };

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setFormError('');
    try {
      if (editing) {
        await api.patch(`/students/${editing.id}`, {
          first_name: form.first_name,
          last_name: form.last_name,
          blood_group: form.blood_group || undefined,
          address: form.address || undefined,
          status: form.status,
        });
      } else {
        await api.post('/students', {
          first_name: form.first_name,
          last_name: form.last_name,
          email: form.email || undefined,
          date_of_birth: form.date_of_birth,
          gender: form.gender,
          blood_group: form.blood_group || undefined,
          address: form.address || undefined,
          admission_date: form.admission_date,
          guardians: form.guardian_name ? [{
            name: form.guardian_name,
            relationship_type: form.guardian_relationship,
            phone: form.guardian_phone,
            is_primary: true,
          }] : [],
        });
      }
      setShowModal(false);
      fetchStudents();
    } catch (err) {
      setFormError(getApiErrorMessage(err, editing ? 'Failed to update student' : 'Failed to create student'));
    }
  };

  return (
    <div>
      <div className="page-header">
        <h1>{isTeacher ? 'My Students' : isParent ? 'My Children' : 'Students'}</h1>
        <p>{canManage ? 'Manage student admissions and profiles' : 'View student records (read-only)'}</p>
      </div>

      <div className="card">
        <div className="card-header">
          <h2>{isTeacher ? 'Class Students' : isParent ? 'Children' : 'All Students'}</h2>
          {canManage && <button className="btn btn-primary" onClick={openCreate}>Admit Student</button>}
        </div>
        <div className="search-bar">
          <input placeholder="Search by admission number..." value={search} onChange={(e) => setSearch(e.target.value)} />
          <button className="btn btn-secondary" onClick={fetchStudents}>Search</button>
        </div>
        {loading ? <p>Loading...</p> : students.length === 0 ? (
          <div className="empty-state">No students found. Admit your first student.</div>
        ) : (
          <table>
            <thead>
              <tr>
                <th>Admission No</th>
                <th>Name</th>
                <th>Gender</th>
                <th>Class</th>
                <th>Status</th>
                <th>Admission Date</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {students.map((s) => (
                <tr key={s.id}>
                  <td>{s.admission_no}</td>
                  <td>
                    <Link to={`/students/${s.id}`} className="table-link">{s.first_name} {s.last_name}</Link>
                  </td>
                  <td>{s.gender}</td>
                  <td>{s.class_section_name || '-'}</td>
                  <td><span className={`badge badge-${s.status === 'active' ? 'success' : 'warning'}`}>{s.status}</span></td>
                  <td>{s.admission_date}</td>
                  <td>
                    {canManage ? (
                      <RowActions onEdit={() => openEdit(s)} onDelete={() => handleDelete(s)} />
                    ) : (
                      <Link to={`/students/${s.id}`} className="btn btn-secondary btn-sm">View</Link>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
        <Pagination page={page} perPage={perPage} total={total} onPageChange={setPage} />
      </div>

      {showModal && (
        <div className="modal-overlay" onClick={() => setShowModal(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <h2>{editing ? 'Edit Student' : 'Admit New Student'}</h2>
            {formError && <div className="error" style={{ marginBottom: 16 }}>{formError}</div>}
            <form onSubmit={handleSubmit}>
              <div className="form-grid">
                <div className="form-group">
                  <label>First Name</label>
                  <input required value={form.first_name} onChange={(e) => setForm({ ...form, first_name: e.target.value })} />
                </div>
                <div className="form-group">
                  <label>Last Name</label>
                  <input required value={form.last_name} onChange={(e) => setForm({ ...form, last_name: e.target.value })} />
                </div>
                {!editing && (
                  <>
                    <div className="form-group">
                      <label>Date of Birth</label>
                      <input type="date" required value={form.date_of_birth} onChange={(e) => setForm({ ...form, date_of_birth: e.target.value })} />
                    </div>
                    <div className="form-group">
                      <label>Gender</label>
                      <select value={form.gender} onChange={(e) => setForm({ ...form, gender: e.target.value })}>
                        <option value="male">Male</option>
                        <option value="female">Female</option>
                        <option value="other">Other</option>
                      </select>
                    </div>
                    <div className="form-group">
                      <label>Admission Date</label>
                      <input type="date" required value={form.admission_date} onChange={(e) => setForm({ ...form, admission_date: e.target.value })} />
                    </div>
                    <div className="form-group">
                      <label>Email (optional)</label>
                      <input type="email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} />
                    </div>
                    <div className="form-group">
                      <label>Guardian Name</label>
                      <input value={form.guardian_name} onChange={(e) => setForm({ ...form, guardian_name: e.target.value })} />
                    </div>
                    <div className="form-group">
                      <label>Guardian Phone</label>
                      <input value={form.guardian_phone} onChange={(e) => setForm({ ...form, guardian_phone: e.target.value })} />
                    </div>
                  </>
                )}
                {editing && (
                  <div className="form-group">
                    <label>Status</label>
                    <select value={form.status} onChange={(e) => setForm({ ...form, status: e.target.value })}>
                      <option value="active">Active</option>
                      <option value="transferred">Transferred</option>
                      <option value="graduated">Graduated</option>
                      <option value="inactive">Inactive</option>
                    </select>
                  </div>
                )}
                <div className="form-group">
                  <label>Blood Group</label>
                  <input value={form.blood_group} onChange={(e) => setForm({ ...form, blood_group: e.target.value })} />
                </div>
                <div className="form-group">
                  <label>Address</label>
                  <input value={form.address} onChange={(e) => setForm({ ...form, address: e.target.value })} />
                </div>
              </div>
              <div className="modal-actions">
                <button type="button" className="btn btn-secondary" onClick={() => setShowModal(false)}>Cancel</button>
                <button type="submit" className="btn btn-primary">{editing ? 'Save Changes' : 'Admit Student'}</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
