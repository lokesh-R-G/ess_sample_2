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
type AdjustmentDraft = {
  reimbursement: number;
  lta: number;
  [key: string]: number;
};

type AdjustmentRecord = AdjustmentDraft & {
  employeeId: string;
  employeeName: string;
  employeeCode?: string;
  branchId?: string;
  branchName?: string;
};

const EMPTY_DRAFT: AdjustmentDraft = {
  reimbursement: 0,
  lta: 0,
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
  const [exportingCSV, setExportingCSV] = useState(false);
  const [exportingXLSX, setExportingXLSX] = useState(false);
  const [adjustments, setAdjustments] = useState<AdjustmentRecord[]>([]);
  const [adjustmentDrafts, setAdjustmentDrafts] = useState<Record<string, AdjustmentDraft>>({});
  const [deductionIndex, setDeductionIndex] = useState<Record<string, Record<string, any>>>({});
  const [currentCycle, setCurrentCycle] = useState<PayrollCycle | null>(null);
  const [currentCompanyRun, setCurrentCompanyRun] = useState<any>(null);
  const [manualComponents, setManualComponents] = useState<any[]>([]);
  const [activeLegacyColumns, setActiveLegacyColumns] = useState<string[]>([]);

  const manualEarnings = useMemo(() => manualComponents.filter(c => c.componentType === 'Earning'), [manualComponents]);
  const manualDeductions = useMemo(() => manualComponents.filter(c => c.componentType === 'Deduction'), [manualComponents]);

  const selectedCompany = useMemo(() => companies.find((company) => company.id === selectedCompanyId) || null, [companies, selectedCompanyId]);
  const selectedBranch = useMemo(() => branches.find((branch) => branch.id === selectedBranchId) || null, [branches, selectedBranchId]);

  useEffect(() => {
    const loadInitialData = async () => {
      setLoadingCompanies(true);
      setLoadingCycles(true);
      try {
        const [companyPayload, cyclePayload, componentsPayload] = await Promise.all([
          organizationApi.getCompanies(),
          payrollCycleApi.getCycles(),
          api.get('/v2/organization/salary-components?inputMode=MANUAL')
        ]);

        const companyList = normalizeArray<any>(companyPayload)
          .map((company) => ({ id: getId(company), name: company?.name || company?.companyName || 'Unnamed Company', code: company?.code }))
          .filter((company) => company.id);

        const cycleList = normalizeArray<PayrollCycle>(cyclePayload)
          .map((cycle) => ({ ...cycle, id: String((cycle as any).id || (cycle as any)._id || ''), processingStatus: cycle.processingStatus || 'DRAFT' }))
          .filter((cycle) => cycle.id);

        const componentsList = normalizeArray<any>(componentsPayload)
          .map((comp) => ({ ...comp, id: getId(comp) }))
          .filter(c => c.id && c.isActive !== false);

        setCompanies(companyList);
        setCycles(cycleList);
        setManualComponents(componentsList);

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

        const detailedCycle = await payrollCycleApi.getCycle(selectedCycleId);
        setCurrentCompanyRun(detailedCycle?.companies?.find((c: any) => c.companyId === selectedCompanyId) || null);

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

        const legacyColumns = new Set<string>();

        for (const deduction of deductionList) {
          const empId = String(deduction?.employeeId || '');
          if (!empId || !rowMap.has(empId)) continue;
          const current = rowMap.get(empId)!;
          
          let compId = deduction?.componentId;
          const deductionType = String(deduction?.deductionType || '');
          
          if (!compId && deductionType) {
             const nameMatch = manualComponents.find(c => (c.name || '').toLowerCase() === deductionType.toLowerCase());
             if (nameMatch) {
               compId = nameMatch.id;
             } else {
               compId = `legacy_${deductionType}`;
               legacyColumns.add(deductionType);
             }
          }

          const amount = toNumber(deduction?.amount);
          if (compId) {
            current[compId] = (current[compId] || 0) + amount;
            deductionMap[empId] = deductionMap[empId] || {};
            deductionMap[empId][compId] = deduction;
          }
        }
        setActiveLegacyColumns(Array.from(legacyColumns));

        setAdjustments(Array.from(rowMap.values()).sort((left, right) => left.employeeName.localeCompare(right.employeeName)));
        setAdjustmentDrafts(
          Array.from(rowMap.values()).reduce<Record<string, AdjustmentDraft>>((accumulator, row) => {
            const draft: AdjustmentDraft = { reimbursement: row.reimbursement, lta: row.lta };
            for (const c of manualComponents) draft[c.id] = row[c.id] || 0;
            for (const l of legacyColumns) draft[`legacy_${l}`] = row[`legacy_${l}`] || 0;
            accumulator[row.employeeId] = draft;
            return accumulator;
          }, {})
        );
        setDeductionIndex(deductionMap);
      } catch (error: any) {
        toast.error(error?.message || 'Failed to load payroll cycle data');
        setAttendanceLedger([]);
        setAdjustments([]);
        setAdjustments([]);
        setPayrolls([]);
        setAdjustmentDrafts({});
        setDeductionIndex({});
        setCurrentCompanyRun(null);
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

  const handleDraftChange = (employeeId: string, key: string, value: string) => {
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
    if (!selectedCompanyId || !selectedCycleId) return false;
    
    // Explicitly fail if no payrollRunId exists
    if (!currentCompanyRun?.id) {
      toast.error('Payroll Run not initialized. Cannot save adjustments.');
      return false;
    }
    
    setSavingAdjustments(true);
    try {
      const saveJobs: Promise<unknown>[] = [];

      for (const row of adjustments) {
        const draft = adjustmentDrafts[row.employeeId] || EMPTY_DRAFT;
        
        const processItems: Array<{
          key: string;
          componentId?: string;
          adjustmentType: 'EARNING' | 'DEDUCTION';
          deductionType: string;
          description: string;
        }> = [];

        for (const c of manualEarnings) {
          processItems.push({
            key: c.id,
            componentId: c.id,
            adjustmentType: 'EARNING',
            deductionType: c.name,
            description: c.name
          });
        }

        for (const c of manualDeductions) {
          processItems.push({
            key: c.id,
            componentId: c.id,
            adjustmentType: 'DEDUCTION',
            deductionType: c.name,
            description: c.name
          });
        }

        for (const l of activeLegacyColumns) {
          processItems.push({
            key: `legacy_${l}`,
            componentId: undefined,
            adjustmentType: 'DEDUCTION',
            deductionType: l,
            description: l
          });
        }

        for (const item of processItems) {
          const amount = toNumber(draft[item.key]);
          const existing = deductionIndex[row.employeeId]?.[item.key];
          
          if (amount === 0 && !existing) continue;

          const payload = {
            companyId: selectedCompanyId,
            branchId: row.branchId || selectedBranchId || undefined,
            employeeId: row.employeeId,
            payrollCycleId: selectedCycleId,
            payrollRunId: currentCompanyRun.id,
            payrollPeriod: payrollMonth,
            componentId: item.componentId,
            adjustmentType: item.adjustmentType,
            deductionType: item.deductionType,
            amount,
            description: item.description,
          };

          console.log('[PAYROLL ADJUSTMENT SAVE PAYLOAD]', payload);

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
        if (!empId) continue;
        let compId = deduction?.componentId;
        const deductionType = String(deduction?.deductionType || '');
        
        if (!compId && deductionType) {
           const nameMatch = manualComponents.find(c => (c.name || '').toLowerCase() === deductionType.toLowerCase());
           if (nameMatch) {
             compId = nameMatch.id;
           } else {
             compId = `legacy_${deductionType}`;
           }
        }
        
        if (compId) {
           deductionMap[empId] = deductionMap[empId] || {};
           deductionMap[empId][compId] = deduction;
        }
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
      const detailedCycle = await payrollCycleApi.getCycle(selectedCycleId);
      setCurrentCompanyRun(detailedCycle?.companies?.find((c: any) => c.companyId === selectedCompanyId) || null);
    } catch (error: any) {
      toast.error(error?.message || 'Failed to calculate payroll');
      try {
        const detailedCycle = await payrollCycleApi.getCycle(selectedCycleId);
        setCurrentCompanyRun(detailedCycle?.companies?.find((c: any) => c.companyId === selectedCompanyId) || null);
      } catch (e) {}
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

  const exportBankCSV = async () => {
    if (!selectedCompanyId || !selectedCycleId) {
      toast.error('Select a company and payroll cycle first');
      return;
    }

    setExportingCSV(true);
    try {
      const csvContent = await payrollCycleApi.exportCsv(selectedCycleId, selectedCompanyId);
      
      const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.setAttribute('href', url);
      link.setAttribute('download', `bank_export_${selectedCycleId}_${selectedCompanyId}.csv`);
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      
      toast.success('Bank export downloaded successfully');
    } catch (error: any) {
      toast.error(error?.message || 'Failed to export bank file');
    } finally {
      setExportingCSV(false);
    }
  };

  const exportPayrollXLSX = async () => {
    const runId = getId(currentCompanyRun);
    if (!runId) {
      toast.error('No payroll run available. Please calculate payroll first.');
      return;
    }

    setExportingXLSX(true);
    try {
      const response = await api.get(`/v2/payroll/runs/${runId}/export/payroll`, {
        responseType: 'raw'
      }) as Response;
      
      let filename = `Payroll_Export_${runId}.xlsx`;
      const disposition = response.headers.get('content-disposition');
      if (disposition && disposition.includes('filename="')) {
        const matches = /filename="([^"]+)"/.exec(disposition);
        if (matches != null && matches[1]) { 
          filename = matches[1];
        }
      }

      const blob = await response.blob();
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.setAttribute('href', url);
      link.setAttribute('download', filename);
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
      
      toast.success('Payroll export downloaded successfully');
    } catch (error: any) {
      toast.error(error?.message || 'Failed to export payroll file');
    } finally {
      setExportingXLSX(false);
    }
  };

  
  /*const exportPF = async () => {
    const runId = currentCompanyRun?.id || currentCompanyRun?._id;
    if (!runId) {
      toast.error('No payroll run available.');
      return;
    }
    try {
      const response = await api.get(`/v2/payroll/admin/export/pf/${runId}`, {
        responseType: 'raw'
      }) as Response;
      
      let filename = `PF_Export_${runId}.txt`;
      const disposition = response.headers.get('content-disposition');
      if (disposition && disposition.includes('filename="')) {
        const matches = /filename="([^"]+)"/.exec(disposition);
        if (matches != null && matches[1]) { 
          filename = matches[1];
        }
      }

      const blob = await response.blob();
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.setAttribute('href', url);
      link.setAttribute('download', filename);
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
      
      toast.success('PF export downloaded successfully');
    } catch (error: any) {
      toast.error(error?.message || 'Failed to export PF file');
    }
  };

  const exportESI = async () => {
    const runId = currentCompanyRun?.id || currentCompanyRun?._id;
    if (!runId) {
      toast.error('No payroll run available.');
      return;
    }
    try {
      const response = await api.get(`/v2/payroll/admin/export/esi/${runId}`, {
        responseType: 'raw'
      }) as Response;
      
      let filename = `ESI_Export_${runId}.csv`;
      const disposition = response.headers.get('content-disposition');
      if (disposition && disposition.includes('filename="')) {
        const matches = /filename="([^"]+)"/.exec(disposition);
        if (matches != null && matches[1]) { 
          filename = matches[1];
        }
      }

      const blob = await response.blob();
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.setAttribute('href', url);
      link.setAttribute('download', filename);
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
      
      toast.success('ESI export downloaded successfully');
    } catch (error: any) {
      toast.error(error?.message || 'Failed to export ESI file');
    }
  };*/

  const exportPF = async () => {
    const runId = currentCompanyRun?.id || currentCompanyRun?._id;
    if (!runId) {
      toast.error('No payroll run available.');
      return;
    }
    try {
      const response = await api.get(`/v2/payroll/admin/export/pf/${runId}`, {
        responseType: 'blob'
      }) as Response;
      
      let filename = `PF_Export_${runId}.txt`;
      // Since we use Axios, headers is an object/map
      const disposition = (response.headers as any)['content-disposition'];
      if (disposition && disposition.includes('filename="')) {
        const matches = /filename="([^"]+)"/.exec(disposition);
        if (matches != null && matches[1]) { 
          filename = matches[1];
        }
      }

      const url = URL.createObjectURL(response.data as any);
      const link = document.createElement('a');
      link.setAttribute('href', url);
      link.setAttribute('download', filename);
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
      
      toast.success('PF export downloaded successfully');
    } catch (error: any) {
      toast.error(error?.message || 'Failed to export PF file');
    }
  };

  const updateCycleStatus = async (status: string) => {
    if (!selectedCycleId || !selectedCompanyId) return;
    try {
      await api.patch(`/v2/payroll/cycles/${selectedCycleId}/status`, { status, companyId: selectedCompanyId });
      toast.success(`Run moved to ${status}`);
      
      // refresh company run specifically
      const detailedCycle = await payrollCycleApi.getCycle(selectedCycleId);
      setCurrentCompanyRun(detailedCycle?.companies?.find((c: any) => c.companyId === selectedCompanyId) || null);
    } catch (error: any) {
      toast.error(error?.message || 'Failed to update cycle status');
    }
  };

  const currentCycleStatus = currentCompanyRun?.status || 'UNINITIALIZED';

  const companyOptions = companies.map((company) => ({ value: company.id, label: company.code ? `${company.name} (${company.code})` : company.name }));
  const cycleOptions = cycles.map((cycle) => ({ value: cycle.id, label: cycle.name }));

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
            {cycles.length === 0 ? (
              <div className="w-full rounded-xl border border-orange-200 bg-orange-50 p-4 text-orange-800">
                <p className="font-medium">No payroll cycles available.</p>
                <p className="text-sm">Create a global payroll cycle to begin processing.</p>
              </div>
            ) : !currentCompanyRun && selectedCompanyId && selectedCycleId ? (
              <div className="flex w-full items-center justify-between rounded-xl border border-blue-200 bg-blue-50 p-4 text-blue-800">
                <div>
                  <p className="font-medium">Payroll run not initialized for this company and cycle.</p>
                  <p className="text-sm">Initialize the run to begin attendance review and adjustments.</p>
                </div>
                <button
                  type="button"
                  onClick={() => updateCycleStatus('OPEN')}
                  className="inline-flex items-center gap-2 rounded-xl bg-blue-600 px-4 py-2 text-sm font-medium text-white shadow-sm transition hover:bg-blue-500"
                >
                  Initialize Payroll Run
                </button>
              </div>
            ) : null}

            <button
              type="button"
              onClick={() => updateCycleStatus('ATTENDANCE_FINALIZED')}
              disabled={!currentCompanyRun || !['DRAFT', 'OPEN', 'APPROVAL_LOCKED'].includes(currentCycleStatus)}
              className="inline-flex items-center gap-2 rounded-xl border border-slate-200 bg-white px-4 py-2 text-sm font-medium text-slate-700 shadow-sm transition hover:border-slate-300 disabled:cursor-not-allowed disabled:opacity-50"
            >
              <ShieldCheck className="h-4 w-4" /> Finalize Attendance
            </button>
            <button
              type="button"
              onClick={saveAdjustments}
              disabled={!currentCompanyRun || savingAdjustments}
              className="inline-flex items-center gap-2 rounded-xl border border-slate-200 bg-white px-4 py-2 text-sm font-medium text-slate-700 shadow-sm transition hover:border-slate-300 disabled:cursor-not-allowed disabled:opacity-50"
            >
              <Save className="h-4 w-4" /> {savingAdjustments ? 'Saving...' : 'Save Adjustments'}
            </button>
            <button
              type="button"
              onClick={recalculatePayroll}
              disabled={!currentCompanyRun || processingPayroll || currentCycleStatus !== 'ATTENDANCE_FINALIZED'}
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
              onClick={exportBankCSV}
              disabled={!['FINALIZED', 'PUBLISHED', 'EXPORTED'].includes(currentCycleStatus || '') || exportingCSV}
              className="inline-flex items-center gap-2 rounded-xl bg-blue-600 px-4 py-2 text-sm font-medium text-white shadow-sm transition hover:bg-blue-500 disabled:cursor-not-allowed disabled:opacity-50"
            >
              <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg> 
              {exportingCSV ? 'Exporting...' : 'Bank Export'}
            </button>
            <button
              type="button"
              onClick={exportPayrollXLSX}
              disabled={!['CALCULATED', 'ADMIN_REVIEW', 'FINALIZED', 'PUBLISHED', 'EXPORTED'].includes(currentCycleStatus || '') || exportingXLSX}
              className="inline-flex items-center gap-2 rounded-xl bg-teal-600 px-4 py-2 text-sm font-medium text-white shadow-sm transition hover:bg-teal-500 disabled:cursor-not-allowed disabled:opacity-50"
            >
              <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              {exportingXLSX ? 'Exporting...' : 'Payroll Export'}
            </button>
            <button
              type="button"
              onClick={publishPayroll}
              disabled={currentCycleStatus !== 'FINALIZED' || publishingPayroll}
              className="inline-flex items-center gap-2 rounded-xl bg-emerald-600 px-4 py-2 text-sm font-medium text-white shadow-sm transition hover:bg-emerald-500 disabled:cursor-not-allowed disabled:opacity-50"
            >
              <RefreshCw className="h-4 w-4" /> {publishingPayroll ? 'Publishing...' : 'Publish'}
            </button>
            <button
              type="button"
              onClick={exportPF}
              disabled={!['CALCULATED', 'ADMIN_REVIEW', 'FINALIZED', 'PUBLISHED', 'EXPORTED'].includes(currentCycleStatus || '')}
              className="inline-flex items-center gap-2 rounded-xl bg-orange-600 px-4 py-2 text-sm font-medium text-white shadow-sm transition hover:bg-orange-500 disabled:cursor-not-allowed disabled:opacity-50"
            >
              <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
              </svg>
              Export PF
            </button>
            <button
              type="button"
              disabled={true}
              title="Specification Pending"
              className="inline-flex items-center gap-2 rounded-xl bg-slate-300 px-4 py-2 text-sm font-medium text-slate-500 shadow-sm cursor-not-allowed opacity-60"
            >
              <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
              </svg>
              Export ESI (Spec Pending)
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
                  {manualEarnings.map((c) => (
                    <th key={c.id} className="px-4 py-3 text-right text-emerald-600">
                      {c.name}
                    </th>
                  ))}
                  {manualDeductions.map((c) => (
                    <th key={c.id} className="px-4 py-3 text-right text-rose-600">
                      {c.name}
                    </th>
                  ))}
                  {activeLegacyColumns.map((l) => (
                    <th key={`legacy_${l}`} className="px-4 py-3 text-right text-slate-500">
                      {l}
                    </th>
                  ))}
                  <th className="px-4 py-3 text-right">Total Earnings</th>
                  <th className="px-4 py-3 text-right">Total Deductions</th>
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
                        {manualEarnings.map((c) => (
                          <td key={c.id} className="px-4 py-3 text-right">
                            <input
                              type="number" min="0" step="0.01"
                              value={draft[c.id] ?? 0}
                              onChange={(event) => handleDraftChange(row.employeeId, c.id, event.target.value)}
                              className="w-28 rounded-lg border border-emerald-200 bg-white px-2 py-1 text-right text-sm text-slate-900 outline-none focus:border-emerald-400"
                            />
                          </td>
                        ))}
                        {manualDeductions.map((c) => (
                          <td key={c.id} className="px-4 py-3 text-right">
                            <input
                              type="number" min="0" step="0.01"
                              value={draft[c.id] ?? 0}
                              onChange={(event) => handleDraftChange(row.employeeId, c.id, event.target.value)}
                              className="w-28 rounded-lg border border-rose-200 bg-white px-2 py-1 text-right text-sm text-slate-900 outline-none focus:border-rose-400"
                            />
                          </td>
                        ))}
                        {activeLegacyColumns.map((l) => (
                          <td key={`legacy_${l}`} className="px-4 py-3 text-right">
                            <input
                              type="number" min="0" step="0.01"
                              value={draft[`legacy_${l}`] ?? 0}
                              onChange={(event) => handleDraftChange(row.employeeId, `legacy_${l}`, event.target.value)}
                              className="w-28 rounded-lg border border-slate-200 bg-white px-2 py-1 text-right text-sm text-slate-900 outline-none focus:border-slate-400"
                            />
                          </td>
                        ))}
                                                <td className="px-4 py-3 text-right font-semibold text-emerald-700">
                          {formatCurrency(
                            draft.reimbursement + draft.lta +
                            manualEarnings.reduce((acc, c) => acc + toNumber(draft[c.id]), 0)
                          )}
                        </td>
                        <td className="px-4 py-3 text-right font-semibold text-rose-700">
                          {formatCurrency(
                            manualDeductions.reduce((acc, c) => acc + toNumber(draft[c.id]), 0) +
                            activeLegacyColumns.reduce((acc, l) => acc + toNumber(draft[`legacy_${l}`]), 0)
                          )}
                        </td>
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
                    <tr key={payroll.id} className="hover:bg-slate-50/60">
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
