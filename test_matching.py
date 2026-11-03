import openpyxl, re, os
from pymongo import MongoClient

uri = os.environ.get('MONGODB_URI', 'mongodb+srv://lokeshca2004_db_user:q7mutTirXPPe8AzC@cluster0.e5z9cjy.mongodb.net/')
client = MongoClient(uri)
db = client['essl_production']

def norm(text):
    if not text: return ''
    return re.sub(r'[^a-zA-Z0-9]', '', str(text)).lower()

def extract_tokens(text):
    if not text: return set()
    # Replace punctuation with spaces, split, lowercase
    cleaned = re.sub(r'[^a-zA-Z0-9]', ' ', str(text)).lower()
    return set(t for t in cleaned.split() if t)

def names_match(n1, n2):
    t1 = extract_tokens(n1)
    t2 = extract_tokens(n2)
    if not t1 or not t2: return False
    
    # Exact full normalized string match
    if norm(n1) == norm(n2): return True
    
    # Substring match on full string
    if norm(n1) in norm(n2) or norm(n2) in norm(n1):
        # Ensure minimum length to avoid matching single initials
        if len(norm(n1)) >= 4 and len(norm(n2)) >= 4:
            return True
            
    # Token-based matching:
    # Separate single-character initials from words with len >= 2
    words1 = [t for t in t1 if len(t) >= 2]
    words2 = [t for t in t2 if len(t) >= 2]
    
    # Check common significant words
    common_words = set(words1).intersection(set(words2))
    if common_words:
        # If the primary name is common (e.g. saravanakumar, badri, narayanan, janarthanan/janardhanan)
        return True
        
    # Check slight spelling variations like janarthanan vs janardhanan, karthick vs karthik
    for w1 in words1:
        for w2 in words2:
            if w1 == w2: return True
            if w1.replace('th', 'd') == w2.replace('th', 'd'): return True
            if w1.replace('ck', 'k') == w2.replace('ck', 'k'): return True
            
    return False

companies = {str(c['_id']): (c.get('companyName') or c.get('name') or '').strip() for c in db.companies.find()}

db_emps = []
for emp_doc in db.employees.find():
    eid = emp_doc.get('employeeId')
    ecode = emp_doc.get('employeeCode')
    
    ehs = list(db.employee_employment_histories.find({'employeeId': eid}))
    personals = list(db.employee_personals.find({'employeeId': eid}))
    
    if ecode in ['423001', '424002', '425001', '425002', '426001', '426002']:
        eh = next((h for h in ehs if str(h.get('companyId')) == '6ac4cc1529e34be07e20f5bc'), None)
        pers = next((p for p in personals if p.get('firstName') in ['WAHEEDA', 'JANARDHANAN ', 'SATHIYAPRIYA', 'KARTHIK', 'VAIRAMANI', 'USHA NANDHINI ']), None)
    else:
        eh = next((h for h in ehs if h.get('isCurrent')), ehs[0] if ehs else None)
        pers = personals[0] if personals else None
    
    name = f"{emp_doc.get('firstName') or ''} {emp_doc.get('lastName') or ''}".strip()
    if not name and pers:
        name = f"{pers.get('firstName') or ''} {pers.get('lastName') or ''}".strip()
    
    comp_id = str(eh.get('companyId')) if eh else ''
    comp_name = companies.get(comp_id, '')
    doj = eh.get('dateOfJoining') if eh else None
    doj_str = doj.strftime('%Y-%m-%d') if doj else ''
    
    db_emps.append({
        'employeeId': eid,
        'employeeCode': ecode,
        'name': name,
        'companyId': comp_id,
        'companyName': comp_name,
        'doj': doj_str
    })

wb = openpyxl.load_workbook('29-10-2026 leave details.xlsx')
ws = wb.active
current_comp = ''

matched = []
unmatched = []

for r in range(1, ws.max_row + 1):
    c1 = str(ws.cell(r, 1).value or '').strip()
    c2 = str(ws.cell(r, 2).value or '').strip()
    for sec in ['IDS Financial Services', 'IDS e Solutions', 'IDS Logistics', 'IDS INDUSTRIES', 'Contract']:
        if sec.lower() in c1.lower() and not c1.isdigit():
            current_comp = c1
            break
    if c2 and c2 not in ['Name', 'total', 'None'] and not c2.startswith('S.no'):
        doj_val = ws.cell(r, 22).value
        doj_str = str(doj_val).split(' ')[0] if doj_val else ''
        
        c_norm = norm(current_comp)
        
        candidates = []
        for d in db_emps:
            d_c_norm = norm(d['companyName'])
            
            comp_match = False
            if ('esolution' in c_norm and 'esolution' in d_c_norm) or \
               ('financial' in c_norm and 'financial' in d_c_norm) or \
               ('logistics' in c_norm and 'logistics' in d_c_norm) or \
               ('industries' in c_norm and 'industries' in d_c_norm):
                comp_match = True
            
            n_match = names_match(c2, d['name'])
            doj_match = (doj_str == d['doj']) if (doj_str and d['doj']) else False
            
            if comp_match and n_match:
                candidates.append((d, comp_match, n_match, doj_match))
        
        if len(candidates) == 1 and candidates[0][1] and candidates[0][2]:
            matched.append((r, current_comp, c2, doj_str, candidates[0][0], candidates[0][3]))
        else:
            unmatched.append((r, current_comp, c2, doj_str, candidates))

print(f"Matched count: {len(matched)}")
for r, comp, name, doj, d, doj_m in matched:
    print(f"Row {r:02d} | {name:<25} -> ID: {d['employeeId']:<6} Code: {d['employeeCode']:<8} Name: {d['name']:<22} DB_DOJ: {d['doj']:<10} (DOJ Match: {doj_m})")

print(f"\nUnmatched count: {len(unmatched)}")
for r, comp, name, doj, cands in unmatched:
    cand_info = [(c[0]['employeeId'], c[0]['name'], c[0]['doj'], f"name_match={c[2]},doj_match={c[3]}") for c in cands]
    print(f"Row {r:02d} | Comp: {comp[:15]} | {name:<22} | DOJ: {doj} -> Candidates: {cand_info}")
