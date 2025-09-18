import pandas as pd
import glob
import re
import os

pasta = "/home/matheus/Área de Trabalho/MartiniIC/Dados/Archive/dados"
arquivos_txt = glob.glob(os.path.join(pasta, "P*"))

# Ordena pela parte numérica do nome (mesmo com P1, P01, P10, P2, etc.)
arquivos_txt = sorted(
    arquivos_txt,
    key=lambda x: int(re.search(r'(\d+)', os.path.basename(x)).group(1))
)

print("Ordem dos arquivos (basename):", [os.path.basename(x) for x in arquivos_txt])

if not arquivos_txt:
    raise FileNotFoundError("Nenhum arquivo encontrado nesse caminho!")

dfs = []
for arquivo in arquivos_txt:
    nome = os.path.basename(arquivo)
    m = re.search(r'P(\d+)', nome, re.IGNORECASE)
    if not m:
        print("Aviso: arquivo não corresponde ao padrão P<number>:", nome)
        continue
    pid = int(m.group(1))
    paciente_label = f'P{pid}'

    df = pd.read_csv(arquivo, sep='\t', header=None, names=['Comprimento_de_Onda', 'Absorbancia'])
    df_filtrado = df[(df['Comprimento_de_Onda'] >= 900) & (df['Comprimento_de_Onda'] <= 1800)].copy()
    df_filtrado['Paciente'] = paciente_label

    dfs.append(df_filtrado)

# concatena tudo (formato longo)
df_todos = pd.concat(dfs, ignore_index=True)

# pivot para formato largo
df_wide = df_todos.pivot(index="Comprimento_de_Onda", columns="Paciente", values="Absorbancia")
df_wide = df_wide.sort_index()  # garante ordem do eixo X

# --- Reordena explicitamente as colunas por número do paciente ---
def paciente_key(col_name):
    m = re.search(r'(\d+)', str(col_name))
    return int(m.group(1)) if m else float('inf')

ordered_cols = sorted(df_wide.columns, key=paciente_key)
print("Colunas antes:", list(df_wide.columns))
print("Colunas ordenadas (numéricas):", ordered_cols)

df_wide = df_wide[ordered_cols]  # reordenar as colunas

# garante nomes como strings simples
df_wide.columns = [str(c) for c in df_wide.columns]

# exporta (nomes padronizados)
df_wide.to_excel("absorbancia_filtrada.xlsx")
df_todos.to_csv("absorbancia_filtrada.csv", index=False)

print("✅ Exportado com colunas na ordem numérica correta.")
