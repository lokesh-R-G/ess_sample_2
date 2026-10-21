with open('c:/ess/ess_sample_2/src/pages/employee/LeaveManagement.tsx', 'r') as f:
    content = f.read()

# Update state
content = content.replace(
    "const [permFormData, setPermFormData] = useState({ date: '', fromTime: '', toTime: '', reason: '' });",
    "const [permFormData, setPermFormData] = useState({ date: '', fromTime: '', toTime: '', reason: '', conversionLeaveType: '' });"
)

# Update submit handler payload
old_submit_req = '''        requestData: {
          date: permFormData.date,
          fromTime: permFormData.fromTime,
          toTime: permFormData.toTime
        },'''
new_submit_req = '''        requestData: {
          date: permFormData.date,
          fromTime: permFormData.fromTime,
          toTime: permFormData.toTime,
          conversionLeaveType: permFormData.conversionLeaveType || undefined
        },'''
content = content.replace(old_submit_req, new_submit_req)

# Update submit handler reset
old_submit_reset = "setPermFormData({ date: '', fromTime: '', toTime: '', reason: '' });"
new_submit_reset = "setPermFormData({ date: '', fromTime: '', toTime: '', reason: '', conversionLeaveType: '' });"
content = content.replace(old_submit_reset, new_submit_reset)

# Update Modal UI
old_modal_ui = '''          <div>
            <label className=\"block text-sm font-medium text-neutral-700 mb-1.5\">Reason</label>'''

new_modal_ui = '''          <div>
            <label className=\"block text-sm font-medium text-neutral-700 mb-1.5\">Leave Type for Excess Permission Conversion</label>
            <select
              className=\"w-full px-4 py-3 mb-4 rounded-lg bg-white border border-neutral-300 text-neutral-900 focus:outline-none focus:border-primary-500 focus:ring-2 focus:ring-primary-500/20\"
              value={permFormData.conversionLeaveType}
              onChange={e => setPermFormData({...permFormData, conversionLeaveType: e.target.value})}
              required
            >
              <option value=\"\">Select leave type</option>
              {Object.keys(leaveBalance).map(lt => (
                <option key={lt} value={lt}>{lt} (Bal: {leaveBalance[lt].balance})</option>
              ))}
            </select>
          </div>
          <div>
            <label className=\"block text-sm font-medium text-neutral-700 mb-1.5\">Reason</label>'''

content = content.replace(old_modal_ui, new_modal_ui)

with open('c:/ess/ess_sample_2/src/pages/employee/LeaveManagement.tsx', 'w') as f:
    f.write(content)
print('Done!')
