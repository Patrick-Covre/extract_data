from pydantic import BaseModel

class MessagePromt(BaseModel):
    prompt: str