import { useEffect, useState, type FormEvent } from 'react';
import api, { type ApiResponse } from '../services/api';
import type { AcademicYear, ClassSection, Grade, Subject, Teacher } from '../types';
import RowActions from '../components/RowActions';
import { getApiErrorMessage } from '../utils/apiError';

type EditType = 'year' | 'grade' | 'subject' | 'section' | null;

export default function ClassesPage() {
  const [sections, setSections] = useState<ClassSection[]>([]);
  const [years, setYears] = useState<AcademicYear[]>([]);
  const [grades, setGrades] = useState<Grade[]>([]);
  const [subjects, setSubjects] = useState<Subject[]>([]);
  const [teachers, setTeachers] = useState<Teacher[]>([]);
  const [editType, setEditType] = useState<EditType>(null);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [sectionForm, setSectionForm] = useState({ name: '', capacity: 40, academic_year_id: '', grade_id: '', class_teacher_id: '' });
  const [yearForm, setYearForm] = useState({ name: '', start_date: '', end_date: '', is_current: true });
  const [gradeForm, setGradeForm] = useState({ name: '', level: 1, description: '' });
  const [subjectForm, setSubjectForm] = useState({ name: '', code: '', subject_type: 'core', description: '' });
  const [formError, setFormError] = useState('');

  const fetchData = async () => {
    setLoading(true);
    try {
      const [sectionsRes, yearsRes, gradesRes, subjectsRes, teachersRes] = await Promise.all([
        api.get<ApiResponse<ClassSection[]>>('/academic/class-sections'),
        api.get<ApiResponse<AcademicYear[]>>('/academic/years'),
        api.get<ApiResponse<Grade[]>>('/academic/grades'),
        api.get<ApiResponse<Subject[]>>('/academic/subjects'),
        api.get<ApiResponse<{ data: Teacher[] }>>('/teachers'),
      ]);
      setSections(sectionsRes.data.data || []);
      setYears(yearsRes.data.data || []);
      setGrades(gradesRes.data.data || []);
      setSubjects(subjectsRes.data.data || []);
      setTeachers(teachersRes.data.data?.data || []);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchData(); }, []);

  const closeModal = () => {
    setEditType(null);
    setEditingId(null);
    setFormError('');
  };

  const openYearModal = (year?: AcademicYear) => {
    setEditType('year');
    setEditingId(year?.id || null);
    setYearForm(year ? { name: year.name, start_date: year.start_date, end_date: year.end_date, is_current: year.is_current } : { name: '', start_date: '', end_date: '', is_current: true });
    setFormError('');
  };

  const openGradeModal = (grade?: Grade) => {
    setEditType('grade');
    setEditingId(grade?.id || null);
    setGradeForm(grade ? { name: grade.name, level: grade.level, description: grade.description || '' } : { name: '', level: 1, description: '' });
    setFormError('');
  };

  const openSubjectModal = (subject?: Subject) => {
    setEditType('subject');
    setEditingId(subject?.id || null);
    setSubjectForm(subject ? { name: subject.name, code: subject.code, subject_type: subject.subject_type, description: subject.description || '' } : { name: '', code: '', subject_type: 'core', description: '' });
    setFormError('');
  };

  const openSectionModal = (section?: ClassSection) => {
    setEditType('section');
    setEditingId(section?.id || null);
    setSectionForm(section ? {
      name: section.name,
      capacity: section.capacity,
      academic_year_id: section.academic_year_id,
      grade_id: section.grade_id,
      class_teacher_id: section.class_teacher_id || '',
    } : { name: '', capacity: 40, academic_year_id: '', grade_id: '', class_teacher_id: '' });
    setFormError('');
  };

  const handleDelete = async (type: EditType, id: string, label: string) => {
    if (!confirm(`Delete ${label}?`)) return;
    const paths: Record<string, string> = {
      year: `/academic/years/${id}`,
      grade: `/academic/grades/${id}`,
      subject: `/academic/subjects/${id}`,
      section: `/academic/class-sections/${id}`,
    };
    try {
      await api.delete(paths[type!]);
      fetchData();
    } catch (err) {
      alert(getApiErrorMessage(err, 'Failed to delete'));
    }
  };

  const handleCreateSection = async (e: FormEvent) => {
    e.preventDefault();
    setFormError('');
    try {
      if (editingId) {
        await api.patch(`/academic/class-sections/${editingId}`, {
          ...sectionForm,
          class_teacher_id: sectionForm.class_teacher_id || null,
        });
      } else {
        await api.post('/academic/class-sections', {
          ...sectionForm,
          class_teacher_id: sectionForm.class_teacher_id || undefined,
        });
      }
      closeModal();
      fetchData();
    } catch (err) {
      setFormError(getApiErrorMessage(err, 'Failed to save class section'));
    }
  };

  const handleCreateYear = async (e: FormEvent) => {
    e.preventDefault();
    setFormError('');
    try {
      if (editingId) {
        await api.patch(`/academic/years/${editingId}`, yearForm);
      } else {
        await api.post('/academic/years', yearForm);
      }
      closeModal();
      fetchData();
    } catch (err) {
      setFormError(getApiErrorMessage(err, 'Failed to save academic year'));
    }
  };

  const handleCreateGrade = async (e: FormEvent) => {
    e.preventDefault();
    setFormError('');
    try {
      if (editingId) {
        await api.patch(`/academic/grades/${editingId}`, gradeForm);
      } else {
        await api.post('/academic/grades', gradeForm);
      }
      closeModal();
      fetchData();
    } catch (err) {
      setFormError(getApiErrorMessage(err, 'Failed to save grade'));
    }
  };

  const handleCreateSubject = async (e: FormEvent) => {
    e.preventDefault();
    setFormError('');
    try {
      if (editingId) {
        await api.patch(`/academic/subjects/${editingId}`, subjectForm);
      } else {
        await api.post('/academic/subjects', subjectForm);
      }
      closeModal();
      fetchData();
    } catch (err) {
      setFormError(getApiErrorMessage(err, 'Failed to save subject'));
    }
  };

  return (
    <div>
      <div className="page-header">
        <h1>Classes & Academic Setup</h1>
        <p>Manage academic years, grades, subjects, and class sections</p>
      </div>

      <div className="card">
        <div className="card-header">
          <h2>Academic Years</h2>
          <button className="btn btn-primary" onClick={() => openYearModal()}>Add Year</button>
        </div>
        <table>
          <thead><tr><th>Name</th><th>Start</th><th>End</th><th>Current</th><th>Actions</th></tr></thead>
          <tbody>
            {years.map((y) => (
              <tr key={y.id}>
                <td>{y.name}</td>
                <td>{y.start_date}</td>
                <td>{y.end_date}</td>
                <td>{y.is_current ? <span className="badge badge-success">Current</span> : '-'}</td>
                <td>
                  <RowActions onEdit={() => openYearModal(y)} onDelete={() => handleDelete('year', y.id, y.name)} />
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="card">
        <div className="card-header">
          <h2>Grades</h2>
          <button className="btn btn-primary" onClick={() => openGradeModal()}>Add Grade</button>
        </div>
        <table>
          <thead><tr><th>Name</th><th>Level</th><th>Description</th><th>Actions</th></tr></thead>
          <tbody>
            {grades.map((g) => (
              <tr key={g.id}>
                <td>{g.name}</td>
                <td>{g.level}</td>
                <td>{g.description || '-'}</td>
                <td>
                  <RowActions onEdit={() => openGradeModal(g)} onDelete={() => handleDelete('grade', g.id, g.name)} />
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="card">
        <div className="card-header">
          <h2>Subjects</h2>
          <button className="btn btn-primary" onClick={() => openSubjectModal()}>Add Subject</button>
        </div>
        {subjects.length === 0 ? (
          <div className="empty-state">No subjects yet. Add subjects here before creating timetable slots.</div>
        ) : (
          <table>
            <thead><tr><th>Name</th><th>Code</th><th>Type</th><th>Description</th><th>Actions</th></tr></thead>
            <tbody>
              {subjects.map((s) => (
                <tr key={s.id}>
                  <td>{s.name}</td>
                  <td>{s.code}</td>
                  <td><span className="badge badge-info">{s.subject_type}</span></td>
                  <td>{s.description || '-'}</td>
                  <td>
                    <RowActions onEdit={() => openSubjectModal(s)} onDelete={() => handleDelete('subject', s.id, s.name)} />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      <div className="card">
        <div className="card-header">
          <h2>Class Sections</h2>
          <button className="btn btn-primary" onClick={() => openSectionModal()}>Add Section</button>
        </div>
        {loading ? <p>Loading...</p> : (
          <table>
            <thead><tr><th>Section</th><th>Grade</th><th>Academic Year</th><th>Capacity</th><th>Actions</th></tr></thead>
            <tbody>
              {sections.map((s) => (
                <tr key={s.id}>
                  <td>{s.name}</td>
                  <td>{s.grade_name}</td>
                  <td>{s.academic_year_name}</td>
                  <td>{s.capacity}</td>
                  <td>
                    <RowActions onEdit={() => openSectionModal(s)} onDelete={() => handleDelete('section', s.id, s.name)} />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {editType === 'section' && (
        <div className="modal-overlay" onClick={closeModal}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <h2>{editingId ? 'Edit Class Section' : 'Add Class Section'}</h2>
            {formError && <div className="error" style={{ marginBottom: 16 }}>{formError}</div>}
            <form onSubmit={handleCreateSection}>
              <div className="form-grid">
                <div className="form-group">
                  <label>Section Name</label>
                  <input required value={sectionForm.name} onChange={(e) => setSectionForm({ ...sectionForm, name: e.target.value })} placeholder="e.g. Grade 10-A" />
                </div>
                <div className="form-group">
                  <label>Capacity</label>
                  <input type="number" required value={sectionForm.capacity} onChange={(e) => setSectionForm({ ...sectionForm, capacity: +e.target.value })} />
                </div>
                <div className="form-group">
                  <label>Academic Year</label>
                  <select required value={sectionForm.academic_year_id} onChange={(e) => setSectionForm({ ...sectionForm, academic_year_id: e.target.value })}>
                    <option value="">Select year</option>
                    {years.map((y) => <option key={y.id} value={y.id}>{y.name}</option>)}
                  </select>
                </div>
                <div className="form-group">
                  <label>Grade</label>
                  <select required value={sectionForm.grade_id} onChange={(e) => setSectionForm({ ...sectionForm, grade_id: e.target.value })}>
                    <option value="">Select grade</option>
                    {grades.map((g) => <option key={g.id} value={g.id}>{g.name}</option>)}
                  </select>
                </div>
                <div className="form-group">
                  <label>Class Teacher (optional)</label>
                  <select value={sectionForm.class_teacher_id} onChange={(e) => setSectionForm({ ...sectionForm, class_teacher_id: e.target.value })}>
                    <option value="">Select teacher</option>
                    {teachers.map((t) => <option key={t.id} value={t.id}>{t.first_name} {t.last_name}</option>)}
                  </select>
                </div>
              </div>
              <div className="modal-actions">
                <button type="button" className="btn btn-secondary" onClick={closeModal}>Cancel</button>
                <button type="submit" className="btn btn-primary">{editingId ? 'Save Changes' : 'Create Section'}</button>
              </div>
            </form>
          </div>
        </div>
      )}

      {editType === 'year' && (
        <div className="modal-overlay" onClick={closeModal}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <h2>{editingId ? 'Edit Academic Year' : 'Add Academic Year'}</h2>
            {formError && <div className="error" style={{ marginBottom: 16 }}>{formError}</div>}
            <form onSubmit={handleCreateYear}>
              <div className="form-grid">
                <div className="form-group"><label>Name</label><input required value={yearForm.name} onChange={(e) => setYearForm({ ...yearForm, name: e.target.value })} placeholder="2025-2026" /></div>
                <div className="form-group"><label>Start Date</label><input type="date" required value={yearForm.start_date} onChange={(e) => setYearForm({ ...yearForm, start_date: e.target.value })} /></div>
                <div className="form-group"><label>End Date</label><input type="date" required value={yearForm.end_date} onChange={(e) => setYearForm({ ...yearForm, end_date: e.target.value })} /></div>
                <div className="form-group">
                  <label><input type="checkbox" checked={yearForm.is_current} onChange={(e) => setYearForm({ ...yearForm, is_current: e.target.checked })} /> Current year</label>
                </div>
              </div>
              <div className="modal-actions">
                <button type="button" className="btn btn-secondary" onClick={closeModal}>Cancel</button>
                <button type="submit" className="btn btn-primary">{editingId ? 'Save Changes' : 'Create Year'}</button>
              </div>
            </form>
          </div>
        </div>
      )}

      {editType === 'grade' && (
        <div className="modal-overlay" onClick={closeModal}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <h2>{editingId ? 'Edit Grade' : 'Add Grade'}</h2>
            {formError && <div className="error" style={{ marginBottom: 16 }}>{formError}</div>}
            <form onSubmit={handleCreateGrade}>
              <div className="form-grid">
                <div className="form-group"><label>Name</label><input required value={gradeForm.name} onChange={(e) => setGradeForm({ ...gradeForm, name: e.target.value })} /></div>
                <div className="form-group"><label>Level</label><input type="number" required value={gradeForm.level} onChange={(e) => setGradeForm({ ...gradeForm, level: +e.target.value })} /></div>
                <div className="form-group"><label>Description</label><input value={gradeForm.description} onChange={(e) => setGradeForm({ ...gradeForm, description: e.target.value })} /></div>
              </div>
              <div className="modal-actions">
                <button type="button" className="btn btn-secondary" onClick={closeModal}>Cancel</button>
                <button type="submit" className="btn btn-primary">{editingId ? 'Save Changes' : 'Create Grade'}</button>
              </div>
            </form>
          </div>
        </div>
      )}

      {editType === 'subject' && (
        <div className="modal-overlay" onClick={closeModal}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <h2>{editingId ? 'Edit Subject' : 'Add Subject'}</h2>
            {formError && <div className="error" style={{ marginBottom: 16 }}>{formError}</div>}
            <form onSubmit={handleCreateSubject}>
              <div className="form-grid">
                <div className="form-group">
                  <label>Subject Name</label>
                  <input required value={subjectForm.name} onChange={(e) => setSubjectForm({ ...subjectForm, name: e.target.value })} placeholder="e.g. Mathematics" />
                </div>
                <div className="form-group">
                  <label>Subject Code</label>
                  <input required value={subjectForm.code} onChange={(e) => setSubjectForm({ ...subjectForm, code: e.target.value.toUpperCase() })} placeholder="e.g. MATH101" />
                </div>
                <div className="form-group">
                  <label>Type</label>
                  <select value={subjectForm.subject_type} onChange={(e) => setSubjectForm({ ...subjectForm, subject_type: e.target.value })}>
                    <option value="core">Core</option>
                    <option value="elective">Elective</option>
                  </select>
                </div>
                <div className="form-group">
                  <label>Description</label>
                  <input value={subjectForm.description} onChange={(e) => setSubjectForm({ ...subjectForm, description: e.target.value })} placeholder="Optional" />
                </div>
              </div>
              <div className="modal-actions">
                <button type="button" className="btn btn-secondary" onClick={closeModal}>Cancel</button>
                <button type="submit" className="btn btn-primary">{editingId ? 'Save Changes' : 'Create Subject'}</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
