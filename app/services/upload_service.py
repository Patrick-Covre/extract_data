from datetime import datetime
from io import BytesIO
from typing import Annotated, List

from fastapi import APIRouter, File, HTTPException
from fastapi import UploadFile as UF
from fastapi.responses import StreamingResponse

from app.connectors.openai import extract_many
from app.utils.base64 import bytes_to_base64
from app.utils.image_processing import preprocess_image
from app.utils.validators import DocumentValidator
from app.utils.xlsx_builder import receipts_to_xlsx


doc_validator = DocumentValidator(max_size=25 * 1024 * 1024)

XLSX_MEDIA_TYPE = (
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

async def upload_service_files(files: List[UploadFile] = File(...)):
    """Recebe múltiplas imagens de notas, extrai os dados via IA e devolve um
    arquivo .xlsx para download."""
    if not files:
        raise HTTPException(status_code=400, detail="Nenhum arquivo enviado")

    prepared: list[tuple[str, str, str]] = []  # (filename, b64, mime)
    errors: list[dict] = []

    for file in files:
        validation = await doc_validator.validate_file(file)
        if not validation["valid"]:
            errors.append(
                {"filename": file.filename, "errors": validation["errors"]}
            )
            continue

        try:
            raw = await file.read()
            processed_bytes, mime = preprocess_image(raw)
            b64 = bytes_to_base64(processed_bytes)
            prepared.append((file.filename, b64, mime))
        except Exception as exc:  # noqa: BLE001
            errors.append(
                {
                    "filename": file.filename,
                    "errors": [f"Falha ao processar imagem: {exc}"],
                }
            )

    if not prepared:
        raise HTTPException(
            status_code=400,
            detail={"message": "Nenhum arquivo válido", "errors": errors},
        )

    images = [(b64, mime) for _, b64, mime in prepared]
    receipts = await extract_many(images)
    named_receipts = list(zip([p[0] for p in prepared], receipts))

    xlsx_bytes = receipts_to_xlsx(named_receipts)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"notas_{timestamp}.xlsx"

    headers = {
        "Content-Disposition": f'attachment; filename="{filename}"',
        "X-Processed-Files": str(len(prepared)),
        "X-Skipped-Files": str(len(errors)),
    }

    return StreamingResponse(
        BytesIO(xlsx_bytes),
        media_type=XLSX_MEDIA_TYPE,
        headers=headers,
    )
