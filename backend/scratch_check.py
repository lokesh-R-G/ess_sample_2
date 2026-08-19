from pymongo import MongoClient
import json
from bson import json_util

client = MongoClient('mongodb+srv://lokeshca2004_db_user:maYiWdAooh5Qw7QM@cluster0.aehbv6j.mongodb.net/')
db = client.essl_production
comps = list(db.employee_salary_components.find({'employeeId': 'ccb45a55-14e4-4544-96c6-75a4d131e812', 'status': 'Active'}))
print(f'Total Active components: {len(comps)}')
for c in comps:
    print(f"_id: {c.get('_id')}, name: {c.get('componentName')}, monthlyAmount: {c.get('monthlyAmount')}, distributionRatio: {c.get('distributionRatio')}")
