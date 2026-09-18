import React, { useState, useEffect } from 'react';
import { useAuth } from '../../../context/AuthContext';
import { companySalaryBankService, CompanySalaryBank } from '../../../services/companySalaryBankService';
import { Check, Edit, Plus, Trash2, Shield, AlertCircle, Building2 } from 'lucide-react';
import toast from 'react-hot-toast';

import { organizationApi } from '../../../services/organization.api';

export default function CompanyBankAccounts() {
  const [companies, setCompanies] = useState<any[]>([]);
  const [filterCompanyCode, setFilterCompanyCode] = useState<string>('all');
  const [banks, setBanks] = useState<CompanySalaryBank[]>([]);
  const [loading, setLoading] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);

  const [formData, setFormData] = useState<Partial<CompanySalaryBank>>({
    companyCode: '',
    accountHolderName: '',
    bankName: '',
    accountNumber: '',
    ifscCode: '',
    branchName: '',
    accountType: 'Current',
    status: 'Active',
    isPrimary: false,
  });

  useEffect(() => {
    loadCompanies();
  }, []);

  const loadCompanies = async () => {
    try {
      const resp: any = await organizationApi.getCompanies();
      const comps = resp.items || resp.data || resp;
      setCompanies(comps || []);
    } catch (error) {
      console.error(error);
      toast.error('Failed to load companies');
    }
  };

  useEffect(() => {
    loadBanks();
  }, [filterCompanyCode]);

  const loadBanks = async () => {
    try {
      setLoading(true);
      const data = await companySalaryBankService.getAll(filterCompanyCode === 'all' ? undefined : filterCompanyCode);
      setBanks(data || []);
    } catch (error: any) {
      toast.error('Failed to load company bank accounts');
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value, type } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? (e.target as HTMLInputElement).checked : value
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      if (editingId) {
        await companySalaryBankService.update(editingId, formData);
        toast.success('Bank account updated');
      } else {
        if (!formData.companyCode) {
          toast.error('Please select a company');
          return;
        }
        await companySalaryBankService.create(formData as any);
        toast.success('Bank account created');
      }
      setIsModalOpen(false);
      loadBanks();
    } catch (error: any) {
      toast.error(error.message || 'Failed to save bank account');
    }
  };

  const handleSetPrimary = async (id: string) => {
    try {
      await companySalaryBankService.setPrimary(id);
      toast.success('Primary account updated');
      loadBanks();
    } catch (error: any) {
      toast.error('Failed to update primary account');
    }
  };

  const handleEdit = (bank: CompanySalaryBank) => {
    setFormData(bank);
    setEditingId(bank._id!);
    setIsModalOpen(true);
  };

  const maskAccount = (account: string) => {
    if (!account) return '';
    if (account.length <= 4) return account;
    return 'X'.repeat(Math.max(0, account.length - 4)) + account.slice(-4);
  };

  return (
    <div className="p-6 max-w-6xl mx-auto space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
            <Building2 className="w-6 h-6 text-blue-600" />
            Company Salary Bank Accounts
          </h1>
          <p className="text-sm text-gray-500 mt-1">
            Manage the bank accounts used to fund employee salary transfers via Bank Export.
          </p>
        </div>
        <div className="flex items-center gap-4">
          <select
            value={filterCompanyCode}
            onChange={(e) => setFilterCompanyCode(e.target.value)}
            className="border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-blue-500 focus:border-blue-500"
          >
            <option value="all">All Companies</option>
            {companies.map(c => (
              <option key={c.code} value={c.code}>
                {c.name} - {c.code}
              </option>
            ))}
          </select>
          <button
            onClick={() => {
              setEditingId(null);
              setFormData({
                companyCode: filterCompanyCode === 'all' ? '' : filterCompanyCode,
                accountHolderName: '',
                bankName: '',
                accountNumber: '',
                ifscCode: '',
                branchName: '',
                accountType: 'Current',
                status: 'Active',
                isPrimary: false,
              });
              setIsModalOpen(true);
            }}
            className="flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
          >
            <Plus className="w-4 h-4" />
            Add Account
          </button>
        </div>
      </div>

      {loading ? (
        <div className="animate-pulse space-y-4">
          {[...Array(3)].map((_, i) => (
            <div key={i} className="h-20 bg-gray-100 rounded-lg" />
          ))}
        </div>
      ) : banks.length === 0 ? (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 text-center">
          <Shield className="w-12 h-12 text-blue-400 mx-auto mb-3" />
          <h3 className="text-lg font-medium text-blue-900">No Salary Accounts Found</h3>
          <p className="text-blue-700 mt-1 mb-4">
            You must configure at least one active primary bank account per company before you can use the Bank Export feature.
          </p>
          <button
            onClick={() => {
                setEditingId(null);
                setFormData({
                  companyCode: filterCompanyCode === 'all' ? '' : filterCompanyCode,
                  accountHolderName: '',
                  bankName: '',
                  accountNumber: '',
                  ifscCode: '',
                  branchName: '',
                  accountType: 'Current',
                  status: 'Active',
                  isPrimary: true,
                });
                setIsModalOpen(true);
            }}
            className="text-blue-600 font-medium hover:underline"
          >
            Create an account now
          </button>
        </div>
      ) : (
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
          <table className="w-full text-left text-sm">
            <thead className="bg-gray-50 border-b border-gray-200 text-gray-600">
              <tr>
                <th className="px-6 py-4 font-medium">Company</th>
                <th className="px-6 py-4 font-medium">Bank Details</th>
                <th className="px-6 py-4 font-medium">Account Details</th>
                <th className="px-6 py-4 font-medium">Status</th>
                <th className="px-6 py-4 font-medium text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {banks.map((bank) => {
                const comp = companies.find(c => c.code === bank.companyCode);
                return (
                <tr key={bank._id || bank.accountNumber || Math.random().toString()} className="hover:bg-gray-50">
                  <td className="px-6 py-4">
                    <div className="font-medium text-gray-900">{comp?.name || bank.companyCode}</div>
                    <div className="text-gray-500 text-xs">{bank.companyCode}</div>
                  </td>
                  <td className="px-6 py-4">
                    <div className="font-medium text-gray-900">{bank.bankName}</div>
                    <div className="text-gray-500">{bank.branchName || 'No branch'}</div>
                  </td>
                  <td className="px-6 py-4">
                    <div className="font-medium text-gray-900">{maskAccount(bank.accountNumber)}</div>
                    <div className="text-gray-500 font-mono text-xs mt-0.5">IFSC: {bank.ifscCode}</div>
                    <div className="text-gray-500 text-xs mt-0.5">{bank.accountHolderName}</div>
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex flex-col gap-2 items-start">
                      <span className={`px-2.5 py-1 rounded-full text-xs font-medium ${
                        bank.status === 'Active' ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-700'
                      }`}>
                        {bank.status}
                      </span>
                      {bank.isPrimary && (
                        <span className="px-2.5 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-700 flex items-center gap-1">
                          <Check className="w-3 h-3" /> Primary
                        </span>
                      )}
                    </div>
                  </td>
                  <td className="px-6 py-4 text-right">
                    <div className="flex justify-end gap-2">
                      {!bank.isPrimary && bank.status === 'Active' && (
                        <button
                          onClick={() => handleSetPrimary(bank._id!)}
                          className="text-xs text-blue-600 hover:text-blue-800 font-medium px-2 py-1 rounded border border-blue-200 hover:bg-blue-50"
                        >
                          Make Primary
                        </button>
                      )}
                      <button
                        onClick={() => handleEdit(bank)}
                        className="text-gray-400 hover:text-gray-600 p-1"
                        title="Edit Details"
                      >
                        <Edit className="w-4 h-4" />
                      </button>
                    </div>
                  </td>
                </tr>
              )})}
            </tbody>
          </table>
        </div>
      )}

      {isModalOpen && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl shadow-xl w-full max-w-xl overflow-hidden">
            <div className="px-6 py-4 border-b border-gray-200 flex justify-between items-center">
              <h2 className="text-lg font-bold text-gray-900">
                {editingId ? 'Edit Bank Account' : 'Add Bank Account'}
              </h2>
              <button
                onClick={() => setIsModalOpen(false)}
                className="text-gray-400 hover:text-gray-600 text-xl"
              >
                &times;
              </button>
            </div>
            
            <form onSubmit={handleSubmit} className="p-6 space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="col-span-2">
                  <label className="block text-sm font-medium text-gray-700 mb-1">Company *</label>
                  <select
                    name="companyCode"
                    value={formData.companyCode || ''}
                    onChange={handleInputChange}
                    disabled={!!editingId}
                    className="w-full border border-gray-300 rounded-md shadow-sm p-2 focus:ring-blue-500 focus:border-blue-500 disabled:bg-gray-100 disabled:text-gray-500"
                    required
                  >
                    <option value="">Select Company</option>
                    {companies.map(c => (
                      <option key={c.code} value={c.code}>
                        {c.name} - {c.code}
                      </option>
                    ))}
                  </select>
                </div>
                
                <div className="col-span-2">
                  <label className="block text-sm font-medium text-gray-700 mb-1">Account Holder Name</label>
                  <input
                    type="text"
                    name="accountHolderName"
                    value={formData.accountHolderName}
                    onChange={handleInputChange}
                    className="w-full border border-gray-300 rounded-md shadow-sm p-2 focus:ring-blue-500 focus:border-blue-500"
                    required
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Bank Name</label>
                  <input
                    type="text"
                    name="bankName"
                    value={formData.bankName}
                    onChange={handleInputChange}
                    className="w-full border border-gray-300 rounded-md shadow-sm p-2 focus:ring-blue-500 focus:border-blue-500"
                    required
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Branch Name</label>
                  <input
                    type="text"
                    name="branchName"
                    value={formData.branchName}
                    onChange={handleInputChange}
                    className="w-full border border-gray-300 rounded-md shadow-sm p-2 focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Account Number</label>
                  <input
                    type={editingId ? 'password' : 'text'}
                    name="accountNumber"
                    value={formData.accountNumber}
                    onChange={handleInputChange}
                    className="w-full border border-gray-300 rounded-md shadow-sm p-2 focus:ring-blue-500 focus:border-blue-500"
                    required
                  />
                  {editingId && (
                    <p className="text-xs text-gray-500 mt-1">Re-enter full account number to update.</p>
                  )}
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">IFSC Code</label>
                  <input
                    type="text"
                    name="ifscCode"
                    value={formData.ifscCode}
                    onChange={handleInputChange}
                    className="w-full border border-gray-300 rounded-md shadow-sm p-2 focus:ring-blue-500 focus:border-blue-500"
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Account Type</label>
                  <select
                    name="accountType"
                    value={formData.accountType}
                    onChange={handleInputChange}
                    className="w-full border border-gray-300 rounded-md shadow-sm p-2 focus:ring-blue-500 focus:border-blue-500"
                  >
                    <option value="Current">Current</option>
                    <option value="Savings">Savings</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Status</label>
                  <select
                    name="status"
                    value={formData.status}
                    onChange={handleInputChange}
                    className="w-full border border-gray-300 rounded-md shadow-sm p-2 focus:ring-blue-500 focus:border-blue-500"
                  >
                    <option value="Active">Active</option>
                    <option value="Inactive">Inactive</option>
                  </select>
                </div>
              </div>

              {!editingId && (
                <div className="flex items-center gap-2 mt-4">
                  <input
                    type="checkbox"
                    id="isPrimary"
                    name="isPrimary"
                    checked={formData.isPrimary}
                    onChange={handleInputChange}
                    className="rounded text-blue-600 focus:ring-blue-500"
                  />
                  <label htmlFor="isPrimary" className="text-sm text-gray-700">
                    Set as primary salary-sending account
                  </label>
                </div>
              )}
              
              <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3 flex gap-2 text-yellow-800 text-sm mt-4">
                <AlertCircle className="w-5 h-5 flex-shrink-0" />
                <p>This information will be included directly in the generated Bank Export CSV. Please verify all details.</p>
              </div>

              <div className="mt-6 flex justify-end gap-3 pt-4 border-t border-gray-200">
                <button
                  type="button"
                  onClick={() => setIsModalOpen(false)}
                  className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700"
                >
                  {editingId ? 'Save Changes' : 'Create Account'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
