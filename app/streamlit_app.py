import pandas as pd
import plotly.express as px
import streamlit as st
from sqlalchemy import inspect, text
from sqlalchemy.exc import SQLAlchemyError

from healthcare_analytics.config.settings import (
    SCHEMA_BRONZE,
    SCHEMA_GOLD,
    SCHEMA_SILVER,
)
from healthcare_analytics.utils.db import get_engine

st.set_page_config(
    page_title="Synthetic Healthcare Data Platform",
    page_icon="🩺",
    layout="wide",
)


@st.cache_resource
def database_engine():
    return get_engine()


@st.cache_data(ttl=60)
def read_table(schema: str, table: str) -> pd.DataFrame:
    engine = database_engine()
    if not inspect(engine).has_table(table, schema=schema):
        return pd.DataFrame()

    return pd.read_sql(
        text(f'SELECT * FROM "{schema}"."{table}"'),
        engine,
    )


@st.cache_data(ttl=60)
def layer_counts() -> pd.DataFrame:
    engine = database_engine()
    tables = {
        "Pacientes recebidos": (SCHEMA_BRONZE, "bronze_patients"),
        "Atendimentos recebidos": (SCHEMA_BRONZE, "bronze_encounters"),
        "Condições registradas": (SCHEMA_BRONZE, "bronze_conditions"),
        "Pacientes validados": (SCHEMA_SILVER, "patients"),
        "Atendimentos validados": (SCHEMA_SILVER, "encounters"),
        "Condições validadas": (SCHEMA_SILVER, "conditions"),
        "Perfis consolidados": (SCHEMA_GOLD, "patient_summary"),
        "Atendimentos consolidados": (SCHEMA_GOLD, "obt_encounters"),
    }
    rows = []

    with engine.connect() as connection:
        inspector = inspect(connection)
        for label, (schema, table) in tables.items():
            count = 0
            if inspector.has_table(table, schema=schema):
                count = connection.execute(
                    text(f'SELECT COUNT(*) FROM "{schema}"."{table}"')
                ).scalar_one()
            rows.append({"Indicador": label, "Volume": count})

    return pd.DataFrame(rows)


def format_number(value: float) -> str:
    return f"{value:,.0f}".replace(",", ".")


def format_currency(value: float) -> str:
    return f"US$ {value:,.2f}"


st.title("🩺 Synthetic Healthcare Data Platform")
st.caption("Visão executiva dos indicadores de pacientes e atendimentos")

if st.sidebar.button("Atualizar dados", width="stretch"):
    st.cache_data.clear()
    st.rerun()

st.sidebar.markdown("**Informações consolidadas**")
st.sidebar.caption("Os indicadores são atualizados automaticamente a cada 60 segundos.")

try:
    patients = read_table(SCHEMA_GOLD, "patient_summary")
    encounters = read_table(SCHEMA_GOLD, "obt_encounters")
    encounter_summary = read_table(SCHEMA_GOLD, "encounter_summary")
except SQLAlchemyError:
    st.error("Não foi possível carregar os indicadores neste momento.")
    st.stop()

if patients.empty or encounters.empty:
    st.warning(
        "Os indicadores ainda estão sendo preparados. "
        "Atualize esta página novamente em alguns instantes."
    )
    try:
        st.dataframe(layer_counts(), width="stretch", hide_index=True)
    except SQLAlchemyError:
        pass
    st.stop()

gender_options = sorted(patients["gender"].dropna().astype(str).unique())
selected_genders = st.sidebar.multiselect(
    "Gênero",
    gender_options,
    default=gender_options,
)

filtered_patients = patients[patients["gender"].astype(str).isin(selected_genders)]
patient_ids = set(filtered_patients["patient_id"])
filtered_encounters = encounters[encounters["patient_id"].isin(patient_ids)]

total_patients = filtered_patients["patient_id"].nunique()
total_encounters = filtered_encounters["encounter_id"].nunique()
total_cost = filtered_encounters["total_claim_cost"].fillna(0).sum()
coverage = filtered_encounters["payer_coverage"].fillna(0).sum()

metric_columns = st.columns(4)
metric_columns[0].metric("Pacientes", format_number(total_patients))
metric_columns[1].metric("Encontros", format_number(total_encounters))
metric_columns[2].metric("Custo total", format_currency(total_cost))
metric_columns[3].metric(
    "Cobertura",
    format_currency(coverage),
    delta=f"{(coverage / total_cost * 100):.1f}% do custo" if total_cost else None,
)

overview_tab, patients_tab, encounters_tab, quality_tab = st.tabs(
    ["Visão geral", "Pacientes", "Atendimentos", "Cobertura dos dados"]
)

with overview_tab:
    left, right = st.columns(2)

    gender_counts = (
        filtered_patients.groupby("gender", dropna=False)["patient_id"]
        .nunique()
        .reset_index(name="patients")
    )
    left.plotly_chart(
        px.pie(
            gender_counts,
            names="gender",
            values="patients",
            hole=0.58,
            title="Pacientes por gênero",
        ),
        width="stretch",
    )

    class_counts = (
        filtered_encounters.groupby("encounterclass", dropna=False)["encounter_id"]
        .nunique()
        .sort_values(ascending=False)
        .reset_index(name="encounters")
    )
    right.plotly_chart(
        px.bar(
            class_counts,
            x="encounters",
            y="encounterclass",
            orientation="h",
            title="Encontros por classe",
            labels={"encounters": "Encontros", "encounterclass": "Classe"},
        ),
        width="stretch",
    )

    timeline = filtered_encounters.copy()
    timeline["month"] = (
        pd.to_datetime(timeline["encounter_start_date"], errors="coerce", utc=True)
        .dt.to_period("M")
        .astype(str)
    )
    timeline = (
        timeline.dropna(subset=["month"])
        .groupby("month")["encounter_id"]
        .nunique()
        .reset_index(name="encounters")
    )
    st.plotly_chart(
        px.line(
            timeline,
            x="month",
            y="encounters",
            markers=True,
            title="Evolução mensal dos encontros",
            labels={"month": "Mês", "encounters": "Encontros"},
        ),
        width="stretch",
    )

with patients_tab:
    patient_columns = [
        "patient_id",
        "full_name",
        "gender",
        "race",
        "ethnicity",
        "death",
        "total_encounters",
        "total_claim_cost",
        "avg_encounter_duration_hours",
    ]
    available_columns = [
        column for column in patient_columns if column in filtered_patients.columns
    ]
    st.dataframe(
        filtered_patients[available_columns].sort_values(
            "total_encounters", ascending=False
        ),
        width="stretch",
        hide_index=True,
    )

with encounters_tab:
    if not encounter_summary.empty:
        summary = encounter_summary.sort_values("total_encounters", ascending=False)
        st.plotly_chart(
            px.bar(
                summary,
                x="encounterclass",
                y="sum_claim_cost",
                color="avg_claim_cost",
                title="Custo por classe de encontro",
                labels={
                    "encounterclass": "Classe",
                    "sum_claim_cost": "Custo total",
                    "avg_claim_cost": "Custo médio",
                },
            ),
            width="stretch",
        )

    encounter_columns = [
        "encounter_id",
        "patient_id",
        "encounter_start_date",
        "encounterclass",
        "encounter_description",
        "duration_hours",
        "total_claim_cost",
        "payer_coverage",
    ]
    st.dataframe(
        filtered_encounters[encounter_columns].sort_values(
            "encounter_start_date", ascending=False
        ),
        width="stretch",
        hide_index=True,
    )

with quality_tab:
    counts = layer_counts()
    st.plotly_chart(
        px.bar(
            counts,
            x="Volume",
            y="Indicador",
            orientation="h",
            title="Cobertura das informações processadas",
        ),
        width="stretch",
    )
    st.dataframe(counts, width="stretch", hide_index=True)
