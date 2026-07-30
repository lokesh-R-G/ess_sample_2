import React, { useState, useEffect } from 'react';
import { api } from '../../lib/api';
import { GlassCard, AnimatedButton, Input, Select, Modal, LookupSelect, ESSLMachineLookup } from '../../components/ui';

export interface ColumnDef {
  key: string;
  label: string;
  render?: (val: any, row: any) => React.ReactNode;
}

export interface FormFieldDef {
  key: string;
  label: string;
  type: 'text' | 'number' | 'select' | 'checkbox' | 'date' | 'lookup' | 'essl-machine';
  options?: { value: string; label: string }[];
  entity?: string;
  labelField?: string;
  valueField?: string;
  required?: boolean;
}

interface GenericCRUDPageProps {
  title: string;
  endpoint: string;
  columns: ColumnDef[];
  formFields: FormFieldDef[];
}

export const GenericCRUDPage: React.FC<GenericCRUDPageProps> = ({ title, endpoint, columns, formFields }) => {
  const [data, setData] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [formData, setFormData] = useState<any>({});
  const [editingId, setEditingId] = useState<string | null>(null);

  const fetchData = async () => {
    setLoading(true);
    try {
      const res = await api.get<any>(`${endpoint}`);
      setData(res.data?.data || res.data || []);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [endpoint]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      if (editingId) {
        await api.put(`${endpoint}${editingId}/`, formData);
      } else {
        await api.post(`${endpoint}`, formData);
      }
      setIsModalOpen(false);
      fetchData();
    } catch (e) {
      console.error(e);
      alert('Error saving data');
    }
  };

  const handleDelete = async (id: string) => {
    if (!window.confirm('Are you sure you want to delete this record?')) return;
    try {
      await api.delete(`${endpoint}${id}/`);
      fetchData();
    } catch (e) {
      console.error(e);
      alert('Error deleting data');
    }
  };

  const openAddModal = () => {
    setFormData({});
    setEditingId(null);
    setIsModalOpen(true);
  };

  const openEditModal = (row: any) => {
    setFormData(row);
    setEditingId(row._id);
    setIsModalOpen(true);
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-neutral-900">{title}</h1>
        <AnimatedButton onClick={openAddModal}>Add New</AnimatedButton>
      </div>

      <GlassCard className="overflow-x-auto">
        {loading ? (
          <div className="text-center py-4">Loading...</div>
        ) : (
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="border-b border-neutral-200">
                {columns.map(c => <th key={c.key} className="p-3 font-semibold text-neutral-700">{c.label}</th>)}
                <th className="p-3 font-semibold text-neutral-700">Actions</th>
              </tr>
            </thead>
            <tbody>
              {data.map(row => (
                <tr key={row._id} className="border-b border-neutral-100 hover:bg-neutral-50/50">
                  {columns.map(c => (
                    <td key={c.key} className="p-3">
                      {c.render ? c.render(row[c.key], row) : row[c.key]}
                    </td>
                  ))}
                  <td className="p-3 space-x-2">
                    <button onClick={() => openEditModal(row)} className="text-primary-600 hover:underline">Edit</button>
                    <button onClick={() => handleDelete(row._id)} className="text-red-600 hover:underline">Delete</button>
                  </td>
                </tr>
              ))}
              {data.length === 0 && (
                <tr>
                  <td colSpan={columns.length + 1} className="p-4 text-center text-neutral-500">No records found.</td>
                </tr>
              )}
            </tbody>
          </table>
        )}
      </GlassCard>

      <Modal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        title={`${editingId ? 'Edit' : 'Add'} ${title}`}
        footer={
          <div className="flex justify-end space-x-3">
            <AnimatedButton type="button" variant="secondary" onClick={() => setIsModalOpen(false)}>Cancel</AnimatedButton>
            <AnimatedButton type="submit" form="crud-form">Save</AnimatedButton>
          </div>
        }
      >
        <form id="crud-form" onSubmit={handleSubmit} className="space-y-4">
          {formFields.map(f => (
            <div key={f.key}>
              {f.type === 'lookup' && f.entity ? (
                <LookupSelect
                  entity={f.entity}
                  labelField={f.labelField}
                  valueField={f.valueField}
                  label={f.label}
                  value={formData[f.key] || ''}
                  onChange={(val) => setFormData({ ...formData, [f.key]: val })}
                  required={f.required}
                />
              ) : f.type === 'essl-machine' ? (
                <ESSLMachineLookup
                  label={f.label}
                  value={formData[f.key] || ''}
                  onChange={(val) => setFormData({ ...formData, [f.key]: val })}
                  required={f.required}
                />
              ) : f.type === 'select' ? (
                <Select
                  label={f.label}
                  value={formData[f.key] || ''}
                  onChange={(e: any) => setFormData({ ...formData, [f.key]: e.target.value })}
                  required={f.required}
                  options={f.options || []}
                  placeholder={`Select ${f.label}`}
                />
              ) : f.type === 'checkbox' ? (
                <label className="flex items-center space-x-2">
                  <input 
                    type="checkbox" 
                    checked={!!formData[f.key]} 
                    onChange={(e) => setFormData({ ...formData, [f.key]: e.target.checked })} 
                  />
                  <span>{f.label}</span>
                </label>
              ) : (
                <Input
                  type={f.type}
                  label={f.label}
                  value={formData[f.key] || ''}
                  onChange={(e) => setFormData({ ...formData, [f.key]: e.target.value })}
                  required={f.required}
                />
              )}
            </div>
          ))}
        </form>
      </Modal>
    </div>
  );
};
