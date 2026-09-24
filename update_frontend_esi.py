import codecs
path = r'c:\ess\ess_sample_2\src\pages\admin\payroll\AdminPayrollControl.tsx'
content = codecs.open(path, 'r', 'utf-8').read()

old_button = """            <button
              type="button"
              onClick={exportESI}
              disabled={!['CALCULATED', 'ADMIN_REVIEW', 'FINALIZED', 'PUBLISHED', 'EXPORTED'].includes(currentCycleStatus || '')}
              className="inline-flex items-center gap-2 rounded-xl bg-purple-600 px-4 py-2 text-sm font-medium text-white shadow-sm transition hover:bg-purple-500 disabled:cursor-not-allowed disabled:opacity-50"
            >
              <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
              </svg>
              Export ESI
            </button>"""

new_button = """            <button
              type="button"
              disabled={true}
              title="Specification Pending"
              className="inline-flex items-center gap-2 rounded-xl bg-slate-300 px-4 py-2 text-sm font-medium text-slate-500 shadow-sm cursor-not-allowed opacity-60"
            >
              <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
              </svg>
              Export ESI (Spec Pending)
            </button>"""

if old_button in content:
    content = content.replace(old_button, new_button)
    codecs.open(path, 'w', 'utf-8').write(content)
    print("ESI button updated")
else:
    print("Old button not found")
