import codecs
import re

path = r'c:\ess\ess_sample_2\src\pages\admin\payroll\AdminPayrollControl.tsx'
content = codecs.open(path, 'r', 'utf-8').read()

# 1. API endpoint
old_api = "api.get('/v2/salary-components?inputMode=MANUAL')"
new_api = "api.get('/v2/organization/salary-components?inputMode=MANUAL')"
content = content.replace(old_api, new_api)

# 2. Save adjustments condition
old_save_1 = """  const saveAdjustments = async (): Promise<boolean> => {
    if (!selectedCompanyId || !selectedCycleId) return false;
    setSavingAdjustments(true);
    try {
      const saveJobs: Promise<unknown>[] = [];
      const runId = currentCompanyRun?.id || currentCompanyRun?._id || selectedCycleId;"""
new_save_1 = """  const saveAdjustments = async (): Promise<boolean> => {
    if (!selectedCompanyId || !selectedCycleId) return false;
    const runId = currentCompanyRun?.id || currentCompanyRun?._id;
    if (!runId) {
      toast.error('A valid Payroll Run is required to save adjustments.');
      return false;
    }
    setSavingAdjustments(true);
    try {
      const saveJobs: Promise<unknown>[] = [];"""
content = content.replace(old_save_1, new_save_1)

# 3. Table headers
old_th_total = '<th className="px-4 py-3 text-right">Total</th>'
new_th_total = '<th className="px-4 py-3 text-right">Total Earnings</th>\n                  <th className="px-4 py-3 text-right">Total Deductions</th>'
content = content.replace(old_th_total, new_th_total)

# 4. Table cells
old_td_total_regex = r'<td className="px-4 py-3 text-right font-semibold text-slate-900">.*?draft\.reimbursement \+ draft\.lta \+.*?activeLegacyColumns\.reduce.*?\).*?<\/td>'
new_td_total = """                        <td className="px-4 py-3 text-right font-semibold text-emerald-700">
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
                        </td>"""
content = re.sub(old_td_total_regex, new_td_total, content, flags=re.DOTALL)

codecs.open(path, 'w', 'utf-8').write(content)
print("Done")
