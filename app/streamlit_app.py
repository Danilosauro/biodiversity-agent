from pathlib import Path
import json

import pandas as pd
import streamlit as st
import plotly.express as px


# ============================================================
# CONFIGURAÇÃO
# ============================================================

st.set_page_config(
    page_title="Biodiversity Agent",
    page_icon="🌿",
    layout="wide",
)


PROJECT_ROOT = Path(__file__).resolve().parent.parent

QUALITY_FILE = (
    PROJECT_ROOT
    / "reports"
    / "quality.json"
)

GOLD_FILE = (
    PROJECT_ROOT
    / "data"
    / "gold"
    / "darwin_core.csv"
)

SILVER_FILE = (
    PROJECT_ROOT
    / "data"
    / "silver"
    / "biodiversity.parquet"
)

AGENT_PLAN_FILE = (
    PROJECT_ROOT
    / "logs"
    / "agent_plan.json"
)

PROFILE_FILE = (
    PROJECT_ROOT
    / "logs"
    / "dataset_profile.json"
)


# ============================================================
# ESTILO
# ============================================================

st.markdown(
    """
    <style>

    .main-title {
        font-size: 2.2rem;
        font-weight: 700;
        margin-bottom: 0.2rem;
    }

    .subtitle {
        color: #666666;
        margin-bottom: 2rem;
    }

    .section-title {
        font-size: 1.4rem;
        font-weight: 650;
        margin-top: 1.5rem;
        margin-bottom: 1rem;
    }

    .status-box {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# FUNÇÕES AUXILIARES
# ============================================================

def load_json(path: Path):

    if not path.exists():
        return None

    try:

        with open(
            path,
            "r",
            encoding="utf-8"
        ) as file:

            return json.load(file)

    except Exception as exc:

        st.error(
            f"Erro ao ler {path}: {exc}"
        )

        return None


@st.cache_data
def load_csv(path: str):

    file = Path(path)

    if not file.exists():
        return None

    try:
        return pd.read_csv(file)

    except Exception as exc:

        st.error(
            f"Erro ao carregar CSV: {exc}"
        )

        return None


@st.cache_data
def load_parquet(path: str):

    file = Path(path)

    if not file.exists():
        return None

    try:
        return pd.read_parquet(file)

    except Exception as exc:

        st.error(
            f"Erro ao carregar Parquet: {exc}"
        )

        return None


def format_percentage(value):

    if value is None:
        return "N/A"

    try:
        return f"{float(value):.1%}"

    except (
        TypeError,
        ValueError
    ):
        return "N/A"


def format_score(value):

    if value is None:
        return "N/A"

    try:
        return f"{float(value):.3f}"

    except (
        TypeError,
        ValueError
    ):
        return "N/A"


def get_quality_metrics(
    quality_report
):

    if not quality_report:
        return {}

    metrics = (
        quality_report
        .get(
            "quality_metrics",
            {}
        )
    )

    if not isinstance(
        metrics,
        dict
    ):
        return {}

    return metrics


def get_validation(
    quality_report
):

    if not quality_report:
        return {}

    validation = (
        quality_report
        .get(
            "darwin_core_validation",
            {}
        )
    )

    if not isinstance(
        validation,
        dict
    ):
        return {}

    return validation


def get_agent(
    quality_report,
    agent_plan
):

    if quality_report:

        agent = quality_report.get(
            "agent",
            {}
        )

        if isinstance(
            agent,
            dict
        ):
            return agent

    if agent_plan:

        return agent_plan

    return {}


def calculate_field_completeness(
    df
):

    if df is None or df.empty:
        return pd.DataFrame()

    result = pd.DataFrame(
        {
            "field": df.columns,
            "completeness": [
                df[column].notna().mean()
                for column in df.columns
            ],
            "missing": [
                int(df[column].isna().sum())
                for column in df.columns
            ],
        }
    )

    result = result.sort_values(
        "completeness"
    )

    return result


def find_metric(
    metrics,
    names
):

    for name in names:

        if name in metrics:
            return metrics[name]

    return None


# ============================================================
# CABEÇALHO
# ============================================================

st.markdown(
    '<div class="main-title">'
    '🌿 Biodiversity Agent'
    '</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'Agentic data-analysis pipeline for biodiversity '
    'observations and Darwin Core interoperability'
    '</div>',
    unsafe_allow_html=True
)


# ============================================================
# CARREGAMENTO
# ============================================================

quality_report = load_json(
    QUALITY_FILE
)

agent_plan = load_json(
    AGENT_PLAN_FILE
)

dataset_profile = load_json(
    PROFILE_FILE
)

gold_df = load_csv(
    str(GOLD_FILE)
)

silver_df = load_parquet(
    str(SILVER_FILE)
)


# ============================================================
# VERIFICAÇÃO
# ============================================================

if quality_report is None:

    st.warning(
        "O relatório de qualidade ainda não foi encontrado."
    )

    st.info(
        "Execute primeiro:"
    )

    st.code(
        "python main.py",
        language="bash"
    )

    st.stop()


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title(
    "Pipeline"
)

st.sidebar.markdown(
    """
    **Bronze**

    Ingestão dos dados originais.

    ↓

    **Agent**

    Análise semântica e planejamento.

    ↓

    **Silver**

    Normalização e transformações determinísticas.

    ↓

    **Gold**

    Representação Darwin Core.

    ↓

    **Quality**

    Validação e métricas.
    """
)

st.sidebar.divider()

if st.sidebar.button(
    "🔄 Recarregar dados"
):

    st.cache_data.clear()

    st.rerun()


# ============================================================
# DADOS DO RELATÓRIO
# ============================================================

metrics = get_quality_metrics(
    quality_report
)

validation = get_validation(
    quality_report
)

agent = get_agent(
    quality_report,
    agent_plan
)

dataset_info = quality_report.get(
    "dataset",
    {}
)


# ============================================================
# 1. RESUMO
# ============================================================

st.markdown(
    '<div class="section-title">'
    '1. Resumo do Pipeline'
    '</div>',
    unsafe_allow_html=True
)


records = dataset_info.get(
    "records"
)

if records is None and gold_df is not None:
    records = len(gold_df)

if records is None:
    records = 0


score = find_metric(
    metrics,
    [
        "score",
        "quality_score",
        "overall_score",
        "overall_quality",
    ]
)

completeness = find_metric(
    metrics,
    [
        "completeness",
        "completeness_rate",
    ]
)

uniqueness = find_metric(
    metrics,
    [
        "uniqueness",
        "uniqueness_rate",
    ]
)

spatial_validity = find_metric(
    metrics,
    [
        "spatial_validity",
        "spatial_validity_rate",
    ]
)

temporal_validity = find_metric(
    metrics,
    [
        "temporal_validity",
        "temporal_validity_rate",
    ]
)


col1, col2, col3, col4, col5 = st.columns(5)


with col1:

    st.metric(
        "Registros",
        f"{records:,}".replace(
            ",",
            "."
        )
    )


with col2:

    st.metric(
        "Qualidade",
        format_score(score)
    )


with col3:

    st.metric(
        "Completude",
        format_percentage(
            completeness
        )
    )


with col4:

    st.metric(
        "Unicidade",
        format_percentage(
            uniqueness
        )
    )


with col5:

    valid = validation.get(
        "valid"
    )

    if valid is True:

        st.metric(
            "Darwin Core",
            "Válido"
        )

    elif valid is False:

        st.metric(
            "Darwin Core",
            "Inválido"
        )

    else:

        st.metric(
            "Darwin Core",
            "N/A"
        )


# ============================================================
# STATUS
# ============================================================

st.markdown(
    '<div class="section-title">'
    'Status da validação'
    '</div>',
    unsafe_allow_html=True
)


valid = validation.get(
    "valid"
)

errors = validation.get(
    "errors",
    []
)

validation_warnings = validation.get(
    "warnings",
    [])


if valid is True:

    st.success(
        "✓ Dataset Darwin Core validado com sucesso."
    )

elif valid is False:

    st.error(
        "✗ A validação Darwin Core encontrou problemas."
    )

else:

    st.warning(
        "⚠ Status de validação não disponível."
    )


if errors:

    with st.expander(
        f"Erros de validação ({len(errors)})"
    ):

        for error in errors:

            st.error(
                error
            )


if validation_warnings:

    with st.expander(
        f"Warnings de validação ({len(validation_warnings)})"
    ):

        for warning in validation_warnings:

            st.warning(
                warning
            )


# ============================================================
# 2. MÉTRICAS
# ============================================================

st.markdown(
    '<div class="section-title">'
    '2. Métricas de Qualidade'
    '</div>',
    unsafe_allow_html=True
)


metric_data = []


metric_mapping = [

    (
        "Completude",
        completeness
    ),

    (
        "Unicidade",
        uniqueness
    ),

    (
        "Validade espacial",
        spatial_validity
    ),

    (
        "Validade temporal",
        temporal_validity
    ),

]


for name, value in metric_mapping:

    if value is not None:

        try:

            metric_data.append(
                {
                    "Métrica": name,
                    "Valor": float(value),
                }
            )

        except (
            TypeError,
            ValueError
        ):
            pass


if metric_data:

    metric_df = pd.DataFrame(
        metric_data
    )

    fig = px.bar(
        metric_df,
        x="Métrica",
        y="Valor",
        range_y=[0, 1],
        text=metric_df["Valor"].map(
            lambda x: f"{x:.1%}"
        ),
        title="Indicadores de qualidade"
    )

    fig.update_layout(
        yaxis_title="Proporção",
        xaxis_title="",
        showlegend=False
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

else:

    st.info(
        "As métricas detalhadas ainda não estão disponíveis."
    )


# ============================================================
# 3. COMPLETUDE POR CAMPO
# ============================================================

st.markdown(
    '<div class="section-title">'
    '3. Completude por Campo'
    '</div>',
    unsafe_allow_html=True
)


if gold_df is not None:

    completeness_df = (
        calculate_field_completeness(
            gold_df
        )
    )

    if not completeness_df.empty:

        fig = px.bar(
            completeness_df,
            x="completeness",
            y="field",
            orientation="h",
            range_x=[0, 1],
            text=completeness_df[
                "completeness"
            ].map(
                lambda x: f"{x:.1%}"
            ),
            title="Completude dos termos Darwin Core"
        )

        fig.update_layout(
            xaxis_title="Completude",
            yaxis_title="Campo",
            height=max(
                400,
                len(completeness_df) * 35
            )
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

        display_df = completeness_df.copy()

        display_df[
            "completeness"
        ] = display_df[
            "completeness"
        ].map(
            lambda x: f"{x:.1%}"
        )

        display_df = display_df.rename(
            columns={
                "field": "Campo",
                "completeness": "Completude",
                "missing": "Valores ausentes",
            }
        )

        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True
        )

else:

    st.info(
        "Dataset Gold não encontrado."
    )


# ============================================================
# 4. TRANSFORMAÇÕES
# ============================================================

st.markdown(
    '<div class="section-title">'
    '4. Transformações do Dataset'
    '</div>',
    unsafe_allow_html=True
)


if silver_df is not None:

    transformation_data = []


    # Taxonomia

    if (
        "nome_popular" in silver_df.columns
        and "nome_cientifico" in silver_df.columns
    ):

        total = len(
            silver_df
        )

        success = int(
            silver_df[
                "nome_cientifico"
            ]
            .notna()
            .sum()
        )

        rate = (
            success / total
            if total
            else 0
        )

        transformation_data.append(
            {
                "Transformação":
                    "Nome popular → nome científico",
                "Sucesso":
                    rate,
                "Registros":
                    f"{success}/{total}",
            }
        )


    # Latitude

    if (
        "latitude" in silver_df.columns
        and "latitude_decimal" in silver_df.columns
    ):

        total = len(
            silver_df
        )

        success = int(
            silver_df[
                "latitude_decimal"
            ]
            .notna()
            .sum()
        )

        rate = (
            success / total
            if total
            else 0
        )

        transformation_data.append(
            {
                "Transformação":
                    "Latitude DMS → decimal",
                "Sucesso":
                    rate,
                "Registros":
                    f"{success}/{total}",
            }
        )


    # Longitude

    if (
        "longitude" in silver_df.columns
        and "longitude_decimal" in silver_df.columns
    ):

        total = len(
            silver_df
        )

        success = int(
            silver_df[
                "longitude_decimal"
            ]
            .notna()
            .sum()
        )

        rate = (
            success / total
            if total
            else 0
        )

        transformation_data.append(
            {
                "Transformação":
                    "Longitude DMS → decimal",
                "Sucesso":
                    rate,
                "Registros":
                    f"{success}/{total}",
            }
        )


    # Data

    if "data_observacao" in silver_df.columns:

        total = len(
            silver_df
        )

        success = int(
            silver_df[
                "data_observacao"
            ]
            .notna()
            .sum()
        )

        rate = (
            success / total
            if total
            else 0
        )

        transformation_data.append(
            {
                "Transformação":
                    "Data → eventDate",
                "Sucesso":
                    rate,
                "Registros":
                    f"{success}/{total}",
            }
        )


    if transformation_data:

        transformation_df = pd.DataFrame(
            transformation_data
        )

        fig = px.bar(
            transformation_df,
            x="Transformação",
            y="Sucesso",
            range_y=[0, 1],
            text=transformation_df[
                "Sucesso"
            ].map(
                lambda x: f"{x:.1%}"
            ),
            title="Taxa de sucesso das transformações"
        )

        fig.update_layout(
            xaxis_title="",
            yaxis_title="Taxa de sucesso"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

        table_df = transformation_df.copy()

        table_df[
            "Sucesso"
        ] = table_df[
            "Sucesso"
        ].map(
            lambda x: f"{x:.1%}"
        )

        st.dataframe(
            table_df,
            use_container_width=True,
            hide_index=True
        )

    else:

        st.info(
            "Nenhuma transformação conhecida "
            "foi identificada no dataset Silver."
        )

else:

    st.warning(
        "Dataset Silver não encontrado."
    )


# ============================================================
# 5. MAPEAMENTO DARWIN CORE
# ============================================================

st.markdown(
    '<div class="section-title">'
    '5. Mapeamento para Darwin Core'
    '</div>',
    unsafe_allow_html=True
)


mappings = quality_report.get(
    "mapping",
    []
)


if not mappings and agent_plan:

    mappings = agent_plan.get(
        "mappings",
        []
    )


if mappings:

    mapping_rows = []

    for item in mappings:

        mapping_rows.append(
            {
                "Origem":
                    item.get(
                        "source_column",
                        ""
                    ),

                "Darwin Core":
                    item.get(
                        "darwin_core_term",
                        ""
                    ),

                "Confiança":
                    item.get(
                        "confidence",
                        0
                    ),

                "Justificativa":
                    item.get(
                        "justification",
                        ""
                    ),
            }
        )

    mapping_df = pd.DataFrame(
        mapping_rows
    )

    mapping_display = mapping_df.copy()

    mapping_display[
        "Confiança"
    ] = mapping_display[
        "Confiança"
    ].map(
        lambda x: f"{float(x):.1%}"
    )

    st.dataframe(
        mapping_display,
        use_container_width=True,
        hide_index=True
    )

else:

    st.info(
        "Nenhum mapeamento foi registrado."
    )


# ============================================================
# 6. AGENTE
# ============================================================

st.markdown(
    '<div class="section-title">'
    '6. Decisão do Agente'
    '</div>',
    unsafe_allow_html=True
)


accepted = agent.get(
    "accepted"
)

reason = agent.get(
    "reason",
    ""
)


col1, col2 = st.columns(
    [1, 3]
)


with col1:

    if accepted is True:

        st.success(
            "DATASET ACEITO"
        )

    elif accepted is False:

        st.error(
            "DATASET REJEITADO"
        )

    else:

        st.warning(
            "STATUS N/D"
        )


with col2:

    st.markdown(
        "**Justificativa da decisão**"
    )

    st.write(
        reason
    )


# ============================================================
# 7. OPERAÇÕES DE LIMPEZA
# ============================================================

cleaning_operations = agent.get(
    "cleaning_operations",
    []
)


st.markdown(
    "**Operações de limpeza propostas**"
)


if cleaning_operations:

    for operation in cleaning_operations:

        st.markdown(
            f"- {operation}"
        )

else:

    st.info(
        "Nenhuma operação de limpeza registrada."
    )


# ============================================================
# 8. VALIDAÇÕES PROPOSTAS PELO AGENTE
# ============================================================

validation_checks = agent.get(
    "validation_checks",
    []
)


st.markdown(
    "**Validações propostas pelo agente**"
)


if validation_checks:

    for check in validation_checks:

        st.markdown(
            f"- {check}"
        )

else:

    st.info(
        "Nenhuma validação registrada."
    )


# ============================================================
# 9. WARNINGS
# ============================================================

warnings = agent.get(
    "warnings",
    []
)


st.markdown(
    '<div class="section-title">'
    '7. Warnings e Ambiguidades'
    '</div>',
    unsafe_allow_html=True
)


if warnings:

    for warning in warnings:

        st.warning(
            warning
        )

else:

    st.success(
        "Nenhum warning foi registrado pelo agente."
    )


# ============================================================
# 10. DATASET GOLD
# ============================================================

st.markdown(
    '<div class="section-title">'
    '8. Dataset Darwin Core'
    '</div>',
    unsafe_allow_html=True
)


if gold_df is not None:

    st.write(
        f"**Registros:** {len(gold_df)}"
    )

    st.write(
        f"**Campos:** {len(gold_df.columns)}"
    )

    st.dataframe(
        gold_df,
        use_container_width=True,
        height=400
    )

else:

    st.warning(
        "Arquivo Darwin Core Gold não encontrado."
    )


# ============================================================
# 11. DISTRIBUIÇÃO ESPACIAL
# ============================================================

if gold_df is not None:

    if (
        "decimalLatitude" in gold_df.columns
        and
        "decimalLongitude" in gold_df.columns
    ):

        spatial_df = gold_df[
            [
                "decimalLatitude",
                "decimalLongitude"
            ]
        ].copy()

        spatial_df[
            "decimalLatitude"
        ] = pd.to_numeric(
            spatial_df[
                "decimalLatitude"
            ],
            errors="coerce"
        )

        spatial_df[
            "decimalLongitude"
        ] = pd.to_numeric(
            spatial_df[
                "decimalLongitude"
            ],
            errors="coerce"
        )

        spatial_df = spatial_df.dropna()


        if not spatial_df.empty:

            st.markdown(
                '<div class="section-title">'
                '9. Distribuição Espacial'
                '</div>',
                unsafe_allow_html=True
            )

            fig = px.scatter_map(
                spatial_df,
                lat="decimalLatitude",
                lon="decimalLongitude",
                zoom=9,
                height=500,
            )

            fig.update_layout(
                margin={
                    "r": 0,
                    "t": 0,
                    "l": 0,
                    "b": 0
                }
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )


# ============================================================
# 12. PERFIL DO DATASET
# ============================================================

st.markdown(
    '<div class="section-title">'
    '10. Perfil do Dataset'
    '</div>',
    unsafe_allow_html=True
)


if dataset_profile:

    profile_col1, profile_col2 = st.columns(
        2
    )


    with profile_col1:

        st.metric(
            "Linhas",
            dataset_profile.get(
                "rows",
                records
            )
        )


    with profile_col2:

        st.metric(
            "Colunas",
            dataset_profile.get(
                "columns",
                len(gold_df.columns)
                if gold_df is not None
                else 0
            )
        )


    with st.expander(
        "Tipos de dados"
    ):

        dtypes = dataset_profile.get(
            "dtypes",
            {}
        )

        if dtypes:

            dtype_df = pd.DataFrame(
                {
                    "Campo":
                        list(dtypes.keys()),
                    "Tipo":
                        list(dtypes.values()),
                }
            )

            st.dataframe(
                dtype_df,
                use_container_width=True,
                hide_index=True
            )


# ============================================================
# 13. ARQUIVOS GERADOS
# ============================================================

st.markdown(
    '<div class="section-title">'
    '11. Evidências e Artefatos'
    '</div>',
    unsafe_allow_html=True
)


artifacts = {

    "Quality report":
        QUALITY_FILE,

    "Darwin Core Gold":
        GOLD_FILE,

    "Silver dataset":
        SILVER_FILE,

    "Agent plan":
        AGENT_PLAN_FILE,

    "Dataset profile":
        PROFILE_FILE,

}


artifact_rows = []


for name, path in artifacts.items():

    artifact_rows.append(
        {
            "Artefato":
                name,

            "Status":
                "✓ Disponível"
                if path.exists()
                else "✗ Ausente",

            "Arquivo":
                str(
                    path.relative_to(
                        PROJECT_ROOT
                    )
                ),
        }
    )


artifact_df = pd.DataFrame(
    artifact_rows
)


st.dataframe(
    artifact_df,
    use_container_width=True,
    hide_index=True
)


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "Biodiversity Agent — "
    "Bronze → Agent → Silver → Darwin Core Gold → Quality"
)
