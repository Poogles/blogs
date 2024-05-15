import asyncio
import time

from fastapi import FastAPI

app = FastAPI()


@app.get("/sync-sleep")
async def time_sleep():
    time.sleep(1)
    return "sync slow\n"


@app.get("/async-sleep")
async def asyncio_sleep():
    await asyncio.sleep(1)
    return "async slow\n"


@app.get("/return")
async def _return():
    return "fast\n"
