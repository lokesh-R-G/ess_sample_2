from pymongo import MongoClient
import os

def run():
    client = MongoClient('mongodb+srv://lokeshca2004_db_user:maYiWdAooh5Qw7QM@cluster0.aehbv6j.mongodb.net/')
    db = client['essl_production']
    
    # Audit payroll_cycles
    c = db.payroll_cycles.count_documents({})
    docs = list(db.payroll_cycles.find({}))
    print('Total payroll_cycles:', c)
    for doc in docs:
        print(doc)
        
    print("\n----------------\n")
    
    # Audit branches to see if they have companyId
    b_count = db.branches.count_documents({})
    b_docs = list(db.branches.find({}).limit(5))
    print('Total branches:', b_count)
    if b_docs:
        print("Sample branch:", b_docs[0])

if __name__ == "__main__":
    run()
