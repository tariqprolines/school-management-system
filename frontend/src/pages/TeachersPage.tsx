import { useEffect, useState, type FormEvent } from 'react';
import { Link } from 'react-router-dom';
import api, { type ApiResponse, type PaginatedResponse } from '../services/api';
import type { Teacher } from '../types';
import { usePermissions } from '../hooks/usePermissions';
import RowActions from '../components/RowActions';
import Pagination from '../components/Pagination';
import { getApiErrorMessage } from '../utils/apiError';

const emptyForm = {
  email: '', password: '', first_name: '', last_name: '', phone: '',
  department: '', qualification: '', joining_date: '', address: '',
};

export default function TeachersPage() {
  const { can, isAdmin } = usePermissions();
  const canManage = can('teachers.manage');
  const [teachers, setTeachers] = useState<Teacher[]>([]);
  const [search, setSearch] = useState('');
  const [showModal, setShowModal] = useState(false);
  const [editing, setEditing] = useState<Teacher | null>(null);
  const [loading, setLoading] = useState(true);
  const [formError, setFormError] = useState('');
  const [form, setForm] = useState(emptyForm);
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);
  const perPage = 20;

  const fetchTeachers = () => {
    setLoading(true);
    api.get<ApiResponse<PaginatedResponse<Teacher>>>('/teachers', { params: { search: search || undefined, page, per_page: perPage } })
      .then((res) => {
        setTeachers(res.data.data?.data || []);
        setTotal(res.data.data?.total_records || 0);
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  };

  useEffect(() => { fetchTeachers(); }, [page]);

  const openCreate = () => {
    setEditing(null);
    setForm(emptyForm);
    setFormError('');
    setShowModal(true);
  };

  const openEdit = (teacher: Teacher) => {
    setEditing(teacher);
    setForm({
      email: teacher.email || '',
      password: '',
      first_name: teacher.first_name || '',
      last_name: teacher.last_name || '',
      phone: teacher.phone || '',
      department: teacher.department,
      qualification: teacher.qualification || '',
      joining_date: teacher.joining_date,
      address: teacher.address || '',
    });
    setFormError('');
    setShowModal(true);
  };

  const handleDelete = async (teacher: Teacher) => {
    if (!confirm(`Delete teacher ${teacher.first_name} ${teacher.last_name}?`)) return;
    try {
      await api.delete(`/teachers/${teacher.id}`);
      fetchTeachers();
    } catch (err) {
      alert(getApiErrorMessage(err, 'Failed to delete teacher'));
    }
  };

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setFormError('');
    try {
      if (editing) {
        await api.patch(`/teachers/${editing.id}`, {
          first_name: form.first_name,
          last_name: form.last_name,
          phone: form.phone || undefined,
          department: form.department,
          qualification: form.qualification || undefined,
          address: form.address || undefined,
        });
      } else {
        await api.post('/teachers', form);
      }
      setShowModal(false);
      fetchTeachers();
    } catch (err) {
      setFormError(getApiErrorMessage(err, editing ? 'Failed to update teacher' : 'Failed to create teacher'));
    }
  };

  return (
    <div>
      <div className="page-header">
        <h1>Teachers</h1>
        <p>{isAdmin ? 'Manage teacher profiles and assignments' : 'Teacher directory'}</p>
      </div>

      <div className="card">
        <div className="card-header">
          <h2>All Teachers</h2>
          {canManage && <button className="btn btn-primary" onClick={openCreate}>Add Teacher</button>}
        </div>
        <div className="search-bar">
          <input placeholder="Search by name or employee ID..." value={search} onChange={(e) => setSearch(e.target.value)} />
          <button className="btn btn-secondary" onClick={fetchTeachers}>Search</button>
        </div>
        {loading ? <p>Loading...</p> : teachers.length === 0 ? (
          <div className="empty-state">No teachers found. Add your first teacher.</div>
        ) : (
          <table>
            <thead>
              <tr>
                <th>Employee ID</th>
                <th>Name</th>
                <th>Email</th>
                <th>Department</th>
                <th>Joining Date</th>
                {canManage && <th>Actions</th>}
              </tr>
            </thead>
            <tbody>
              {teachers.map((t) => (
                <tr key={t.id}>
                  <td>{t.employee_id}</td>
                  <td><Link to={`/teachers/${t.id}`} className="table-link">{t.first_name} {t.last_name}</Link></td>
                  <td>{t.email}</td>
                  <td>{t.department}</td>
                  <td>{t.joining_date}</td>
                  {canManage && (
                    <td>
                      <RowActions onEdit={() => openEdit(t)} onDelete={() => handleDelete(t)} />
                    </td>
                  )}
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
            <h2>{editing ? 'Edit Teacher' : 'Add New Teacher'}</h2>
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
                      <label>Email</label>
                      <input type="email" required value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} />
                    </div>
                    <div className="form-group">
                      <label>Password</label>
                      <input type="password" required value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} />
                    </div>
                    <div className="form-group">
                      <label>Joining Date</label>
                      <input type="date" required value={form.joining_date} onChange={(e) => setForm({ ...form, joining_date: e.target.value })} />
                    </div>
                  </>
                )}
                <div className="form-group">
                  <label>Department</label>
                  <input required value={form.department} onChange={(e) => setForm({ ...form, department: e.target.value })} />
                </div>
                <div className="form-group">
                  <label>Phone</label>
                  <input value={form.phone} onChange={(e) => setForm({ ...form, phone: e.target.value })} />
                </div>
                <div className="form-group">
                  <label>Qualification</label>
                  <input value={form.qualification} onChange={(e) => setForm({ ...form, qualification: e.target.value })} />
                </div>
                <div className="form-group">
                  <label>Address</label>
                  <input value={form.address} onChange={(e) => setForm({ ...form, address: e.target.value })} />
                </div>
              </div>
              <div className="modal-actions">
                <button type="button" className="btn btn-secondary" onClick={() => setShowModal(false)}>Cancel</button>
                <button type="submit" className="btn btn-primary">{editing ? 'Save Changes' : 'Create Teacher'}</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
