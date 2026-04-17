from fastapi import APIRouter, File, HTTPException, Form, Depends, Request
from fastapi.templating import Jinja2Templates
from fastapi import UploadFile as UF
from pydantic import WithJsonSchema
from typing import List
from app.utils.base64 import bytes_to_base64
import uuid
from pathlib import Path
from datetime import datetime
from app.utils.validators import DocumentValidator
from app.connectors.openai import send_message_ia
from typing import Annotated

UploadFile = Annotated[
    UF,
    WithJsonSchema({
        "type": "string",
        "format": "binary"
    })
]

templates = Jinja2Templates(directory="templates")


router = APIRouter(prefix="/upload")

UPLOAD_DIR = Path("uploads")


doc_validator = DocumentValidator(max_size=25 * 1024 * 1024)

MIME_BY_EXT = {
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
    ".pdf": "application/pdf",
}

@router.post("/multiple")
async def upload_multiple_files(request: Request, prompt: str = Form(...), files: List[UploadFile] = File(...)):
    """Upload multiple files with validation"""
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

    results = []
    images = []

    for file in files:
        # Validate each file
        validation = await doc_validator.validate_file(file)

        if not validation["valid"]:
            results.append({
                "filename": file.filename,
                "success": False,
                "errors": validation["errors"]
            })
            continue

        file_ext = Path(file.filename).suffix.lower()
        unique_filename = f"{uuid.uuid4()}{file_ext}"
        file_path = UPLOAD_DIR / unique_filename

        try:
            data = await file.read()
            file_path.write_bytes(data)
            b64 = bytes_to_base64(data)
            mime = MIME_BY_EXT.get(file_ext, "application/octet-stream")

            images.append((b64, mime))

            results.append({
                "filename": file.filename,
                "stored_filename": unique_filename,
                "success": True,
            })
        except Exception as e:
            results.append({
                "filename": file.filename,
                "success": False,
                "errors": [f"Failed to save: {str(e)}"]
            })

    successful = [r for r in results if r["success"]]
    failed = [r for r in results if not r["success"]]

    return templates.TemplateResponse(
        request,
        "index.html",
        {"message": await send_message_ia(prompt, images)},
    )
