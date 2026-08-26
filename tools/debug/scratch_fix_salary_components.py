from pymongo import MongoClient

def main():
    client = MongoClient('mongodb+srv://lokeshca2004_db_user:maYiWdAooh5Qw7QM@cluster0.aehbv6j.mongodb.net/')
    db = client.essl_production
    
    # Update all components that don't have a status field to have status="Active"
    result = db.employee_salary_components.update_many(
        {"status": {"$exists": False}},
        {"$set": {"status": "Active"}}
    )
    print(f"Updated {result.modified_count} existing salary components.")

if __name__ == "__main__":
    main()
