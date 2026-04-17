import asyncio

from openai import AsyncOpenAI

from app.schemas.receipt import ReceiptData

client = AsyncOpenAI()

MODEL = "gpt-5.4"

EXTRACTION_PROMPT = """
Você é um assistente especializado em extrair dados de cupons/notas de pedido
de materiais de construção (areia, argamassa, brita, etc.).

A partir da IMAGEM da nota, preencha o objeto estruturado com:

- cliente: nome ao lado de "Cliente".
- motorista: nome ao lado de "Motorista".
- placa_veiculo: texto ao lado de "Placa Veículo". É OPCIONAL; se ilegível ou
  ausente, retorne null.
- controle_interno: número ao lado de "CONTROLE INTERNO" (topo direito).
- data: data da nota exatamente como escrita (ex.: "06/01/26").
- itens: lista de produtos da tabela QUANT / UNID / PRODUTO. Inclua APENAS
  linhas com valor preenchido na coluna QUANT (ignore linhas em branco e
  rabiscos/risco em cima do nome).
- observacao: qualquer anotação manuscrita fora da tabela (ex.: local de
  entrega, "Jard NP", nome de obra). Se não houver, retorne null.

Para cada item:
- quantidade: número da coluna QUANT (use ponto como separador decimal).
- unidade: valor da coluna UNID (ex.: "mts", "m³", "sc", "ton"). Null se vazio.
- produto: escolha o rótulo padronizado mais próximo do texto manuscrito dentre:
    Argamassa, Argamassa mista, Argamassa assentamento, Areia mista sem cal,
    Areia fina, Areia média fina, Areia grossa, Areia suja, Barro,
    Pedrisco/Brita, Pó de pedra.
  Se o texto for "Argamassa MISTA" -> "Argamassa mista".
  Se o texto for "Argamassa ASSENTAMENTO" -> "Argamassa assentamento".
  Se não houver correspondência clara, use "Outro".
- produto_original: texto literal escrito na nota (preencha sempre que houver
  alguma variação manuscrita, mesmo se mapeado para um rótulo padronizado).

Regras importantes:
- Se um campo não for legível, retorne null em vez de inventar.
- Nunca invente itens: apenas as linhas com QUANT preenchida entram em "itens".
- Mantenha os textos em português.
""".strip()


async def extract_receipt(image_b64: str, mime: str) -> ReceiptData:
    """Extrai os dados de UMA imagem de nota em formato estruturado."""
    try:
        response = await client.responses.parse(
            model=MODEL,
            input=[
                {
                    "role": "user",
                    "content": [
                        {"type": "input_text", "text": EXTRACTION_PROMPT},
                        {
                            "type": "input_image",
                            "image_url": f"data:{mime};base64,{image_b64}",
                        },
                    ],
                }
            ],
            text_format=ReceiptData,
        )
        return response.output_parsed or ReceiptData()
    except Exception as exc:  # noqa: BLE001
        return ReceiptData(observacao=f"Erro na extração: {exc}")


async def extract_many(images: list[tuple[str, str]]) -> list[ReceiptData]:
    """Processa várias imagens em paralelo e retorna uma lista de ReceiptData."""
    tasks = [extract_receipt(b64, mime) for b64, mime in images]
    return await asyncio.gather(*tasks)
