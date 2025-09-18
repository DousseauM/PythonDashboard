import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# =======================
# 1. Carregando os dados
# =======================
df_abs = pd.read_excel("absorbancia_filtrada.xlsx")
df_pacientes = pd.read_excel("dados_pacientes_hemograma.xls")

# Cria coluna Paciente (P1, P2, ..., Pn) baseada na ordem das linhas
df_pacientes = df_pacientes.reset_index(drop=True)
df_pacientes["Paciente"] = ["P" + str(i+1) for i in df_pacientes.index]

st.title("Comparação de Grupos - Absorbância")

# =======================
# 2. Funções auxiliares
# =======================
def filtros_grupo_sidebar(nome, df):
    st.sidebar.subheader(f"Filtros do {nome}")
    sexo = st.sidebar.selectbox(f"Sexo ({nome})", ["Todos"] + df["Sexo"].unique().tolist(), key=f"sexo_{nome}")
    idade = st.sidebar.slider(f"Faixa etária ({nome})", int(df["Idade"].min()), int(df["Idade"].max()), (51, 88), key=f"idade_{nome}")
    glicemia = st.sidebar.slider(f"Glicemia ({nome})", int(df["Nivel Glicemia (mg/dL)"].min()), int(df["Nivel Glicemia (mg/dL)"].max()), (27, 67), key=f"glicemia_{nome}")
    globulosvermelhos = st.sidebar.slider(f"Globulos Vermelhos ({nome})", int(df["Globulos Vermelhos (milhoes/µL)"].min()), int(df["Globulos Vermelhos (milhoes/µL)"].max()), (75, 130 ), key=f"globulosvermelhos_{nome}")
    globulosbrancos = st.sidebar.slider(f"Globulos Brancos ({nome})", int(df["Globulos Brancos (milhoes/µl)"].min()), int(df["Globulos Brancos (milhoes/µl)"].max()), (4, 5), key=f"globulosbrancos_{nome}")
    plaquetas = st.sidebar.slider(f"Plaquetas ({nome})", int(df["Plaquetas (mil/µl)"].min()), int(df["Plaquetas (mil/µl)"].max()), (0, 9), key=f"plaquetas{nome}")
    return sexo, idade, glicemia, globulosvermelhos, globulosbrancos, plaquetas

def filtrar(df, sexo, faixa_idade, faixa_glicemia, faixa_globulosvermelhos, faixa_globulosbrancos, faixa_plaquetas):
    df_f = df.copy()
    if sexo != "Todos":
        df_f = df_f[df_f["Sexo"] == sexo]
    df_f = df_f[(df_f["Idade"] >= faixa_idade[0]) & (df_f["Idade"] <= faixa_idade[1])]
    df_f = df_f[(df_f["Nivel Glicemia (mg/dL)"] >= faixa_glicemia[0]) & (df_f["Nivel Glicemia (mg/dL)"] <= faixa_glicemia[1])]
    df_f = df_f[(df_f["Globulos Vermelhos (milhoes/µL)"] >= faixa_globulosvermelhos[0]) & (df_f["Globulos Vermelhos (milhoes/µL)"] <= faixa_globulosvermelhos[1])]
    df_f = df_f[(df_f["Globulos Brancos (milhoes/µl)"] >= faixa_globulosbrancos[0]) & (df_f["Globulos Brancos (milhoes/µl)"] <= faixa_globulosbrancos[1])]
    df_f = df_f[(df_f["Plaquetas (mil/µl)"] >= faixa_plaquetas[0]) & (df_f["Plaquetas (mil/µl)"] <= faixa_plaquetas[1])]
    return df_f

# =======================
# 3. Filtros no sidebar
# =======================
st.sidebar.header("Filtros dos Grupos")
sexo_A, idade_A, glicemia_A, globulosvermelhos_A, globulosbrancos_A, plaquetas_A = filtros_grupo_sidebar("Grupo A", df_pacientes)
sexo_B, idade_B, glicemia_B, globulosvermelhos_B, globulosbrancos_B, plaquetas_B = filtros_grupo_sidebar("Grupo B", df_pacientes)

# =======================
# 4. Aplicando filtros
# =======================
grupoA = filtrar(df_pacientes, sexo_A, idade_A, glicemia_A, globulosvermelhos_A, globulosbrancos_A, plaquetas_A)
grupoB = filtrar(df_pacientes, sexo_B, idade_B, glicemia_B, globulosvermelhos_B, globulosbrancos_B, plaquetas_B)

pacientes_A = grupoA["Paciente"].tolist()
pacientes_B = grupoB["Paciente"].tolist()

# =======================
# 5. Médias
# =======================
media_A = df_abs[["Comprimento_de_Onda"] + pacientes_A].set_index("Comprimento_de_Onda").mean(axis=1) if pacientes_A else None
media_B = df_abs[["Comprimento_de_Onda"] + pacientes_B].set_index("Comprimento_de_Onda").mean(axis=1) if pacientes_B else None

# =======================
# 6. Exibição dos pacientes
# =======================
st.markdown(f"**Grupo A:** {', '.join(pacientes_A) if pacientes_A else 'Nenhum paciente selecionado'}")
st.markdown(f"**Grupo B:** {', '.join(pacientes_B) if pacientes_B else 'Nenhum paciente selecionado'}")

# =======================
# 7. Gráfico
# =======================
fig, ax = plt.subplots(figsize=(10, 6))
if media_A is not None:
    ax.plot(media_A.index, media_A.values, label="Grupo A", color="blue")
if media_B is not None:
    ax.plot(media_B.index, media_B.values, label="Grupo B", color="red")

ax.set_xlabel("Comprimento de Onda (nm)")
ax.set_ylabel("Absorbância média")
ax.set_title("Comparação de Grupos")
ax.legend()

st.pyplot(fig)
