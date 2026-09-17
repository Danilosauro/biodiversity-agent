import json

from langchain_ollama import ChatOllama

from .schemas import AgentPlan


# ============================================================
# CONFIGURAÇÃO DO MODELO
# ============================================================

MODEL_NAME = "llama3.2"


# ============================================================
# SYSTEM PROMPT
# ============================================================

SYSTEM_PROMPT = """
Você é um agente especialista em:

- dados de biodiversidade;
- ciência de dados;
- qualidade de dados;
- interoperabilidade;
- padrão Darwin Core.

Sua função é analisar a estrutura de um dataset de biodiversidade
e produzir um plano estruturado para sua transformação para Darwin Core.

IMPORTANTE:

O agente NÃO executa as transformações.

O agente deve:

1. compreender a estrutura do dataset;
2. identificar o significado provável das colunas;
3. identificar transformações necessárias;
4. propor o mapeamento para termos Darwin Core;
5. identificar validações necessárias;
6. identificar ambiguidades;
7. produzir warnings quando houver incerteza.

As transformações efetivas serão executadas posteriormente por
código Python determinístico.

============================================================
REGRAS GERAIS
============================================================

1. Nunca invente colunas.

2. Nunca invente valores.

3. Utilize somente as colunas fornecidas.

4. Não altere os valores do dataset.

5. Não execute transformações.

6. Não considere somente o nome da coluna.
   Analise também a amostra dos dados.

7. Quando houver ambiguidade, registre em warnings.

8. Quando uma transformação determinística for necessária,
   registre essa operação em cleaning_operations.

9. Para cada mapeamento, forneça uma justificativa.

10. A confiança deve estar entre 0 e 1.

============================================================
TRANSFORMAÇÕES SEMÂNTICAS
============================================================

O dataset pode utilizar uma estrutura diferente do Darwin Core.

O agente deve identificar essas situações.

Exemplo 1:

nome_popular
    ↓
conversão taxonômica
    ↓
nome_cientifico
    ↓
scientificName

Exemplo 2:

latitude em graus/minutos/segundos
    ↓
conversão DMS
    ↓
latitude_decimal
    ↓
decimalLatitude

Exemplo 3:

longitude em graus/minutos/segundos
    ↓
conversão DMS
    ↓
longitude_decimal
    ↓
decimalLongitude

Exemplo 4:

data_observacao no formato DD/MM/YYYY
    ↓
normalização da data
    ↓
eventDate

============================================================
MAPEAMENTOS CONHECIDOS
============================================================

Quando semanticamente apropriado, utilize os seguintes
mapeamentos:

id_registro
    → occurrenceID

id_observacao
    → occurrenceID

nome_popular
    → scientificName

nome_cientifico
    → scientificName

data_observacao
    → eventDate

latitude
    → decimalLatitude

latitude_decimal
    → decimalLatitude

longitude
    → decimalLongitude

longitude_decimal
    → decimalLongitude

observador
    → recordedBy

ambiente
    → habitat

habitat
    → habitat

============================================================
REGRAS IMPORTANTES DE MAPEAMENTO
============================================================

Se existir uma coluna chamada "id_registro" ou
"id_observacao", ela DEVE ser mapeada para:

occurrenceID

Esse mapeamento deve ser incluído mesmo que outras colunas
tenham maior relevância semântica.

Não omita identificadores de ocorrência.

Não invente termos Darwin Core.

Não utilize "count" como termo Darwin Core neste projeto.

Se existir uma coluna de quantidade, como "quantidade",
não a mapeie automaticamente.

Nesse caso, registre uma warning explicando que a variável
não possui um mapeamento Darwin Core definido no contrato
atual.
============================================================
IDENTIFICAÇÃO DE COORDENADAS
============================================================

Se a amostra apresentar valores como:

12°58'17"S
38°30'05"W

considere que os valores estão em graus, minutos e segundos
(DMS).

Nesse caso, proponha:

latitude → decimalLatitude
com operação de conversão DMS.

longitude → decimalLongitude
com operação de conversão DMS.

Não faça o cálculo no agente.

O cálculo será realizado por uma ferramenta determinística.

============================================================
IDENTIFICAÇÃO TAXONÔMICA
============================================================

Se houver uma coluna de nome popular, reconheça que ela pode
precisar de uma conversão taxonômica antes de preencher
scientificName.

Exemplo:

onça-pintada
    ↓
Panthera onca

anta
    ↓
Tapirus terrestris

O agente NÃO deve inventar o nome científico.

A conversão será realizada por uma tabela taxonômica ou ferramenta
determinística.

============================================================
CRITÉRIO DE ACEITAÇÃO
============================================================

O dataset deve ser considerado compatível quando possuir
informações suficientes para representar observações de
biodiversidade.

Procure principalmente:

- identificação da ocorrência;
- organismo ou espécie;
- data do evento;
- localização espacial.

A ausência de algum desses elementos não significa necessariamente
que o dataset deve ser rejeitado.

Nesse caso:

- registre a limitação;
- produza warning;
- explique o impacto na transformação.

O dataset deve ser rejeitado quando claramente não representar
dados de observações de biodiversidade ou quando não houver
informação suficiente para realizar qualquer mapeamento relevante.

============================================================
SAÍDA
============================================================

Responda SOMENTE com JSON válido.

Não utilize Markdown.

Não utilize:

```json

Não escreva texto antes ou depois do JSON.

Utilize exatamente esta estrutura:

{
    "analysis_goal": "string",
    "accepted": true,
    "reason": "string",
    "mappings": [
        {
            "source_column": "string",
            "darwin_core_term": "string",
            "confidence": 0.0,
            "justification": "string"
        }
    ],
    "cleaning_operations": [
        "string"
    ],
    "validation_checks": [
        "string"
    ],
    "warnings": [
        "string"
    ]
}
"""


# ============================================================
# MODELO
# ============================================================

def build_model():
    """
    Inicializa o Llama 3.2 através do Ollama.
    """

    return ChatOllama(
        model=MODEL_NAME,
        temperature=0,
    )


# ============================================================
# NORMALIZAÇÃO DA RESPOSTA
# ============================================================

def normalize_llm_response(
    data: dict
) -> dict:
    """
    Normaliza a resposta do LLM antes da validação Pydantic.

    Isso é importante porque modelos locais podem retornar
    pequenas variações no formato JSON.
    """

    # --------------------------------------------------------
    # analysis_goal
    # --------------------------------------------------------

    if not isinstance(
        data.get("analysis_goal"),
        str
    ):

        data["analysis_goal"] = (
            "Mapeamento de dados de biodiversidade "
            "para Darwin Core"
        )


    # --------------------------------------------------------
    # accepted
    # --------------------------------------------------------

    if "accepted" not in data:

        data["accepted"] = False

    elif isinstance(
        data["accepted"],
        str
    ):

        data["accepted"] = (
            data["accepted"]
            .lower()
            .strip()
            == "true"
        )


    # --------------------------------------------------------
    # reason
    # --------------------------------------------------------

    if not isinstance(
        data.get("reason"),
        str
    ):

        data["reason"] = str(
            data.get("reason", "")
        )


    # --------------------------------------------------------
    # mappings
    # --------------------------------------------------------

    if (
        "mappings" not in data
        or data["mappings"] is None
    ):

        data["mappings"] = []

    elif not isinstance(
        data["mappings"],
        list
    ):

        data["mappings"] = []


    # --------------------------------------------------------
    # normalização dos mappings
    # --------------------------------------------------------

    normalized_mappings = []

    for mapping in data["mappings"]:

        if not isinstance(
            mapping,
            dict
        ):
            continue

        source_column = mapping.get(
            "source_column"
        )

        darwin_core_term = mapping.get(
            "darwin_core_term"
        )

        confidence = mapping.get(
            "confidence",
            0
        )

        justification = mapping.get(
            "justification",
            ""
        )

        if source_column is None:
            continue

        if darwin_core_term is None:
            continue

        try:

            confidence = float(
                confidence
            )

        except (
            TypeError,
            ValueError
        ):

            confidence = 0.0


        confidence = max(
            0.0,
            min(
                1.0,
                confidence
            )
        )


        normalized_mappings.append(
            {
                "source_column": str(
                    source_column
                ),

                "darwin_core_term": str(
                    darwin_core_term
                ),

                "confidence": confidence,

                "justification": str(
                    justification
                ),
            }
        )


    data["mappings"] = normalized_mappings


    # --------------------------------------------------------
    # cleaning_operations
    # --------------------------------------------------------

    data["cleaning_operations"] = (
        normalize_string_list(
            data.get(
                "cleaning_operations",
                []
            )
        )
    )


    # --------------------------------------------------------
    # validation_checks
    # --------------------------------------------------------

    data["validation_checks"] = (
        normalize_string_list(
            data.get(
                "validation_checks",
                []
            )
        )
    )


    # --------------------------------------------------------
    # warnings
    # --------------------------------------------------------

    data["warnings"] = (
        normalize_string_list(
            data.get(
                "warnings",
                []
            )
        )
    )


    return data


# ============================================================
# NORMALIZAÇÃO DE LISTAS
# ============================================================

def normalize_string_list(
    value
) -> list[str]:
    """
    Converte diferentes representações de listas produzidas
    pelo LLM para list[str].
    """

    if value is None:

        return []


    if not isinstance(
        value,
        list
    ):

        value = [value]


    result = []


    for item in value:

        if isinstance(
            item,
            str
        ):

            result.append(
                item
            )

            continue


        if isinstance(
            item,
            dict
        ):

            for key in [
                "warning",
                "message",
                "description",
                "operation",
                "check",
                "value",
            ]:

                if key in item:

                    result.append(
                        str(
                            item[key]
                        )
                    )

                    break

            else:

                result.append(
                    json.dumps(
                        item,
                        ensure_ascii=False
                    )
                )

            continue


        result.append(
            str(item)
        )


    return result


# ============================================================
# EXTRAÇÃO DO JSON
# ============================================================

def extract_json(
    content: str
) -> dict:
    """
    Extrai o objeto JSON retornado pelo LLM.

    Aceita tanto JSON puro quanto respostas contendo
    acidentalmente blocos Markdown.
    """

    if not content:

        raise RuntimeError(
            "Ollama retornou uma resposta vazia."
        )


    content = str(
        content
    ).strip()


    # --------------------------------------------------------
    # Remove Markdown
    # --------------------------------------------------------

    content = (
        content
        .replace(
            "```json",
            ""
        )
        .replace(
            "```JSON",
            ""
        )
        .replace(
            "```",
            ""
        )
        .strip()
    )


    # --------------------------------------------------------
    # Tenta JSON direto
    # --------------------------------------------------------

    try:

        result = json.loads(
            content
        )

        if not isinstance(
            result,
            dict
        ):

            raise RuntimeError(
                "A resposta JSON do Ollama "
                "não é um objeto."
            )

        return result

    except json.JSONDecodeError:
        pass


    # --------------------------------------------------------
    # Procura objeto JSON dentro da resposta
    # --------------------------------------------------------

    start = content.find(
        "{"
    )

    end = content.rfind(
        "}"
    )


    if (
        start == -1
        or end == -1
        or end <= start
    ):

        raise RuntimeError(
            "Não foi encontrado JSON válido "
            "na resposta do Ollama.\n\n"
            "Resposta recebida:\n"
            f"{content}"
        )


    json_content = content[
        start:end + 1
    ]


    try:

        result = json.loads(
            json_content
        )

    except json.JSONDecodeError as exc:

        raise RuntimeError(
            "O Ollama retornou um JSON inválido.\n\n"
            "Resposta recebida:\n"
            f"{content}"
        ) from exc


    if not isinstance(
        result,
        dict
    ):

        raise RuntimeError(
            "A resposta JSON do Ollama "
            "não é um objeto."
        )


    return result


# ============================================================
# ANÁLISE DO DATASET
# ============================================================

def analyze_dataset(
    columns: list[str],
    sample: list[dict] | None = None,
) -> AgentPlan:
    """
    Analisa um dataset de biodiversidade utilizando
    Llama 3.2 através do Ollama.

    Parameters
    ----------
    columns:
        Lista dos nomes das colunas.

    sample:
        Pequena amostra dos registros.

    Returns
    -------
    AgentPlan
        Plano estruturado e validado.
    """

    # --------------------------------------------------------
    # Modelo
    # --------------------------------------------------------

    model = build_model()


    # --------------------------------------------------------
    # Serialização
    # --------------------------------------------------------

    columns_json = json.dumps(
        columns,
        ensure_ascii=False,
        indent=2
    )


    sample_json = json.dumps(
        sample or [],
        ensure_ascii=False,
        indent=2,
        default=str
    )


    # --------------------------------------------------------
    # Prompt
    # --------------------------------------------------------

    prompt = f"""
Analise o dataset de biodiversidade abaixo.

============================================================
COLUNAS
============================================================

{columns_json}


============================================================
AMOSTRA
============================================================

{sample_json}


============================================================
TAREFA
============================================================

Determine:

1. Se o dataset é compatível com observações de biodiversidade.

2. Qual é o objetivo provável do dataset.

3. Quais colunas podem ser mapeadas para Darwin Core.

4. Quais colunas precisam de transformação antes do mapeamento.

5. Quais operações de limpeza devem ser executadas.

6. Quais validações devem ser executadas.

7. Quais limitações ou ambiguidades devem ser registradas.

IMPORTANTE:

Não invente informações.

Não invente colunas.

Não invente nomes científicos.

Se houver nome popular, indique que é necessária uma
conversão taxonômica determinística.

Se houver coordenadas DMS, indique que é necessária uma
conversão determinística para graus decimais.

Não execute nenhum cálculo.

Retorne somente o JSON especificado.
"""


    # --------------------------------------------------------
    # Chamada ao modelo
    # --------------------------------------------------------

    response = model.invoke(
        [
            (
                "system",
                SYSTEM_PROMPT
            ),
            (
                "human",
                prompt
            ),
        ]
    )


    # --------------------------------------------------------
    # Conteúdo
    # --------------------------------------------------------

    content = response.content


    print()
    print(
        "Resposta bruta do Llama:"
    )
    print(
        "-" * 60
    )
    print(
        content
    )
    print(
        "-" * 60
    )


    # --------------------------------------------------------
    # JSON
    # --------------------------------------------------------

    data = extract_json(
        content
    )


    # --------------------------------------------------------
    # Normalização
    # --------------------------------------------------------

    data = normalize_llm_response(
        data
    )


    # --------------------------------------------------------
    # Validação
    # --------------------------------------------------------

    try:

        plan = AgentPlan.model_validate(
            data
        )

    except Exception as exc:

        raise RuntimeError(
            "A resposta do Llama não corresponde "
            "ao schema AgentPlan.\n\n"
            "Dados recebidos:\n"
            f"{json.dumps(data, indent=2, ensure_ascii=False)}"
        ) from exc


    return plan
