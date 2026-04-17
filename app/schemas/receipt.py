from typing import Literal, Optional
from pydantic import BaseModel, Field

ProductType = Literal[
    "Argamassa",
    "Argamassa mista",
    "Argamassa assentamento",
    "Areia mista sem cal",
    "Areia fina",
    "Areia média fina",
    "Areia grossa",
    "Areia suja",
    "Barro",
    "Pedrisco/Brita",
    "Pó de pedra",
    "Outro",
]


class ProductItem(BaseModel):
    produto: ProductType = Field(
        description="Tipo do produto conforme a lista pré-definida. Use 'Outro' caso nenhum se encaixe."
    )
    produto_original: Optional[str] = Field(
        default=None,
        description=(
            "Texto original escrito na nota. Preencher sempre que 'produto' for 'Outro' "
            "ou quando houver alguma informação complementar (ex.: 'Argamassa MISTA')."
        ),
    )
    quantidade: float = Field(
        description="Quantidade numérica registrada na coluna QUANT."
    )
    unidade: Optional[str] = Field(
        default=None,
        description="Unidade de medida registrada na coluna UNID (ex.: m³, mts, sc, ton).",
    )


class ReceiptData(BaseModel):
    cliente: Optional[str] = Field(default=None, description="Nome do cliente.")
    motorista: Optional[str] = Field(default=None, description="Nome do motorista.")
    placa_veiculo: Optional[str] = Field(
        default=None,
        description="Placa do veículo (opcional, pode não estar presente).",
    )
    controle_interno: Optional[str] = Field(
        default=None,
        description="Número do CONTROLE INTERNO exibido no topo direito da nota.",
    )
    data: Optional[str] = Field(
        default=None,
        description="Data da nota exatamente como escrita (ex.: '06/01/26').",
    )
    itens: list[ProductItem] = Field(
        default_factory=list,
        description=(
            "Itens da nota. Inclua SOMENTE linhas da tabela que possuam valor "
            "preenchido na coluna QUANT."
        ),
    )
    observacao: Optional[str] = Field(
        default=None,
        description="Qualquer anotação adicional escrita fora da tabela (ex.: destino/entrega).",
    )
