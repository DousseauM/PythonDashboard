import streamlit as st
import pandas as pd
import altair as alt
import io

df = pd.read_excel('dados_pacientes_hemograma.xls')
def get_dataframe():
    return df

st.set_page_config(page_title="Hemograma", layout="wide")
st.title("📊 Dados de Hemograma")

# Carrega os dados
df = get_dataframe()

# Filtro por sexo (verifica se há dados)
sexo_opcoes = df['Sexo'].dropna().unique().tolist()
if not sexo_opcoes:
    st.warning("Não há dados de sexo disponíveis.")
    st.stop()

sexo_filtrado = st.multiselect("Filtrar por sexo:", sexo_opcoes, default=sexo_opcoes)

# Aplica o filtro
df_filtrado = df[df['Sexo'].isin(sexo_filtrado)]

# Mostra o dataframe filtrado
st.subheader("Tabela de Dados")
st.dataframe(df_filtrado, use_container_width=True)

if not df_filtrado.empty:
    # Gráfico 1
    st.subheader("📈 Comparação de Nível de Glicemia (Intervalo de Idade)")
    idade_min = int(df_filtrado["Idade"].min())
    idade_max = int(df_filtrado["Idade"].max())
    idade_range = st.slider("Selecione o intervalo de idade:", idade_min, idade_max, (idade_min, idade_max))

    df_idade = df_filtrado[
        (df_filtrado["Idade"] >= idade_range[0]) &
        (df_filtrado["Idade"] <= idade_range[1])
    ]

    if not df_idade.empty:
        df_grouped = df_idade.groupby("Sexo", as_index=False)["Nivel Glicemia (mg/dL)"].mean()
        chart = alt.Chart(df_grouped).mark_bar(size=40).encode(
            x=alt.X("Sexo:N", title="Sexo"),
            y=alt.Y("Nivel Glicemia (mg/dL):Q", title="Média de Glicemia"),
            color="Sexo:N"
        ).properties(width=500, height=400)
        st.altair_chart(chart, use_container_width=True)

    # Gráfico 2
    st.subheader("📊 Comparação entre duas idades específicas")
    atributos = ["Nivel Glicemia (mg/dL)", "Globulos Brancos", "Globulos Vermelhos"]
    atributo_escolhido = st.selectbox("Selecione o atributo para comparar:", atributos)

    idade1 = st.number_input("Idade 1:", min_value=idade_min, max_value=idade_max, value=idade_min)
    idade2 = st.number_input("Idade 2:", min_value=idade_min, max_value=idade_max, value=idade_max)

    df_duas_idades = df_filtrado[df_filtrado["Idade"].isin([idade1, idade2])]

    if not df_duas_idades.empty:
        df_grouped2 = df_duas_idades.groupby(["Sexo", "Idade"], as_index=False)[atributo_escolhido].mean()
        # Garantir que Idade seja string para barras lado a lado
        df_grouped2["Idade"] = df_grouped2["Idade"].astype(str)

        chart2 = alt.Chart(df_grouped2).mark_bar(size=60).encode(
            x=alt.X("Idade:N", title="Idade", axis=alt.Axis(labelAngle=0)),
            y=alt.Y(f"{atributo_escolhido}:Q", title=f"Média de {atributo_escolhido}"),
            color=alt.Color("Sexo:N", title="Sexo"),
            tooltip=["Sexo", "Idade", atributo_escolhido],
            xOffset="Sexo:N"  # <<< essa linha separa as barras lado a lado
        ).properties(width=500, height=400)

        st.altair_chart(chart2, use_container_width=True)


    else:
        st.info("Não há dados para as idades selecionadas ou atributo inválido.")

    # Exportar
    st.subheader("Exportar")
    excel_buffer = io.BytesIO()
    df_filtrado.to_excel(excel_buffer, index=False)
    excel_buffer.seek(0)

    st.download_button(
        label="📥 Baixar dados filtrados (.xlsx)",
        data=excel_buffer,
        file_name="dados_filtrados.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
