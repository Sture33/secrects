import asyncio

from db.main import get_all_users

print(asyncio.run(get_all_users()))