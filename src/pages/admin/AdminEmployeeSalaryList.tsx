import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { employeeApi } from '../../services/employeeApi';
import { GlassCard, AnimatedButton } from '../../components/ui';
import { toast } from 'react-hot-toast';
import { Settings, Search } from 'lucide-react';

export default function AdminEmployeeSalaryList() {
  const navigate = useNavigate();
  const [employees, setEmployees] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    fetchEmployees();
  }, []);

  const fetchEmployees = async () => {
    setLoading(true);
    try {
      const res = await employeeApi.getEmployees();
      setEmployees(res?.data || res || []);
    } catch (e) {
      console.error(e);
      toast.error('Failed to load employees');
    } finally {
      setLoading(false);
    }
  };

  const filteredEmployees = employees.filter((emp: any) => 
    emp.firstName?.toLowerCase().includes(searchQuery.toLowerCase()) ||
    emp.lastName?.toLowerCase().includes(searchQuery.toLowerCase()) ||
    emp.employeeCode?.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-neutral-900">Employee Salary Configuration</h1>
          <p className="text-neutral-500 mt-1">Manage and configure salary structures for employees</p>
        </div>
      </div>

      <GlassCard className="p-6">
        <div className="mb-4 relative max-w-md">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <Search className="h-5 w-5 text-neutral-400" />
            </div>
            <input
              type="text"
              placeholder="Search by name or code..."
              className="block w-full pl-10 pr-3 py-2 border border-neutral-300 rounded-md leading-5 bg-white placeholder-neutral-500 focus:outline-none focus:placeholder-neutral-400 focus:ring-1 focus:ring-brand-500 focus:border-brand-500 sm:text-sm"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
        </div>
        
        {loading ? (
          <div className="text-center py-10 text-neutral-500">Loading employees...</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm text-left">
              <thead className="bg-neutral-50 text-neutral-600 font-medium border-b border-neutral-200">
                <tr>
                  <th className="px-4 py-3">Code</th>
                  <th className="px-4 py-3">Employee Name</th>
                  <th className="px-4 py-3">Department</th>
                  <th className="px-4 py-3">Designation</th>
                  <th className="px-4 py-3">Status</th>
                  <th className="px-4 py-3 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-neutral-200">
                {filteredEmployees.map((emp) => (
                  <tr key={emp.id || emp._id} className="hover:bg-neutral-50 transition-colors">
                    <td className="px-4 py-3">{emp.employeeCode}</td>
                    <td className="px-4 py-3 font-medium text-neutral-900">
                      {emp.firstName} {emp.lastName}
                    </td>
                    <td className="px-4 py-3">{emp.departmentName || emp.departmentId || '-'}</td>
                    <td className="px-4 py-3">{emp.designationName || emp.designationId || '-'}</td>
                    <td className="px-4 py-3">
                      <span className="px-2 py-1 bg-green-100 text-green-700 rounded-full text-xs font-medium">
                        {emp.employmentStatus || 'Active'}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-right">
                      <AnimatedButton 
                        variant="secondary"
                        size="sm"
                        onClick={() => navigate(`/admin/employee-salary/${emp.id || emp._id}`)}
                      >
                        <Settings className="w-4 h-4 mr-2" /> Configure
                      </AnimatedButton>
                    </td>
                  </tr>
                ))}
                {filteredEmployees.length === 0 && (
                  <tr>
                    <td colSpan={6} className="px-4 py-8 text-center text-neutral-500">
                      No employees found.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        )}
      </GlassCard>
    </div>
  );
}
