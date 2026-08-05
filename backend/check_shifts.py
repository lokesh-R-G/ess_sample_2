import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

async def main():
    client = AsyncIOMotorClient('mongodb://localhost:27017')
    db = client['ess']
    shifts = await db.shifts.find().to_list(length=100)
    for s in shifts:
        print(s)

if __name__ == "__main__":
    asyncio.run(main())
