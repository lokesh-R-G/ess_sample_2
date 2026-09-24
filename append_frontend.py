import codecs
path = r'c:\ess\ess_sample_2\src\pages\admin\payroll\AdminPayrollControl.tsx'
content = codecs.open(path, 'r', 'utf-8').read()

export_pf_func = """
  const exportPF = async () => {
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
  };
"""

button_html = """
            <button
              type="button"
              onClick={exportPF}
              disabled={!['CALCULATED', 'ADMIN_REVIEW', 'FINALIZED', 'PUBLISHED', 'EXPORTED'].includes(currentCycleStatus || '')}
              className="inline-flex items-center gap-2 rounded-xl bg-orange-600 px-4 py-2 text-sm font-medium text-white shadow-sm transition hover:bg-orange-500 disabled:cursor-not-allowed disabled:opacity-50"
            >
              <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
              </svg>
              Export PF / EPFO
            </button>
            <button
              type="button"
              onClick={exportESI}
              disabled={!['CALCULATED', 'ADMIN_REVIEW', 'FINALIZED', 'PUBLISHED', 'EXPORTED'].includes(currentCycleStatus || '')}
              className="inline-flex items-center gap-2 rounded-xl bg-purple-600 px-4 py-2 text-sm font-medium text-white shadow-sm transition hover:bg-purple-500 disabled:cursor-not-allowed disabled:opacity-50"
            >
              <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
              </svg>
              Export ESI
            </button>
"""

if "exportPF" not in content:
    content = content.replace("const updateCycleStatus = async (status: string) => {", export_pf_func + "\n  const updateCycleStatus = async (status: string) => {")
    content = content.replace("</button>\n            <button\n              type=\"button\"\n              onClick={publishPayroll}", "</button>\n" + button_html + "            <button\n              type=\"button\"\n              onClick={publishPayroll}")
    codecs.open(path, 'w', 'utf-8').write(content)
    print("Frontend updated")
else:
    print("Already updated")
