import asyncio
import pprint
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import os

async def run():
    load_dotenv('../../backend/.env')
    client = AsyncIOMotorClient(os.getenv('MONGODB_URI'))
    db = client[os.getenv('MONGODB_DB_NAME')]
    p = await db.employee_personals.find_one()
    c = await db.employee_contacts.find_one()
    print('--- Personal ---')
    pprint.pprint(p)
    print('--- Contact ---')
    pprint.pprint(c)
    client.close()

if __name__ == "__main__":
    asyncio.run(run())
