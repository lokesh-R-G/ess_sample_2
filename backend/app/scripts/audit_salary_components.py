import pymongo
from bson import ObjectId

from dotenv import load_dotenv
import os

def main():
    load_dotenv()
    client = pymongo.MongoClient(os.getenv("MONGODB_URI"))
    db = client[os.getenv("MONGODB_DB_NAME")]
    
    print("--- Salary Components Migration Audit ---")
    
    components = list(db.salary_components.find({}))
    
    basic_candidates = []
    derived_candidates = []
    name_to_id = {}
    
    for c in components:
        name = c.get("name", "")
        c_id = str(c["_id"])
        name_to_id[name.lower()] = c_id
        
        if name.lower() == "basic" or name.lower() == "basic salary":
            basic_candidates.append(c)
            
        if c.get("calculationMethod") in ["Percentage", "Formula"]:
            derived_candidates.append(c)
            
    print(f"\n1. Basic Component candidates found: {len(basic_candidates)}")
    for c in basic_candidates:
        print(f"  - [{c['_id']}] {c['name']} (isBasicComponent={c.get('isBasicComponent', False)})")
        
    print(f"\n2. Percentage Components requiring derived ID linking: {len(derived_candidates)}")
    for c in derived_candidates:
        ref_str = c.get("percentageDerivedFrom")
        new_ref_id = c.get("percentageDerivedFromComponentId")
        mapped_id = name_to_id.get(str(ref_str).lower(), "NOT FOUND")
        print(f"  - [{c['_id']}] {c['name']} -> derivedFrom='{ref_str}' | currentRefId={new_ref_id} | mappedId={mapped_id}")
        
    print("\n--- Migration Plan ---")
    if len(basic_candidates) == 1:
        print(f"Update component {basic_candidates[0]['_id']} ({basic_candidates[0]['name']}) to set isBasicComponent=True")
    elif len(basic_candidates) > 1:
        print("WARNING: Multiple Basic candidates found. Manual intervention required.")
    else:
        print("WARNING: No Basic component candidate found.")
        
    for c in derived_candidates:
        ref_str = c.get("percentageDerivedFrom")
        mapped_id = name_to_id.get(str(ref_str).lower())
        if mapped_id:
            print(f"Update component {c['_id']} ({c['name']}) to set percentageDerivedFromComponentId='{mapped_id}'")
        else:
            print(f"WARNING: Cannot map percentageDerivedFrom='{ref_str}' for component {c['name']}.")
            
if __name__ == "__main__":
    main()
