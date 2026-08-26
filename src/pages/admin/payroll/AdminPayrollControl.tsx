import React, { useEffect, useMemo, useState } from 'react';
import { Building2, Calendar, Calculator, CheckCircle, ChevronRight, RefreshCw, Save, ShieldCheck } from 'lucide-react';
import { toast } from 'react-hot-toast';
import { useAuth } from '../../../context/AuthContext';
import { api } from '../../../lib/api';
import { organizationApi } from '../../../services/organization.api';
import { employeeApi } from '../../../services/employeeApi';
import { payrollCycleApi, AttendanceLedgerRow, PayrollCycle } from '../../../services/payrollCycleApi';
import { payrollReviewApi, PayrollRecord } from '../../../services/payrollReviewApi';

type CompanyOption = { id: string; name: string; code?: string };
type BranchOption = { id: string; name: string; companyId?: string };
type DeductionColumnKey = 'salaryAdvance' | 'tds' | 'otherAdvance' | 'labourWelfare' | 'professionalTax';

type AdjustmentDraft = {
  reimbursement: number;
  lta: number;
  salaryAdvance: number;
  tds: number;
  otherAdvance: number;
  labourWelfare: number;
  professionalTax: number;
};

type AdjustmentRecord = AdjustmentDraft & {
  employeeId: string;
  employeeName: string;
  employeeCode?: string;
  branchId?: string;
  branchName?: string;
};

const DEDUCTION_COLUMNS: Array<{ key: DeductionColumnKey; label: string; deductionType: string }> = [
  { key: 'salaryAdvance', label: 'Salary Advance', deductionType: 'Salary Advance' },
  { key: 'tds', label: 'TDS', deductionType: 'TDS' },
  { key: 'otherAdvance', label: 'Other Advance', deductionType: 'Other Advance' },
  { key: 'labourWelfare', label: 'Labour Welfare', deductionType: 'Labour Welfare' },
  { key: 'professionalTax', label: 'Professional Tax', deductionType: 'Professional Tax' },
];

const EMPTY_DRAFT: AdjustmentDraft = {
  reimbursement: 0,
  lta: 0,
  salaryAdvance: 0,
  tds: 0,
  otherAdvance: 0,
  labourWelfare: 0,
  professionalTax: 0,
};

function normalizeArray<T>(payload: unknown): T[] {
  if (Array.isArray(payload)) return payload as T[];
  if (payload && typeof payload === 'object') {
    const candidate = (payload as { data?: unknown; items?: unknown }).data ?? (payload as { data?: unknown; items?: unknown }).items ?? payload;
    return Array.isArray(candidate) ? (candidate as T[]) : [];
  }
  return [];
}

function toNumber(value: unknown): number {
  const parsed = typeof value === 'number' ? value : Number(value);
  return Number.isFinite(parsed) ? parsed : 0;
}

function getId(entity: any): string {
  return String(entity?.id || entity?._id || entity?.companyId || entity?.branchId || entity?.employeeId || '');
}

function formatCurrency(amount: number): string {
  return new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 2 }).format(amount || 0);
}

function employeeName(employee: any): string {
  return `${employee?.firstName || ''} ${employee?.lastName || ''}`.trim() || employee?.employeeCode || employee?.employeeId || 'Unnamed Employee';
}

function calcRowTotal(row: AdjustmentDraft): number {
  return row.reimbursement + row.lta + row.salaryAdvance + row.tds + row.otherAdvance + row.labourWelfare + row.professionalTax;
}

const AdminPayrollControl: React.FC = () => {
  const { user, hasPermission } = useAuth();

  const [companies, setCompanies] = useState<CompanyOption[]>([]);
  const [cycles, setCycles] = useState<PayrollCycle[]>([]);
  const [branches, setBranches] = useState<BranchOption[]>([]);
  const [employees, setEmployees] = useState<any[]>([]);
  const [attendanceLedger, setAttendanceLedger] = useState<AttendanceLedgerRow[]>([]);
  const [payrolls, setPayrolls] = useState<PayrollRecord[]>([]);
  const [selectedCompanyId, setSelectedCompanyId] = useState<string>('');
  const [selectedBranchId, setSelectedBranchId] = useState<string>('');
  const [selectedCycleId, setSelectedCycleId] = useState<string>('');
  const [loadingCompanies, setLoadingCompanies] = useState(false);
  const [loadingCycles, setLoadingCycles] = useState(false);
  const [loadingCompanyData, setLoadingCompanyData] = useState(false);
  const [loadingPayrolls, setLoadingPayrolls] = useState(false);
  const [savingAdjustments, setSavingAdjustments] = useState(false);
  const [processingPayroll, setProcessingPayroll] = useState(false);
  const [publishingPayroll, setPublishingPayroll] = useState(false);
  const [adjustments, setAdjustments] = useState<AdjustmentRecord[]>([]);
  const [adjustmentDrafts, setAdjustmentDrafts] = useState<Record<string, AdjustmentDraft>>({});
  const [deductionIndex, setDeductionIndex] = useState<Record<string, Record<string, any>>>({});
  const [currentCycle, setCurrentCycle] = useState<PayrollCycle | null>(null);

  const selectedCompany = useMemo(() => companies.find((company) => company.id === selectedCompanyId) || null, [companies, selectedCompanyId]);
  const selectedBranch = useMemo(() => branches.find((branch) => branch.id === selectedBranchId) || null, [branches, selectedBranchId]);

  useEffect(() => {
    const loadInitialData = async () => {
      setLoadingCompanies(true);
      setLoadingCycles(true);
      try {
        const [companyPayload, cyclePayload] = await Promise.all([
          organizationApi.getCompanies(),
          payrollCycleApi.getCycles(),
        ]);

        const companyList = normalizeArray<any>(companyPayload)
          .map((company) => ({ id: getId(company), name: company?.name || company?.companyName || 'Unnamed Company', code: company?.code }))
          .filter((company) => company.id);

        const cycleList = normalizeArray<PayrollCycle>(cyclePayload)
          .map((cycle) => ({ ...cycle, id: String((cycle as any).id || (cycle as any)._id || ''), processingStatus: cycle.processingStatus || 'DRAFT' }))
          .filter((cycle) => cycle.id);

        setCompanies(companyList);
        setCycles(cycleList);

        const defaultCompany = user?.companyId && companyList.some((company) => company.id === user.companyId)
          ? user.companyId
          : companyList[0]?.id || '';
        setSelectedCompanyId(defaultCompany);

        const defaultCycle = cycleList.find((cycle) => cycle.processingStatus === 'ATTENDANCE_FINALIZED') || cycleList[0] || null;
        if (defaultCycle) {
          setSelectedCycleId(defaultCycle.id);
          setCurrentCycle(defaultCycle);
        }
      } catch (error: any) {
        toast.error(error?.message || 'Failed to load payroll setup');
      } finally {
        setLoadingCompanies(false);
        setLoadingCycles(false);
      }
    };

    loadInitialData();
  }, [user?.companyId]);

  useEffect(() => {
    const selected = cycles.find((cycle) => cycle.id === selectedCycleId) || null;
    setCurrentCycle(selected);
  }, [cycles, selectedCycleId]);

  useEffect(() => {
    const loadCompanyScopedData = async () => {
      if (!selectedCompanyId) {
        setBranches([]);
        setEmployees([]);
        setAttendanceLedger([]);
        setAdjustments([]);
        setPayrolls([]);
        setAdjustmentDrafts({});
        setDeductionIndex({});
        return;
      }

      setLoadingCompanyData(true);
      try {
        const [branchResult, employeeResult] = await Promise.allSettled([
          organizationApi.getBranches(selectedCompanyId),
          employeeApi.getAllDirectoryEmployees(),
        ]);

        const branchPayload = branchResult.status === 'fulfilled' ? branchResult.value : [];
        if (branchResult.status === 'rejected') {
          console.error('Failed to load branches:', branchResult.reason);
          toast.error('Failed to load branches');
        }

        const employeePayload = employeeResult.status === 'fulfilled' ? employeeResult.value : [];
        if (employeeResult.status === 'rejected') {
          console.error('Failed to load employees:', employeeResult.reason);
          toast.error('Failed to load employees');
        }

        const branchList = normalizeArray<any>(branchPayload)
          .map((branch) => ({ id: getId(branch), name: branch?.name || 'Unnamed Branch', companyId: branch?.companyId }))
          .filter((branch) => branch.id);

        const employeeList = normalizeArray<any>(employeePayload)
          .filter((employee) => {
            const employeeCompanyId = employee?.companyId || employee?.employment?.companyId || employee?.employmentHistory?.companyId;
            return selectedCompanyId ? employeeCompanyId === selectedCompanyId : true;
          })
          .filter((employee) => !selectedBranchId || (employee?.branchId || employee?.employment?.branchId) === selectedBranchId);

        setBranches(branchList);
        setEmployees(employeeList);

        if (selectedBranchId && !branchList.some((branch) => branch.id === selectedBranchId)) {
          setSelectedBranchId('');
        }
      } catch (error: any) {
        toast.error(error?.message || 'Failed to load company data');
        setBranches([]);
        setEmployees([]);
      } finally {
        setLoadingCompanyData(false);
      }
    };

    loadCompanyScopedData();
  }, [selectedCompanyId]);

  useEffect(() => {
    const loadCycleScopedData = async () => {
      if (!selectedCompanyId || !selectedCycleId) {
        setAttendanceLedger([]);
        setAdjustments([]);
        setPayrolls([]);
        setAdjustmentDrafts({});
        setDeductionIndex({});
        return;
      }

      setLoadingPayrolls(true);
      try {
        const cycle = cycles.find((item) => item.id === selectedCycleId) || null;
        setCurrentCycle(cycle);

        const [attendanceResult, payrollResult, reimbursementResult, deductionResult] = await Promise.allSettled([
          payrollCycleApi.getAttendanceLedger(selectedCycleId, selectedCompanyId, selectedBranchId || undefined),
          payrollReviewApi.getPayrollsForCycle(selectedCycleId, selectedCompanyId),
          api.get(`/v2/payroll/admin/reimbursements?payrollCycleId=${selectedCycleId}&companyId=${selectedCompanyId}${selectedBranchId ? `&branchId=${selectedBranchId}` : ''}`),
          api.get(`/v2/payroll/admin/deductions?payrollCycleId=${selectedCycleId}&companyId=${selectedCompanyId}${selectedBranchId ? `&branchId=${selectedBranchId}` : ''}`),
        ]);

        const attendancePayload = attendanceResult.status === 'fulfilled' ? attendanceResult.value : [];
        const payrollPayload = payrollResult.status === 'fulfilled' ? payrollResult.value : [];
        const reimbursementPayload = reimbursementResult.status === 'fulfilled' ? reimbursementResult.value : [];
        const deductionPayload = deductionResult.status === 'fulfilled' ? deductionResult.value : [];

        if (attendanceResult.status === 'rejected') console.error('Failed to load attendance:', attendanceResult.reason);
        if (payrollResult.status === 'rejected') console.error('Failed to load payrolls:', payrollResult.reason);
        if (reimbursementResult.status === 'rejected') console.error('Failed to load reimbursements:', reimbursementResult.reason);
        if (deductionResult.status === 'rejected') console.error('Failed to load deductions:', deductionResult.reason);

        const attendanceList = normalizeArray<AttendanceLedgerRow>(attendancePayload);
        const payrollList = normalizeArray<PayrollRecord>(payrollPayload);
        const reimbursementList = normalizeArray<any>(reimbursementPayload);
        const deductionList = normalizeArray<any>(deductionPayload);

        setAttendanceLedger(attendanceList);
        setPayrolls(payrollList);

        const branchNameById = new Map(branches.map((branch) => [branch.id, branch.name]));
        const employeeById = new Map(
          employees.map((employee) => {
            const id = employee?.employeeId || employee?.id;
            return [String(id), employee];
          })
        );

        const rowMap = new Map<string, AdjustmentRecord>();
        const deductionMap: Record<string, Record<string, any>> = {};

        for (const employee of employees) {
          const empId = String(employee?.employeeId || employee?.id || '');
          if (!empId) continue;
          const branchId = String(employee?.branchId || employee?.employment?.branchId || '');
          rowMap.set(empId, {
            employeeId: empId,
            employeeName: employeeName(employee),
            employeeCode: employee?.employeeCode,
            branchId: branchId || undefined,
            branchName: branchNameById.get(branchId) || employee?.branchName || branchId || undefined,
            ...EMPTY_DRAFT,
          });
        }

        for (const claim of reimbursementList) {
          const empId = String(claim?.employeeId || '');
          if (!empId || !rowMap.has(empId)) continue;
          const current = rowMap.get(empId)!;
          const amount = toNumber(claim?.calculatedAmount ?? claim?.claimedAmount ?? claim?.amount);
          const label = `${String(claim?.claimType || claim?.description || '')} ${String(claim?.description || '')}`.toUpperCase();
          if (label.includes('LTA')) {
            current.lta += amount;
          } else {
            current.reimbursement += amount;
          }
        }

        for (const deduction of deductionList) {
          const empId = String(deduction?.employeeId || '');
          if (!empId || !rowMap.has(empId)) continue;
          const current = rowMap.get(empId)!;
          const deductionType = String(deduction?.deductionType || '').toUpperCase();
          const amount = toNumber(deduction?.amount);
          const key = deductionType.includes('SALARY')
            ? 'salaryAdvance'
            : deductionType.includes('TDS')
              ? 'tds'
              : deductionType.includes('OTHER')
                ? 'otherAdvance'
                : deductionType.includes('LABOUR') || deductionType.includes('LWF')
                  ? 'labourWelfare'
                  : deductionType.includes('PROFESSIONAL') || deductionType.includes('PT')
                    ? 'professionalTax'
                    : null;

          if (key) {
            current[key] += amount;
            deductionMap[empId] = deductionMap[empId] || {};
            deductionMap[empId][key] = deduction;
          }
        }

        setAdjustments(Array.from(rowMap.values()).sort((left, right) => left.employeeName.localeCompare(right.employeeName)));
        setAdjustmentDrafts(
          Array.from(rowMap.values()).reduce<Record<string, AdjustmentDraft>>((accumulator, row) => {
            accumulator[row.employeeId] = {
              reimbursement: row.reimbursement,
              lta: row.lta,
              salaryAdvance: row.salaryAdvance,
              tds: row.tds,
              otherAdvance: row.otherAdvance,
              labourWelfare: row.labourWelfare,
              professionalTax: row.professionalTax,
            };
            return accumulator;
          }, {})
        );
        setDeductionIndex(deductionMap);
      } catch (error: any) {
        toast.error(error?.message || 'Failed to load payroll cycle data');
        setAttendanceLedger([]);
        setAdjustments([]);
        setPayrolls([]);
        setAdjustmentDrafts({});
        setDeductionIndex({});
      } finally {
        setLoadingPayrolls(false);
      }
    };

    loadCycleScopedData();
  }, [selectedCompanyId, selectedBranchId, selectedCycleId, employees, branches, cycles]);

  const payrollMonth = useMemo(() => {
    if (!currentCycle?.startDate) return '';
    return currentCycle.startDate.slice(0, 7);
  }, [currentCycle?.startDate]);

  const handleDraftChange = (employeeId: string, key: DeductionColumnKey, value: string) => {
    const amount = Number(value);
    setAdjustmentDrafts((current) => ({
      ...current,
      [employeeId]: {
        ...(current[employeeId] || EMPTY_DRAFT),
        [key]: Number.isFinite(amount) ? amount : 0,
      },
    }));
  };

  const saveAdjustments = async (): Promise<boolean> => {
    if (!selectedCompanyId || !selectedCycleId) return;
    setSavingAdjustments(true);
    try {
      const saveJobs: Promise<unknown>[] = [];

      for (const row of adjustments) {
        const draft = adjustmentDrafts[row.employeeId] || EMPTY_DRAFT;
        for (const column of DEDUCTION_COLUMNS) {
          const amount = toNumber(draft[column.key]);
          const existing = deductionIndex[row.employeeId]?.[column.key];
          const payload = {
            companyId: selectedCompanyId,
            branchId: row.branchId || selectedBranchId || undefined,
            employeeId: row.employeeId,
            payrollCycleId: selectedCycleId,
            payrollPeriod: payrollMonth,
            deductionType: column.deductionType,
            amount,
            description: column.label,
          };

          if (amount > 0) {
            if (existing?._id) {
              saveJobs.push(api.put(`/v2/payroll/admin/deductions/${existing._id}?companyId=${selectedCompanyId}&payrollCycleId=${selectedCycleId}`, payload));
            } else {
              saveJobs.push(api.post(`/v2/payroll/admin/deductions?companyId=${selectedCompanyId}&payrollCycleId=${selectedCycleId}`, payload));
            }
          } else if (existing?._id) {
            saveJobs.push(api.delete(`/v2/payroll/admin/deductions/${existing._id}?companyId=${selectedCompanyId}&payrollCycleId=${selectedCycleId}`));
          }
        }
      }

      await Promise.all(saveJobs);
      toast.success('Adjustments saved');
      const refreshed = await api.get(`/v2/payroll/admin/deductions?payrollCycleId=${selectedCycleId}&companyId=${selectedCompanyId}${selectedBranchId ? `&branchId=${selectedBranchId}` : ''}`);
      const deductionList = normalizeArray<any>(refreshed);
      const deductionMap: Record<string, Record<string, any>> = {};
      for (const deduction of deductionList) {
        const empId = String(deduction?.employeeId || '');
        const deductionType = String(deduction?.deductionType || '').toUpperCase();
        const key = deductionType.includes('SALARY')
          ? 'salaryAdvance'
          : deductionType.includes('TDS')
            ? 'tds'
            : deductionType.includes('OTHER')
              ? 'otherAdvance'
              : deductionType.includes('LABOUR') || deductionType.includes('LWF')
                ? 'labourWelfare'
                : deductionType.includes('PROFESSIONAL') || deductionType.includes('PT')
                  ? 'professionalTax'
                  : null;
        if (!empId || !key) continue;
        deductionMap[empId] = deductionMap[empId] || {};
        deductionMap[empId][key] = deduction;
      }
      setDeductionIndex(deductionMap);
      return true;
    } catch (error: any) {
      toast.error(error?.message || 'Failed to save adjustments');
      return false;
    } finally {
      setSavingAdjustments(false);
    }
  };

  const recalculatePayroll = async () => {
    if (!selectedCompanyId || !selectedCycleId) {
      toast.error('Select a company and payroll cycle first');
      return;
    }

    setProcessingPayroll(true);
    try {
      const saved = await saveAdjustments();
      if (!saved) return;
      const summary = await payrollCycleApi.calculatePayroll(selectedCycleId, selectedCompanyId);
      toast.success(`Payroll calculated for ${summary?.successfullyCalculated ?? 0} employees`);
      const payrollList = await payrollReviewApi.getPayrollsForCycle(selectedCycleId, selectedCompanyId);
      setPayrolls(normalizeArray<PayrollRecord>(payrollList));
    } catch (error: any) {
      toast.error(error?.message || 'Failed to calculate payroll');
    } finally {
      setProcessingPayroll(false);
    }
  };

  const publishPayroll = async () => {
    if (!selectedCompanyId || !selectedCycleId) {
      toast.error('Select a company and payroll cycle first');
      return;
    }

    if (!window.confirm('Publish payroll for the selected company?')) return;

    setPublishingPayroll(true);
    try {
      const response = await payrollCycleApi.publishCycle(selectedCycleId, selectedCompanyId);
      toast.success(`Published ${response?.publishedPayslips ?? 0} payslips`);
    } catch (error: any) {
      toast.error(error?.message || 'Failed to publish payroll');
    } finally {
      setPublishingPayroll(false);
    }
  };

  const updateCycleStatus = async (status: string) => {
    if (!selectedCycleId) return;
    try {
      await payrollCycleApi.updateStatus(selectedCycleId, status);
      toast.success(`Cycle moved to ${status}`);
      const refreshed = await payrollCycleApi.getCycles();
      const cycleList = normalizeArray<PayrollCycle>(refreshed).map((cycle) => ({ ...cycle, id: String((cycle as any).id || (cycle as any)._id || '') }));
      setCycles(cycleList);
      setCurrentCycle(cycleList.find((cycle) => cycle.id === selectedCycleId) || null);
    } catch (error: any) {
      toast.error(error?.message || 'Failed to update cycle status');
    }
  };

  const currentCycleStatus = currentCycle?.processingStatus || 'DRAFT';

  const companyOptions = companies.map((company) => ({ value: company.id, label: company.code ? `${company.name} (${company.code})` : company.name }));
  const cycleOptions = cycles.map((cycle) => ({ value: cycle.id, label: `${cycle.name} · ${cycle.processingStatus}` }));

  return (
    <div className="min-h-screen bg-slate-50/70">
      <div className="mx-auto max-w-7xl space-y-6 p-4 sm:p-6 lg:p-8">
        <div className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
          <div className="flex flex-col gap-6 lg:flex-row lg:items-end lg:justify-between">
            <div>
              <p className="text-sm font-medium uppercase tracking-[0.24em] text-slate-500">Payroll Control</p>
              <h1 className="mt-2 text-3xl font-semibold text-slate-900">Company-first payroll processing</h1>
              <p className="mt-2 max-w-3xl text-sm text-slate-600">
                Select a company, choose a global payroll cycle, review attendance, edit employee deductions, calculate payroll, and publish only after review.
              </p>
            </div>
            <div className="grid gap-3 sm:grid-cols-3">
              <div className="rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3">
                <p className="text-xs uppercase tracking-[0.2em] text-slate-500">Current cycle state</p>
                <p className="mt-1 text-sm font-semibold text-slate-900">{currentCycleStatus}</p>
              </div>
              <div className="rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3">
                <p className="text-xs uppercase tracking-[0.2em] text-slate-500">Selected company</p>
                <p className="mt-1 text-sm font-semibold text-slate-900">{selectedCompany?.name || 'None'}</p>
              </div>
              <div className="rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3">
                <p className="text-xs uppercase tracking-[0.2em] text-slate-500">Selected cycle</p>
                <p className="mt-1 text-sm font-semibold text-slate-900">{currentCycle?.name || 'None'}</p>
              </div>
            </div>
          </div>

          <div className="mt-6 grid gap-4 lg:grid-cols-3">
            <label className="rounded-2xl border border-slate-200 bg-slate-50 p-4">
              <span className="mb-2 flex items-center gap-2 text-sm font-medium text-slate-700"><Building2 className="h-4 w-4" /> Company</span>
              <select
                value={selectedCompanyId}
                onChange={(event) => {
                  setSelectedCompanyId(event.target.value);
                  setSelectedBranchId('');
                }}
                className="w-full rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm text-slate-900 shadow-sm outline-none focus:border-slate-400"
              >
                <option value="">Select Company</option>
                {companyOptions.map((company) => (
                  <option key={company.value} value={company.value}>
                    {company.label}
                  </option>
                ))}
              </select>
            </label>

            <label className="rounded-2xl border border-slate-200 bg-slate-50 p-4">
              <span className="mb-2 flex items-center gap-2 text-sm font-medium text-slate-700"><Calendar className="h-4 w-4" /> Payroll Cycle</span>
              <select
                value={selectedCycleId}
                onChange={(event) => setSelectedCycleId(event.target.value)}
                className="w-full rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm text-slate-900 shadow-sm outline-none focus:border-slate-400"
              >
                <option value="">Select Payroll Cycle</option>
                {cycleOptions.map((cycle) => (
                  <option key={cycle.value} value={cycle.value}>
                    {cycle.label}
                  </option>
                ))}
              </select>
            </label>

            <label className="rounded-2xl border border-slate-200 bg-slate-50 p-4">
              <span className="mb-2 flex items-center gap-2 text-sm font-medium text-slate-700"><Building2 className="h-4 w-4" /> Branch</span>
              <select
                value={selectedBranchId}
                onChange={(event) => setSelectedBranchId(event.target.value)}
                className="w-full rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm text-slate-900 shadow-sm outline-none focus:border-slate-400"
              >
                <option value="">All Branches</option>
                {branches.map((branch) => (
                  <option key={branch.id} value={branch.id}>
                    {branch.name}
                  </option>
                ))}
              </select>
            </label>
          </div>

          <div className="mt-6 flex flex-wrap gap-3">
            <button
              type="button"
              onClick={() => updateCycleStatus('ATTENDANCE_FINALIZED')}
              disabled={!selectedCycleId}
              className="inline-flex items-center gap-2 rounded-xl border border-slate-200 bg-white px-4 py-2 text-sm font-medium text-slate-700 shadow-sm transition hover:border-slate-300 disabled:cursor-not-allowed disabled:opacity-50"
            >
              <ShieldCheck className="h-4 w-4" /> Finalize Attendance
            </button>
            <button
              type="button"
              onClick={saveAdjustments}
              disabled={!selectedCompanyId || !selectedCycleId || savingAdjustments}
              className="inline-flex items-center gap-2 rounded-xl border border-slate-200 bg-white px-4 py-2 text-sm font-medium text-slate-700 shadow-sm transition hover:border-slate-300 disabled:cursor-not-allowed disabled:opacity-50"
            >
              <Save className="h-4 w-4" /> {savingAdjustments ? 'Saving...' : 'Save Adjustments'}
            </button>
            <button
              type="button"
              onClick={recalculatePayroll}
              disabled={!selectedCompanyId || !selectedCycleId || processingPayroll}
              className="inline-flex items-center gap-2 rounded-xl bg-slate-900 px-4 py-2 text-sm font-medium text-white shadow-sm transition hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-50"
            >
              <Calculator className="h-4 w-4" /> {processingPayroll ? 'Calculating...' : 'Calculate Payroll'}
            </button>
            <button
              type="button"
              onClick={() => updateCycleStatus('ADMIN_REVIEW')}
              disabled={currentCycleStatus !== 'CALCULATED'}
              className="inline-flex items-center gap-2 rounded-xl border border-slate-200 bg-white px-4 py-2 text-sm font-medium text-slate-700 shadow-sm transition hover:border-slate-300 disabled:cursor-not-allowed disabled:opacity-50"
            >
              <ChevronRight className="h-4 w-4" /> Send to Review
            </button>
            <button
              type="button"
              onClick={() => updateCycleStatus('FINALIZED')}
              disabled={currentCycleStatus !== 'ADMIN_REVIEW'}
              className="inline-flex items-center gap-2 rounded-xl border border-slate-200 bg-white px-4 py-2 text-sm font-medium text-slate-700 shadow-sm transition hover:border-slate-300 disabled:cursor-not-allowed disabled:opacity-50"
            >
              <CheckCircle className="h-4 w-4" /> Finalize Payroll
            </button>
            <button
              type="button"
              onClick={publishPayroll}
              disabled={currentCycleStatus !== 'FINALIZED' || publishingPayroll}
              className="inline-flex items-center gap-2 rounded-xl bg-emerald-600 px-4 py-2 text-sm font-medium text-white shadow-sm transition hover:bg-emerald-500 disabled:cursor-not-allowed disabled:opacity-50"
            >
              <RefreshCw className="h-4 w-4" /> {publishingPayroll ? 'Publishing...' : 'Publish'}
            </button>
          </div>
        </div>

        <section className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
          <div className="flex items-center justify-between gap-3">
            <div>
              <h2 className="text-lg font-semibold text-slate-900">Attendance Ledger</h2>
              <p className="text-sm text-slate-500">
                Company and cycle specific employee attendance for {currentCycle?.name || 'the selected cycle'}.
              </p>
            </div>
            <div className="text-sm text-slate-500">
              {loadingCompanyData || loadingCompanies || loadingCycles ? 'Loading...' : `${attendanceLedger.length} employees`}
            </div>
          </div>

          <div className="mt-4 overflow-x-auto rounded-2xl border border-slate-200">
            <table className="min-w-full divide-y divide-slate-200 text-sm">
              <thead className="bg-slate-50 text-left text-xs uppercase tracking-[0.16em] text-slate-500">
                <tr>
                  <th className="px-4 py-3">Employee</th>
                  <th className="px-4 py-3">Employee Code</th>
                  <th className="px-4 py-3">Branch</th>
                  <th className="px-4 py-3 text-right">Present Days</th>
                  <th className="px-4 py-3 text-right">Absent Days</th>
                  <th className="px-4 py-3 text-right">Paid Leave</th>
                  <th className="px-4 py-3 text-right">LOP</th>
                  <th className="px-4 py-3 text-right">Working Days</th>
                  <th className="px-4 py-3 text-right">Holiday</th>
                  <th className="px-4 py-3 text-right">Weekly Off</th>
                  <th className="px-4 py-3">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 bg-white">
                {attendanceLedger.length === 0 ? (
                  <tr>
                    <td className="px-4 py-8 text-center text-slate-500" colSpan={11}>
                      No attendance ledger loaded yet.
                    </td>
                  </tr>
                ) : (
                  attendanceLedger.map((row) => (
                    <tr key={row.employeeId} className="hover:bg-slate-50/60">
                      <td className="px-4 py-3 font-medium text-slate-900">{row.employeeName}</td>
                      <td className="px-4 py-3 text-slate-600">{row.employeeCode || '-'}</td>
                      <td className="px-4 py-3 text-slate-600">{row.branchName || row.branchId || '-'}</td>
                      <td className="px-4 py-3 text-right text-slate-900">{row.presentDays}</td>
                      <td className="px-4 py-3 text-right text-slate-900">{row.absentDays}</td>
                      <td className="px-4 py-3 text-right text-slate-900">{row.paidLeave}</td>
                      <td className="px-4 py-3 text-right text-slate-900">{row.lop}</td>
                      <td className="px-4 py-3 text-right text-slate-900">{row.workingDays}</td>
                      <td className="px-4 py-3 text-right text-slate-900">{row.holiday}</td>
                      <td className="px-4 py-3 text-right text-slate-900">{row.weeklyOff}</td>
                      <td className="px-4 py-3 text-slate-700">{row.attendanceStatus}</td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </section>

        <section className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
          <div className="flex items-center justify-between gap-3">
            <div>
              <h2 className="text-lg font-semibold text-slate-900">Employee-wise Salary Adjustments</h2>
              <p className="text-sm text-slate-500">
                Reimbursement and LTA are additions. Manual salary advance, TDS, other advance, labour welfare and professional tax are deductions.
              </p>
            </div>
            <div className="text-sm text-slate-500">
              {adjustments.length === 0 ? 'No employees loaded' : `${adjustments.length} adjustment rows`}
            </div>
          </div>

          <div className="mt-4 overflow-x-auto rounded-2xl border border-slate-200">
            <table className="min-w-[1400px] divide-y divide-slate-200 text-sm">
              <thead className="bg-slate-50 text-left text-xs uppercase tracking-[0.16em] text-slate-500">
                <tr>
                  <th className="px-4 py-3">Sl. No</th>
                  <th className="px-4 py-3">Employee</th>
                  <th className="px-4 py-3 text-right">Reimbursement</th>
                  <th className="px-4 py-3 text-right">LTA</th>
                  {DEDUCTION_COLUMNS.map((column) => (
                    <th key={column.key} className="px-4 py-3 text-right">
                      {column.label}
                    </th>
                  ))}
                  <th className="px-4 py-3 text-right">Total</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 bg-white">
                {adjustments.length === 0 ? (
                  <tr>
                    <td className="px-4 py-8 text-center text-slate-500" colSpan={9}>
                      Load a company and payroll cycle to view adjustment rows.
                    </td>
                  </tr>
                ) : (
                  adjustments.map((row, index) => {
                    const draft = adjustmentDrafts[row.employeeId] || row;
                    return (
                      <tr key={row.employeeId} className="hover:bg-slate-50/60">
                        <td className="px-4 py-3 text-slate-500">{index + 1}</td>
                        <td className="px-4 py-3">
                          <div className="font-medium text-slate-900">{row.employeeName}</div>
                          <div className="text-xs text-slate-500">{row.employeeCode || row.employeeId}</div>
                        </td>
                        <td className="px-4 py-3 text-right text-slate-900">{formatCurrency(row.reimbursement)}</td>
                        <td className="px-4 py-3 text-right text-slate-900">{formatCurrency(row.lta)}</td>
                        {DEDUCTION_COLUMNS.map((column) => (
                          <td key={column.key} className="px-4 py-3 text-right">
                            <input
                              type="number"
                              min="0"
                              step="0.01"
                              value={draft[column.key]}
                              onChange={(event) => handleDraftChange(row.employeeId, column.key, event.target.value)}
                              className="w-28 rounded-lg border border-slate-200 bg-white px-2 py-1 text-right text-sm text-slate-900 outline-none focus:border-slate-400"
                            />
                          </td>
                        ))}
                        <td className="px-4 py-3 text-right font-semibold text-slate-900">{formatCurrency(calcRowTotal(draft))}</td>
                      </tr>
                    );
                  })
                )}
              </tbody>
            </table>
          </div>
        </section>

        <section className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
          <div className="flex items-center justify-between gap-3">
            <div>
              <h2 className="text-lg font-semibold text-slate-900">Calculated Payroll Review</h2>
              <p className="text-sm text-slate-500">Review calculated payroll before finalization and publish.</p>
            </div>
            <button
              type="button"
              onClick={() => payrollReviewApi.getPayrollsForCycle(selectedCycleId, selectedCompanyId).then((data) => setPayrolls(normalizeArray<PayrollRecord>(data))).catch((error: any) => toast.error(error?.message || 'Failed to refresh payrolls'))}
              disabled={!selectedCompanyId || !selectedCycleId}
              className="inline-flex items-center gap-2 rounded-xl border border-slate-200 bg-white px-4 py-2 text-sm font-medium text-slate-700 shadow-sm transition hover:border-slate-300 disabled:cursor-not-allowed disabled:opacity-50"
            >
              <RefreshCw className="h-4 w-4" /> Refresh
            </button>
          </div>

          <div className="mt-4 overflow-x-auto rounded-2xl border border-slate-200">
            <table className="min-w-full divide-y divide-slate-200 text-sm">
              <thead className="bg-slate-50 text-left text-xs uppercase tracking-[0.16em] text-slate-500">
                <tr>
                  <th className="px-4 py-3">Employee</th>
                  <th className="px-4 py-3 text-right">Gross Earnings</th>
                  <th className="px-4 py-3 text-right">Total Deductions</th>
                  <th className="px-4 py-3 text-right">Net Pay</th>
                  <th className="px-4 py-3">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 bg-white">
                {payrolls.length === 0 ? (
                  <tr>
                    <td className="px-4 py-8 text-center text-slate-500" colSpan={5}>
                      No payroll calculated yet for this company and cycle.
                    </td>
                  </tr>
                ) : (
                  payrolls.map((payroll) => (
                    <tr key={payroll._id} className="hover:bg-slate-50/60">
                      <td className="px-4 py-3 font-medium text-slate-900">{payroll.employeeName || payroll.employeeId}</td>
                      <td className="px-4 py-3 text-right text-slate-900">{formatCurrency(payroll.grossEarnings)}</td>
                      <td className="px-4 py-3 text-right text-slate-900">{formatCurrency(payroll.grossDeductions)}</td>
                      <td className="px-4 py-3 text-right font-semibold text-slate-900">{formatCurrency(payroll.netPay)}</td>
                      <td className="px-4 py-3 text-slate-700">{payroll.status}</td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </section>

        {(loadingCompanies || loadingCycles || loadingCompanyData || loadingPayrolls) && (
          <div className="rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-600 shadow-sm">
            Loading payroll data for the selected company and cycle...
          </div>
        )}

        {!hasPermission('payroll.calculate') && (
          <div className="rounded-2xl border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-900">
            Your current role does not expose payroll calculation permission.
          </div>
        )}
      </div>
    </div>
  );
};

export default AdminPayrollControl;
