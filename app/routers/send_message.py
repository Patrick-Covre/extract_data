from fastapi import APIRouter, Form
from app.schemas.message import MessagePromt
from app.connectors.openai import send_message_ia

router = APIRouter(prefix="/send_mesage")

@router.post('/prompt')
async def send_message(msg: MessagePromt, username: str = Form(...)):
    text = await send_message_ia(msg.prompt, [])
    return {"message": text}
