from io import BytesIO

from PIL import Image, ImageOps

MAX_DIMENSION = 2048
JPEG_QUALITY = 92


def preprocess_image(data: bytes) -> tuple[bytes, str]:
    """Pré-processa uma imagem para melhorar a extração pela IA.

    - Corrige a orientação usando EXIF (fotos de celular deitadas).
    - Converte para RGB (remove canal alpha e paletas).
    - Redimensiona para no máximo MAX_DIMENSION no maior lado (reduz custo de
      tokens sem perder legibilidade do manuscrito).
    - Exporta como JPEG otimizado.

    Retorna (bytes_processados, mime_type).
    """
    with Image.open(BytesIO(data)) as img:
        img = ImageOps.exif_transpose(img)

        if img.mode != "RGB":
            img = img.convert("RGB")

        width, height = img.size
        largest = max(width, height)
        if largest > MAX_DIMENSION:
            scale = MAX_DIMENSION / largest
            new_size = (int(width * scale), int(height * scale))
            img = img.resize(new_size, Image.LANCZOS)

        buf = BytesIO()
        img.save(buf, format="JPEG", quality=JPEG_QUALITY, optimize=True)
        return buf.getvalue(), "image/jpeg"
