import asyncio
from app.db.mongo import get_database

async def run_remediation():
    db = get_database()
    
    # Get the "General Week Off" policy
    policy = await db.weekly_off_policies.find_one({"name": "General Week Off"})
    
    if not policy:
        print("General Week Off policy not found in weekly_off_policies. Looking for policyName...")
        policy = await db.weekly_off_policies.find_one({"policyName": "General Week Off"})
        if not policy:
            policy = await db.weekly_off_policies.find_one({})
    
    if policy:
        policy_id = str(policy["_id"])
        print(f"Using Policy ID: {policy_id}")
        
        # Update employee_shifts where weeklyOffPolicyId is "General Week Off"
        result = await db.employee_shifts.update_many(
            {"weeklyOffPolicyId": "General Week Off"},
            {"$set": {"weeklyOffPolicyId": policy_id}}
        )
        print(f"Modified {result.modified_count} employee_shifts documents.")
    else:
        print("Could not find a weekly off policy to map to!")

if __name__ == "__main__":
    asyncio.run(run_remediation())
