from datetime import datetime
from io import BytesIO
from typing import Annotated, List

from fastapi import APIRouter, File, HTTPException
from fastapi import UploadFile as UF
from fastapi.responses import StreamingResponse
from pydantic import WithJsonSchema

from app.connectors.openai import extract_many
from app.utils.base64 import bytes_to_base64
from app.utils.image_processing import preprocess_image
from app.utils.validators import DocumentValidator
from app.utils.xlsx_builder import receipts_to_xlsx
from app.services.upload_service import upload_service_files


UploadFile = Annotated[
    UF,
    WithJsonSchema({"type": "string", "format": "binary"}),
]

router = APIRouter(prefix="/upload")




@router.post("/multiple")
async def upload_multiple_files(files: List[UploadFile] = File(...)):
    """Recebe múltiplas imagens de notas, extrai os dados via IA e devolve um
    arquivo .xlsx para download."""
    return await upload_service_files(files)
