from pathlib import Path
from fastapi import UploadFile


class DocumentValidator:
    def __init__(self, max_size: int = 10 * 1024 * 1024):
        self.max_size = max_size
        self.allowed_extensions = {".png", ".jpeg", ".jpg"}

    async def validate_file(self, file: UploadFile) -> dict:
        result = {"valid": True, "errors": []}

        if not file.filename or file.filename.strip() == "":
            result["valid"] = False
            result["errors"].append("Nenhum arquivo selecionado")
            return result

        file_suffix = Path(file.filename).suffix.lower()

        if file_suffix not in self.allowed_extensions:
            result["valid"] = False
            result["errors"].append(
                f"Extensão não suportada: {file_suffix or '(desconhecida)'}"
            )

        content = await file.read()
        await file.seek(0)

        file_size = len(content)
        if file_size > self.max_size:
            result["valid"] = False
            result["errors"].append("Arquivo muito grande")

        return result
