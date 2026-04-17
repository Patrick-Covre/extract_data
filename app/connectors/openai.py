from openai import OpenAI
from app.utils.parser_csv import manipulate_data
client = OpenAI()

async def send_message_ia(
    prompt: str,
    images: list[tuple[str, str]] | None = None,
):
    """images: lista de (base64_sem_prefixo, mime) ex.: ("...", "image/jpeg")."""
    if images is None:
        images = []
    content: list[dict] = [{"type": "input_text", "text": prompt}]
    for b64, mime in images:
        content.append(
            {"type": "input_image", "image_url": f"data:{mime};base64,{b64}"}
        )
    response = client.responses.create(
        model="gpt-5.4",
        input=[
            {
                "role": "user",
                "content": content,
            }
        ]
    )
    
    manipulate_data(response.output_text)

    return response.output_text 

