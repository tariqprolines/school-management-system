import { useEffect, useState, type FormEvent } from 'react';
import api, { type ApiResponse } from '../services/api';
import type { AcademicYear, ClassSection, FeeCategory, FeeInvoice, FeeStructure } from '../types';
import { usePermissions } from '../hooks/usePermissions';
import RowActions from '../components/RowActions';
import { getApiErrorMessage } from '../utils/apiError';

export default function FeesPage() {
  const { can, isAccountant, isParent, isStudent } = usePermissions();
  const canManage = can('fees.manage');
  const [categories, setCategories] = useState<FeeCategory[]>([]);
  const [structures, setStructures] = useState<FeeStructure[]>([]);
  const [invoices, setInvoices] = useState<FeeInvoice[]>([]);
  const [defaulters, setDefaulters] = useState<FeeInvoice[]>([]);
  const [sections, setSections] = useState<ClassSection[]>([]);
  const [years, setYears] = useState<AcademicYear[]>([]);
  const [activeTab, setActiveTab] = useState<'structures' | 'invoices' | 'defaulters'>('structures');
  const [showCategoryModal, setShowCategoryModal] = useState(false);
  const [showStructureModal, setShowStructureModal] = useState(false);
  const [showCollectModal, setShowCollectModal] = useState(false);
  const [editingCategory, setEditingCategory] = useState<FeeCategory | null>(null);
  const [editingStructure, setEditingStructure] = useState<FeeStructure | null>(null);
  const [formError, setFormError] = useState('');
  const [categoryForm, setCategoryForm] = useState({ name: '', description: '' });
  const [structureForm, setStructureForm] = useState({
    category_id: '', class_section_id: '', amount: '', due_date: '', academic_year_id: '',
  });
  const [collectForm, setCollectForm] = useState({
    invoice_id: '', amount: '', payment_mode: 'cash', payment_date: new Date().toISOString().split('T')[0],
  });

  const fetchData = async () => {
    if (canManage) {
      const [catRes, structRes, invRes, defRes, secRes, yearRes] = await Promise.all([
        api.get<ApiResponse<FeeCategory[]>>('/fees/categories'),
        api.get<ApiResponse<FeeStructure[]>>('/fees/structures'),
        api.get<ApiResponse<FeeInvoice[]>>('/fees/invoices'),
        api.get<ApiResponse<FeeInvoice[]>>('/fees/defaulters'),
        api.get<ApiResponse<ClassSection[]>>('/academic/class-sections'),
        api.get<ApiResponse<AcademicYear[]>>('/academic/years'),
      ]);
      setCategories(catRes.data.data || []);
      setStructures(structRes.data.data || []);
      setInvoices(invRes.data.data || []);
      setDefaulters(defRes.data.data || []);
      setSections(secRes.data.data || []);
      setYears(yearRes.data.data || []);
    } else {
      const invRes = await api.get<ApiResponse<FeeInvoice[]>>('/fees/invoices');
      setInvoices(invRes.data.data || []);
    }
  };

  const openCategoryModal = (category?: FeeCategory) => {
    setEditingCategory(category || null);
    setCategoryForm(category ? { name: category.name, description: category.description || '' } : { name: '', description: '' });
    setFormError('');
    setShowCategoryModal(true);
  };

  const openStructureModal = (structure?: FeeStructure) => {
    setEditingStructure(structure || null);
    setStructureForm(structure ? {
      category_id: structure.category_id,
      class_section_id: structure.class_section_id,
      amount: String(structure.amount),
      due_date: structure.due_date,
      academic_year_id: structure.academic_year_id,
    } : { category_id: '', class_section_id: '', amount: '', due_date: '', academic_year_id: '' });
    setFormError('');
    setShowStructureModal(true);
  };

  const handleDeleteCategory = async (category: FeeCategory) => {
    if (!confirm(`Delete category "${category.name}"?`)) return;
    try {
      await api.delete(`/fees/categories/${category.id}`);
      fetchData();
    } catch (err) {
      alert(getApiErrorMessage(err, 'Failed to delete category'));
    }
  };

  const handleDeleteStructure = async (structure: FeeStructure) => {
    if (!confirm('Delete this fee structure?')) return;
    try {
      await api.delete(`/fees/structures/${structure.id}`);
      fetchData();
    } catch (err) {
      alert(getApiErrorMessage(err, 'Failed to delete structure'));
    }
  };

  const handleCreateCategory = async (e: FormEvent) => {
    e.preventDefault();
    setFormError('');
    try {
      if (editingCategory) {
        await api.patch(`/fees/categories/${editingCategory.id}`, categoryForm);
      } else {
        await api.post('/fees/categories', categoryForm);
      }
      setShowCategoryModal(false);
      fetchData();
    } catch (err) {
      setFormError(getApiErrorMessage(err, 'Failed to save category'));
    }
  };

  const handleCreateStructure = async (e: FormEvent) => {
    e.preventDefault();
    setFormError('');
    try {
      const payload = { ...structureForm, amount: parseFloat(structureForm.amount) };
      if (editingStructure) {
        await api.patch(`/fees/structures/${editingStructure.id}`, payload);
      } else {
        await api.post('/fees/structures', payload);
      }
      setShowStructureModal(false);
      fetchData();
    } catch (err) {
      setFormError(getApiErrorMessage(err, 'Failed to save structure'));
    }
  };

  const handleGenerateInvoices = async (structureId: string) => {
    const res = await api.post<ApiResponse<{ created: number }>>('/fees/generate-invoices', { fee_structure_id: structureId });
    alert(`Generated ${res.data.data?.created} invoices`);
    fetchData();
  };

  const handleCollect = async (e: FormEvent) => {
    e.preventDefault();
    await api.post('/fees/collect', { ...collectForm, amount: parseFloat(collectForm.amount) });
    setShowCollectModal(false);
    fetchData();
  };

  const statusBadge = (status: string) => {
    const map: Record<string, string> = { paid: 'success', pending: 'warning', partial: 'info', overdue: 'danger' };
    return <span className={`badge badge-${map[status] || 'info'}`}>{status}</span>;
  };

  useEffect(() => {
    if (!canManage) setActiveTab('invoices');
    fetchData();
  }, [canManage]);

  return (
    <div>
      <div className="page-header">
        <h1>{isAccountant ? 'Fee Management' : isStudent ? 'My Fees' : isParent ? 'School Fees' : 'Fees'}</h1>
        <p>
          {canManage
            ? 'Manage fee categories, structures, invoices, and collections'
            : 'View fee invoices and payment status'}
        </p>
      </div>

      {canManage && (
        <div className="card">
          <div className="card-header">
            <h2>Fee Categories</h2>
            <button className="btn btn-primary" onClick={() => openCategoryModal()}>Add Category</button>
          </div>
          <table>
            <thead><tr><th>Name</th><th>Description</th><th>Actions</th></tr></thead>
            <tbody>
              {categories.map((c) => (
                <tr key={c.id}>
                  <td>{c.name}</td>
                  <td>{c.description || '-'}</td>
                  <td>
                    <RowActions onEdit={() => openCategoryModal(c)} onDelete={() => handleDeleteCategory(c)} />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <div className="card">
        <div className="card-header">
          <div style={{ display: 'flex', gap: 16 }}>
            {(canManage ? (['structures', 'invoices', 'defaulters'] as const) : (['invoices'] as const)).map((tab) => (
              <button key={tab} className={`btn ${activeTab === tab ? 'btn-primary' : 'btn-secondary'}`} onClick={() => setActiveTab(tab)}>
                {tab.charAt(0).toUpperCase() + tab.slice(1)}
              </button>
            ))}
          </div>
          {canManage && activeTab === 'structures' && (
            <button className="btn btn-primary" onClick={() => openStructureModal()}>Add Structure</button>
          )}
          {canManage && activeTab === 'invoices' && (
            <button className="btn btn-primary" onClick={() => setShowCollectModal(true)}>Collect Fee</button>
          )}
        </div>

        {canManage && activeTab === 'structures' && (
          <table>
            <thead><tr><th>Category</th><th>Class</th><th>Amount</th><th>Due Date</th><th>Actions</th></tr></thead>
            <tbody>
              {structures.map((s) => (
                <tr key={s.id}>
                  <td>{s.category_name}</td>
                  <td>{s.class_section_name}</td>
                  <td>${Number(s.amount).toLocaleString()}</td>
                  <td>{s.due_date}</td>
                  <td>
                    <div className="table-actions">
                      <button className="btn btn-secondary btn-sm" onClick={() => handleGenerateInvoices(s.id)}>Generate</button>
                      <button className="btn btn-secondary btn-sm" onClick={() => openStructureModal(s)}>Edit</button>
                      <button className="btn btn-danger btn-sm" onClick={() => handleDeleteStructure(s)}>Delete</button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}

        {activeTab === 'invoices' && (
          <table>
            <thead><tr><th>Invoice No</th><th>Student</th><th>Category</th><th>Amount</th><th>Paid</th><th>Status</th><th>Due Date</th></tr></thead>
            <tbody>
              {invoices.map((inv) => (
                <tr key={inv.id}>
                  <td>{inv.invoice_no}</td>
                  <td>{inv.student_name}</td>
                  <td>{inv.category_name}</td>
                  <td>${Number(inv.amount).toLocaleString()}</td>
                  <td>${Number(inv.paid_amount).toLocaleString()}</td>
                  <td>{statusBadge(inv.status)}</td>
                  <td>{inv.due_date}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}

        {canManage && activeTab === 'defaulters' && (
          <table>
            <thead><tr><th>Invoice No</th><th>Student</th><th>Outstanding</th><th>Due Date</th><th>Status</th></tr></thead>
            <tbody>
              {defaulters.length === 0 ? (
                <tr><td colSpan={5} className="empty-state">No defaulters found</td></tr>
              ) : defaulters.map((d) => (
                <tr key={d.id}>
                  <td>{d.invoice_no}</td>
                  <td>{d.student_name}</td>
                  <td style={{ color: '#dc2626' }}>${Number(d.outstanding).toLocaleString()}</td>
                  <td>{d.due_date}</td>
                  <td>{statusBadge(d.status)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {canManage && showCategoryModal && (
        <div className="modal-overlay" onClick={() => setShowCategoryModal(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <h2>{editingCategory ? 'Edit Fee Category' : 'Add Fee Category'}</h2>
            {formError && <div className="error" style={{ marginBottom: 16 }}>{formError}</div>}
            <form onSubmit={handleCreateCategory}>
              <div className="form-group"><label>Name</label><input required value={categoryForm.name} onChange={(e) => setCategoryForm({ ...categoryForm, name: e.target.value })} /></div>
              <div className="form-group"><label>Description</label><input value={categoryForm.description} onChange={(e) => setCategoryForm({ ...categoryForm, description: e.target.value })} /></div>
              <div className="modal-actions">
                <button type="button" className="btn btn-secondary" onClick={() => setShowCategoryModal(false)}>Cancel</button>
                <button type="submit" className="btn btn-primary">{editingCategory ? 'Save Changes' : 'Create'}</button>
              </div>
            </form>
          </div>
        </div>
      )}

      {canManage && showStructureModal && (
        <div className="modal-overlay" onClick={() => setShowStructureModal(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <h2>{editingStructure ? 'Edit Fee Structure' : 'Add Fee Structure'}</h2>
            {formError && <div className="error" style={{ marginBottom: 16 }}>{formError}</div>}
            <form onSubmit={handleCreateStructure}>
              <div className="form-grid">
                <div className="form-group">
                  <label>Category</label>
                  <select required value={structureForm.category_id} onChange={(e) => setStructureForm({ ...structureForm, category_id: e.target.value })}>
                    <option value="">Select</option>
                    {categories.map((c) => <option key={c.id} value={c.id}>{c.name}</option>)}
                  </select>
                </div>
                <div className="form-group">
                  <label>Class Section</label>
                  <select required value={structureForm.class_section_id} onChange={(e) => setStructureForm({ ...structureForm, class_section_id: e.target.value })}>
                    <option value="">Select</option>
                    {sections.map((s) => <option key={s.id} value={s.id}>{s.name}</option>)}
                  </select>
                </div>
                <div className="form-group">
                  <label>Academic Year</label>
                  <select required value={structureForm.academic_year_id} onChange={(e) => setStructureForm({ ...structureForm, academic_year_id: e.target.value })}>
                    <option value="">Select</option>
                    {years.map((y) => <option key={y.id} value={y.id}>{y.name}</option>)}
                  </select>
                </div>
                <div className="form-group"><label>Amount</label><input type="number" required value={structureForm.amount} onChange={(e) => setStructureForm({ ...structureForm, amount: e.target.value })} /></div>
                <div className="form-group"><label>Due Date</label><input type="date" required value={structureForm.due_date} onChange={(e) => setStructureForm({ ...structureForm, due_date: e.target.value })} /></div>
              </div>
              <div className="modal-actions">
                <button type="button" className="btn btn-secondary" onClick={() => setShowStructureModal(false)}>Cancel</button>
                <button type="submit" className="btn btn-primary">{editingStructure ? 'Save Changes' : 'Create'}</button>
              </div>
            </form>
          </div>
        </div>
      )}

      {canManage && showCollectModal && (
        <div className="modal-overlay" onClick={() => setShowCollectModal(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <h2>Collect Fee</h2>
            <form onSubmit={handleCollect}>
              <div className="form-grid">
                <div className="form-group">
                  <label>Invoice</label>
                  <select required value={collectForm.invoice_id} onChange={(e) => setCollectForm({ ...collectForm, invoice_id: e.target.value })}>
                    <option value="">Select invoice</option>
                    {invoices.filter((i) => i.status !== 'paid').map((i) => (
                      <option key={i.id} value={i.id}>{i.invoice_no} - {i.student_name} (${Number(i.amount - i.paid_amount).toFixed(2)} due)</option>
                    ))}
                  </select>
                </div>
                <div className="form-group"><label>Amount</label><input type="number" required value={collectForm.amount} onChange={(e) => setCollectForm({ ...collectForm, amount: e.target.value })} /></div>
                <div className="form-group">
                  <label>Payment Mode</label>
                  <select value={collectForm.payment_mode} onChange={(e) => setCollectForm({ ...collectForm, payment_mode: e.target.value })}>
                    <option value="cash">Cash</option>
                    <option value="card">Card</option>
                    <option value="bank_transfer">Bank Transfer</option>
                    <option value="online">Online</option>
                  </select>
                </div>
                <div className="form-group"><label>Payment Date</label><input type="date" required value={collectForm.payment_date} onChange={(e) => setCollectForm({ ...collectForm, payment_date: e.target.value })} /></div>
              </div>
              <div className="modal-actions">
                <button type="button" className="btn btn-secondary" onClick={() => setShowCollectModal(false)}>Cancel</button>
                <button type="submit" className="btn btn-primary">Record Payment</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
