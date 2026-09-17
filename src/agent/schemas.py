from pydantic import BaseModel, Field
from typing import List


class ColumnMapping(BaseModel):

    source_column: str = Field(
        description="Nome exato da coluna de origem"
    )

    darwin_core_term: str = Field(
        description="Termo Darwin Core correspondente"
    )

    confidence: float = Field(
        ge=0,
        le=1,
        description="Confiança do mapeamento"
    )

    justification: str = Field(
        description="Justificativa do mapeamento"
    )


class AgentPlan(BaseModel):

    analysis_goal: str

    accepted: bool

    reason: str

    mappings: List[ColumnMapping] = Field(
        default_factory=list
    )

    cleaning_operations: List[str] = Field(
        default_factory=list
    )

    validation_checks: List[str] = Field(
        default_factory=list
    )

    warnings: List[str] = Field(
        default_factory=list
    )
