import re

with open(r'c:\ess\ess_sample_2\src\pages\admin\payroll\AdminPayrollControl.tsx', 'r', encoding='utf-8') as f:
    content = f.read()

# Chunk 1: types and DEDUCTION_COLUMNS
chunk1_old = """type DeductionColumnKey = 'salaryAdvance' | 'tds' | 'otherAdvance' | 'labourWelfare' | 'professionalTax';

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
};"""

chunk1_new = """type AdjustmentDraft = {
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
};"""
content = content.replace(chunk1_old, chunk1_new)

# Remove calcRowTotal
content = re.sub(r'function calcRowTotal.*?\}', '', content, flags=re.DOTALL)


# Chunk 2: state
chunk2_old = """  const [currentCycle, setCurrentCycle] = useState<PayrollCycle | null>(null);
  const [currentCompanyRun, setCurrentCompanyRun] = useState<any>(null);

  const selectedCompany = useMemo(() => companies.find((company) => company.id === selectedCompanyId) || null, [companies, selectedCompanyId]);"""

chunk2_new = """  const [currentCycle, setCurrentCycle] = useState<PayrollCycle | null>(null);
  const [currentCompanyRun, setCurrentCompanyRun] = useState<any>(null);
  const [manualComponents, setManualComponents] = useState<any[]>([]);
  const [activeLegacyColumns, setActiveLegacyColumns] = useState<string[]>([]);

  const manualEarnings = useMemo(() => manualComponents.filter(c => c.componentType === 'Earning'), [manualComponents]);
  const manualDeductions = useMemo(() => manualComponents.filter(c => c.componentType === 'Deduction'), [manualComponents]);

  const selectedCompany = useMemo(() => companies.find((company) => company.id === selectedCompanyId) || null, [companies, selectedCompanyId]);"""
content = content.replace(chunk2_old, chunk2_new)


# Chunk 3: loadInitialData
chunk3_old = """        const [companyPayload, cyclePayload] = await Promise.all([
          organizationApi.getCompanies(),
          payrollCycleApi.getCycles(),
        ]);"""
chunk3_new = """        const [companyPayload, cyclePayload, componentsPayload] = await Promise.all([
          organizationApi.getCompanies(),
          payrollCycleApi.getCycles(),
          api.get('/v2/salary-components?inputMode=MANUAL')
        ]);"""
content = content.replace(chunk3_old, chunk3_new)

chunk3b_old = """        setCompanies(companyList);
        setCycles(cycleList);"""
chunk3b_new = """        const componentsList = normalizeArray<any>(componentsPayload)
          .map((comp) => ({ ...comp, id: getId(comp) }))
          .filter(c => c.id && c.isActive !== false);

        setCompanies(companyList);
        setCycles(cycleList);
        setManualComponents(componentsList);"""
content = content.replace(chunk3b_old, chunk3b_new)


# Chunk 4: loop
chunk4_old = """        for (const deduction of deductionList) {
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
        }"""
chunk4_new = """        const legacyColumns = new Set<string>();

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
        setActiveLegacyColumns(Array.from(legacyColumns));"""
content = content.replace(chunk4_old, chunk4_new)


# Chunk 5: setAdjustmentDrafts
chunk5_old = """        setAdjustmentDrafts(
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
        );"""
chunk5_new = """        setAdjustmentDrafts(
          Array.from(rowMap.values()).reduce<Record<string, AdjustmentDraft>>((accumulator, row) => {
            const draft: AdjustmentDraft = { reimbursement: row.reimbursement, lta: row.lta };
            for (const c of manualComponents) draft[c.id] = row[c.id] || 0;
            for (const l of legacyColumns) draft[`legacy_${l}`] = row[`legacy_${l}`] || 0;
            accumulator[row.employeeId] = draft;
            return accumulator;
          }, {})
        );"""
content = content.replace(chunk5_old, chunk5_new)

# Chunk 6: handleDraftChange
chunk6_old = """  const handleDraftChange = (employeeId: string, key: DeductionColumnKey, value: string) => {"""
chunk6_new = """  const handleDraftChange = (employeeId: string, key: string, value: string) => {"""
content = content.replace(chunk6_old, chunk6_new)

# Chunk 7: saveAdjustments
chunk7_old = """  const saveAdjustments = async (): Promise<boolean> => {
    if (!selectedCompanyId || !selectedCycleId) return false;
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
    } catch (error: any) {"""
chunk7_new = """  const saveAdjustments = async (): Promise<boolean> => {
    if (!selectedCompanyId || !selectedCycleId) return false;
    setSavingAdjustments(true);
    try {
      const saveJobs: Promise<unknown>[] = [];
      const runId = currentCompanyRun?.id || currentCompanyRun?._id || selectedCycleId;

      for (const row of adjustments) {
        const draft = adjustmentDrafts[row.employeeId] || EMPTY_DRAFT;
        
        const processColumn = (key: string, label: string, compId: string | null, type: string) => {
          const amount = toNumber(draft[key]);
          const existing = deductionIndex[row.employeeId]?.[key];
          const payload = {
            companyId: selectedCompanyId,
            branchId: row.branchId || selectedBranchId || undefined,
            employeeId: row.employeeId,
            payrollRunId: runId,
            payrollCycleId: selectedCycleId,
            payrollPeriod: payrollMonth,
            componentId: compId,
            adjustmentType: type,
            deductionType: label,
            amount,
            description: label,
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
        };

        for (const c of manualEarnings) processColumn(c.id, c.name, c.id, "EARNING");
        for (const c of manualDeductions) processColumn(c.id, c.name, c.id, "DEDUCTION");
        for (const l of activeLegacyColumns) processColumn(`legacy_${l}`, l, null, "DEDUCTION");
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
          compId = nameMatch ? nameMatch.id : `legacy_${deductionType}`;
        }
        if (compId) {
          deductionMap[empId] = deductionMap[empId] || {};
          deductionMap[empId][compId] = deduction;
        }
      }
      setDeductionIndex(deductionMap);
      return true;
    } catch (error: any) {"""
content = content.replace(chunk7_old, chunk7_new)


# Chunk 8: Headers
chunk8_old = """                  {DEDUCTION_COLUMNS.map((column) => (
                    <th key={column.key} className="px-4 py-3 text-right">
                      {column.label}
                    </th>
                  ))}"""
chunk8_new = """                  {manualEarnings.map((c) => (
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
                  ))}"""
content = content.replace(chunk8_old, chunk8_new)


# Chunk 9: Inputs
chunk9_old = """                        {DEDUCTION_COLUMNS.map((column) => (
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
                        <td className="px-4 py-3 text-right font-semibold text-slate-900">{formatCurrency(calcRowTotal(draft))}</td>"""
chunk9_new = """                        {manualEarnings.map((c) => (
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
                        <td className="px-4 py-3 text-right font-semibold text-slate-900">
                          {formatCurrency(
                            draft.reimbursement + draft.lta +
                            manualEarnings.reduce((acc, c) => acc + toNumber(draft[c.id]), 0) +
                            manualDeductions.reduce((acc, c) => acc + toNumber(draft[c.id]), 0) +
                            activeLegacyColumns.reduce((acc, l) => acc + toNumber(draft[`legacy_${l}`]), 0)
                          )}
                        </td>"""
content = content.replace(chunk9_old, chunk9_new)

with open(r'c:\ess\ess_sample_2\src\pages\admin\payroll\AdminPayrollControl.tsx', 'w', encoding='utf-8') as f:
    f.write(content)

print("Done")
