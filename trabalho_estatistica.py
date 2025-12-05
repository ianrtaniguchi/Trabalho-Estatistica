import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import math
import os

sns.set_theme(style="whitegrid")
plt.rcParams["figure.figsize"] = [10, 6]


def gerar_dados_simulados():
    horarios = []
    periodos = [(5, 8, 10), (8, 11, 20), (11, 13, 15), (13, 16, 20), (16, 19, 8), (19, 23, 30)]

    hora_atual = 5 * 60

    for h_ini, h_fim, intervalo in periodos:
        fim_periodo = h_fim * 60
        while hora_atual < fim_periodo:
            np.random.seed(42)
            ruido = np.random.normal(0, 2)

            horario_real = hora_atual + ruido
            horarios.append(horario_real)
            hora_atual += intervalo

    df = pd.DataFrame({"minutos_dia": horarios})
    df["hora_formatada"] = df["minutos_dia"].apply(lambda x: f"{int(x//60):02d}:{int(x%60):02d}")
    df["intervalo"] = df["minutos_dia"].diff()

    df = df.dropna()
    df = df[df["intervalo"] > 0]
    return df


print("--- 1. Gerando Dados da Linha 211 ---")
df = gerar_dados_simulados()
data = df["intervalo"]
df.to_csv("dados_transporte_vitoria.csv", index=False)
print(f"Dados gerados: {len(df)} observações salvas em 'dados_transporte_vitoria.csv'.")

print("\n--- 2. Calculando Estatísticas ---")
media = np.mean(data)
mediana = np.median(data)
moda = stats.mode(data, keepdims=True)[0][0]
variancia = np.var(data, ddof=1)
desvio_padrao = np.std(data, ddof=1)
cv = (desvio_padrao / media) * 100
amplitude = data.max() - data.min()
assimetria = stats.skew(data)
quartis = np.percentile(data, [25, 50, 75])
decis = np.percentile(data, [10, 90])
desvio_medio = np.mean(np.abs(data - media))

print(f"Média: {media:.2f} | Mediana: {mediana:.2f} | Moda: {moda:.2f}")
print(f"Desvio Padrão: {desvio_padrao:.2f} | CV: {cv:.2f}%")
print(f"Desvio Médio Absoluto: {desvio_medio:.2f}")

print("\n--- 3. Gerando Gráficos ---")
if not os.path.exists("img"):
    os.makedirs("img")

plt.figure()
sns.histplot(data, kde=True, bins=12, color="skyblue", edgecolor="black")
plt.axvline(media, color="red", linestyle="--", label=f"Média ({media:.1f})")
plt.axvline(mediana, color="green", linestyle="-", label=f"Mediana ({mediana:.1f})")
plt.title("Distribuição dos Intervalos (Headway)")
plt.xlabel("Intervalo (min)")
plt.legend()
plt.savefig("img/grafico_histograma.png")

plt.figure()
sns.boxplot(x=data, color="lightgreen")
plt.title("Boxplot dos Intervalos")
plt.xlabel("Intervalo (min)")
plt.savefig("grafico_boxplot.png")

num_bins = 12
intervalos_bins = pd.cut(data, bins=num_bins)
tabela_freq = pd.DataFrame(intervalos_bins.value_counts()).sort_index()
tabela_freq["Frequencia_Acumulada"] = tabela_freq["count"].cumsum()
pontos_medios = [i.mid for i in tabela_freq.index]

plt.figure()
plt.plot(pontos_medios, tabela_freq["count"], marker="o", linestyle="-", color="blue")
plt.title("Polígono de Frequência")
plt.xlabel("Intervalo (min)")
plt.grid(True)
plt.savefig("img/grafico_poligono.png")

plt.figure()
plt.plot(pontos_medios, tabela_freq["Frequencia_Acumulada"], marker="o", linestyle="-", color="orange")
plt.title("Ogiva (Frequência Acumulada)")
plt.xlabel("Intervalo (min)")
plt.grid(True)
plt.savefig("img/grafico_ogiva.png")

print("Gráficos salvos em 'img/' e raiz.")

print("\n--- 4. Inferência e Probabilidade ---")

max_val = data.max()
z_max = (max_val - media) / desvio_padrao

df["hora_float"] = df["minutos_dia"] / 60
pico_tarde = df[(df["hora_float"] >= 16) & (df["hora_float"] < 19)]
prob_condicional = len(pico_tarde[pico_tarde["intervalo"] < 10]) / len(pico_tarde)

erro_desejado = 1.0
n_necessario = ((1.96 * desvio_padrao) / erro_desejado) ** 2
margem_erro = 1.96 * (desvio_padrao / math.sqrt(len(data)))
ic_inferior = media - margem_erro
ic_superior = media + margem_erro

prob_mais_25 = 1 - stats.norm.cdf(25, loc=media, scale=desvio_padrao)

print(f"Escore Z Máximo: {z_max:.2f}")
print(f"Prob. Condicional (Pico Tarde < 10min): {prob_condicional*100:.2f}%")
print(f"Prob. Normal (> 25min): {prob_mais_25*100:.2f}%")
print(f"Intervalo Confiança 95%: [{ic_inferior:.2f}, {ic_superior:.2f}]")
print(f"Tamanho Amostra (Erro=1min): {math.ceil(n_necessario)}")

print("\n--- FIM DO PROCESSAMENTO ---")
