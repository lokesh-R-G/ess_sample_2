from dotenv import load_dotenv
import os
import asyncio
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

from app.services.essl_service import build_essl_client

async def main():
    client = build_essl_client()
    to_date = None
    from_date = None
    try:
        records = await asyncio.to_thread(client.fetch_transactions, from_date, to_date)
    except Exception as e:
        print('Error calling eSSL:', e)
        return
    print(f'Fetched {len(records)} records (showing up to 20):')
    for r in records[:20]:
        print(r)

if __name__ == '__main__':
    asyncio.run(main())
