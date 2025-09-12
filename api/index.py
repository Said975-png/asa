from fastapi import FastAPI, Request
from tgbot.main import tgbot

app = FastAPI()

@app.post("/api/index")
async def webhook(request: Request):
    update_dict = await request.json()
    await tgbot.update_bot(update_dict)
    return {"ok": True}
