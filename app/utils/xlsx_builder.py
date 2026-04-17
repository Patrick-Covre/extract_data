from io import BytesIO

import polars as pl

from app.schemas.receipt import ReceiptData

COLUMNS = [
    "Arquivo",
    "Controle Interno",
    "Data",
    "Cliente",
    "Motorista",
    "Placa Veículo",
    "Produto",
    "Produto (original)",
    "Quantidade",
    "Unidade",
    "Observação",
]


def _resolve_product(produto: str, produto_original: str | None) -> str:
    """Se a IA classificou como 'Outro', prioriza o texto original."""
    if produto == "Outro" and produto_original:
        return produto_original
    return produto


def receipts_to_rows(
    receipts: list[tuple[str, ReceiptData]],
) -> list[dict]:
    """Transforma uma lista de (arquivo, ReceiptData) em linhas da planilha.

    - Cada item de produto vira uma linha (com dados da nota repetidos).
    - Notas sem itens também são registradas (para o usuário saber que o arquivo
      foi processado mas não tinha quantidade preenchida).
    """
    rows: list[dict] = []

    for filename, receipt in receipts:
        base = {
            "Arquivo": filename,
            "Controle Interno": receipt.controle_interno,
            "Data": receipt.data,
            "Cliente": receipt.cliente,
            "Motorista": receipt.motorista,
            "Placa Veículo": receipt.placa_veiculo,
            "Observação": receipt.observacao,
        }

        if not receipt.itens:
            rows.append(
                {
                    **base,
                    "Produto": None,
                    "Produto (original)": None,
                    "Quantidade": None,
                    "Unidade": None,
                }
            )
            continue

        for item in receipt.itens:
            rows.append(
                {
                    **base,
                    "Produto": _resolve_product(item.produto, item.produto_original),
                    "Produto (original)": item.produto_original,
                    "Quantidade": item.quantidade,
                    "Unidade": item.unidade,
                }
            )

    return rows


def receipts_to_xlsx(receipts: list[tuple[str, ReceiptData]]) -> bytes:
    """Gera os bytes de um arquivo .xlsx a partir das notas extraídas."""
    rows = receipts_to_rows(receipts)

    if not rows:
        df = pl.DataFrame(schema={col: pl.Utf8 for col in COLUMNS})
    else:
        df = pl.DataFrame(rows).select(COLUMNS)

    buf = BytesIO()
    df.write_excel(
        workbook=buf,
        worksheet="Notas",
        autofit=True,
        header_format={"bold": True, "bg_color": "#1f2937", "font_color": "white"},
    )
    return buf.getvalue()
