import React, { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { employeeApi } from '../../services/employeeApi';
import { GlassCard, AnimatedButton } from '../../components/ui';
import { toast } from 'react-hot-toast';
import { ChevronLeft, Save, Calendar } from 'lucide-react';
import SalaryPayrollStep from './employee/wizard-steps/SalaryPayrollStep';
import { Input } from '../../components/ui';

export default function AdminEmployeeSalaryConfig() {
  const navigate = useNavigate();
  const { id: employeeId } = useParams<{ id: string }>();
  
  const [employee, setEmployee] = useState<any>(null);
  const [formData, setFormData] = useState<any>({});
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    if (employeeId) {
      loadData(employeeId);
    }
  }, [employeeId]);

  const loadData = async (empId: string) => {
    setLoading(true);
    try {
      const [empRes, configRes] = await Promise.all([
        employeeApi.getEmployee(empId),
        employeeApi.getSalaryConfig(empId)
      ]);
      setEmployee(empRes?.data || empRes || null);
      
      const config = configRes?.data || configRes || {};
      
      setFormData({
        employeeId: empId,
        ...config
      });
      
    } catch (e) {
      console.error(e);
      toast.error('Failed to load employee salary configuration');
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    if (!formData.salaryStructureId || !formData.basicSalary) {
      toast.error("Please configure basic salary and structure.");
      return;
    }
    
    if (!formData.effectiveFrom) {
      toast.error("Effective date is required.");
      return;
    }
    
    setSaving(true);
    try {
      const payload = {
        ...formData,
        employeeId: employeeId,
      };
      
      await employeeApi.assignSalary(payload);
      toast.success("Salary configuration finalized successfully");
      navigate('/admin/employee-salary');
    } catch (e: any) {
      console.error(e);
      const errorMsg = e instanceof Error ? e.message : 'Failed to save salary configuration';
      toast.error(errorMsg);
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return <div className="text-center py-10 text-neutral-500">Loading configuration...</div>;
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center space-x-4 mb-6">
        <button 
          onClick={() => navigate('/admin/employee-salary')}
          className="p-2 hover:bg-neutral-100 rounded-full transition-colors text-neutral-500"
        >
          <ChevronLeft className="w-5 h-5" />
        </button>
        <div>
          <h1 className="text-2xl font-bold text-neutral-900">
            Configure Salary: {employee?.firstName} {employee?.lastName}
          </h1>
          <p className="text-neutral-500 mt-1">Code: {employee?.employeeCode} • {employee?.designationName || employee?.designationId}</p>
        </div>
      </div>

      <GlassCard className="p-6">
        <div className="mb-6 grid grid-cols-1 md:grid-cols-2">
          <div className="bg-brand-50 p-4 rounded-lg border border-brand-100 flex items-start gap-4">
            <div className="bg-brand-100 p-2 rounded-full mt-1">
              <Calendar className="w-5 h-5 text-brand-700" />
            </div>
            <div className="flex-1">
              <h3 className="text-sm font-semibold text-brand-900 mb-1">Effective Date</h3>
              <p className="text-xs text-brand-700 mb-3">When does this salary configuration take effect?</p>
              <Input
                type="date"
                value={formData.effectiveFrom ? formData.effectiveFrom.split('T')[0] : ''}
                onChange={(e) => setFormData({ ...formData, effectiveFrom: new Date(e.target.value).toISOString() })}
                required
              />
            </div>
          </div>
        </div>

        <SalaryPayrollStep 
          data={formData} 
          onChange={(newData: any) => setFormData(newData)} 
          errors={{}} 
        />
        
        <div className="mt-8 pt-6 border-t border-neutral-200 flex justify-end space-x-4">
          <AnimatedButton 
            variant="secondary" 
            onClick={() => navigate('/admin/employee-salary')}
            disabled={saving}
          >
            Cancel
          </AnimatedButton>
          <AnimatedButton 
            variant="primary" 
            onClick={handleSave}
            disabled={saving}
            isLoading={saving}
          >
            <Save className="w-4 h-4 mr-2" /> Save & Finalize
          </AnimatedButton>
        </div>
      </GlassCard>
    </div>
  );
}
