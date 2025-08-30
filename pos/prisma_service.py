from contextlib import asynccontextmanager
from prisma import Prisma

prisma = Prisma()

@asynccontextmanager
async def prisma_client():
    await prisma.connect()
    try:
        yield prisma
    finally:
        await prisma.disconnect()
