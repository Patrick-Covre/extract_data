from pathlib import Path
from fastapi import UploadFile

class DocumentValidator:
    def __init__(self, max_size: int = 10 * 1024 * 1024):
        self.max_size = max_size
        self.allowed_extensions = {'.pdf', '.png', '.jpeg', '.jpg'}
    
    async def validate_file(self, file: UploadFile) -> dict:
        result = {"valid": True, "errors": []}

        if not file.filename or file.filename.strip() == "":
            result["valid"] = False
            result['errors'].append("No file selected")
            return result

        file_prefix = Path(file.filename).suffix.lower()

        if file_prefix not in self.allowed_extensions:
            result['valid'] = False
            result['errors'].append("Sufix is not suported")
        
        content = await file.read()
        await file.seek(0)

        file_size = len(content)
        if file_size > self.max_size:
            result['valid'] = False
            result['errors'].append("The file too large")
        
        return result