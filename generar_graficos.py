import os
import sys
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
GRAFICOS_DIR = os.path.join(BASE_DIR, "graficos")
os.makedirs(GRAFICOS_DIR, exist_ok=True)

# Configuracion de estilo grafico editorial
plt.rcParams.update({
    "font.size": 11,
    "axes.labelsize": 12,
    "axes.titlesize": 13,
    "xtick.labelsize": 10,
    "ytick.labelsize": 10,
    "legend.fontsize": 10,
    "figure.titlesize": 14,
    "axes.grid": True,
    "grid.alpha": 0.35,
    "grid.linestyle": "--"
})

def graficar_convergencia():
    ruta_historial = os.path.join(BASE_DIR, "historial_entrenamiento.csv")
    if not os.path.exists(ruta_historial):
        print(f"Aviso: No se encontro {ruta_historial} para graficar convergencia.")
        return
        
    df = pd.read_csv(ruta_historial)
    
    fig, ax1 = plt.subplots(figsize=(9, 5), dpi=300)
    
    episodios = df["Episodio"]
    recompensas = df["Recompensa_Acumulada"]
    
    # Calcular media movil para suavizar la curva
    ventana = 5
    media_movil = recompensas.rolling(window=ventana, min_periods=1).mean()
    
    # Curva de recompensa
    ax1.plot(episodios, recompensas, color="#1f77b4", alpha=0.35, label="Recompensa por episodio")
    ax1.plot(episodios, media_movil, color="#0b407a", linewidth=2.2, label=f"Media movil ({ventana} ep)")
    ax1.set_xlabel("Episodio de Entrenamiento")
    ax1.set_ylabel("Recompensa Acumulada", color="#0b407a")
    ax1.tick_params(axis="y", labelcolor="#0b407a")
    
    # Eje secundario para decaimiento de epsilon
    ax2 = ax1.twinx()
    ax2.plot(episodios, df["Epsilon"], color="#d95f02", linestyle=":", linewidth=1.8, label="Epsilon (exploracion)")
    ax2.set_ylabel("Tasa de Exploracion (Epsilon)", color="#d95f02")
    ax2.tick_params(axis="y", labelcolor="#d95f02")
    ax2.grid(False)
    
    # Combinar leyendas
    lineas1, etiquetas1 = ax1.get_legend_handles_labels()
    lineas2, etiquetas2 = ax2.get_legend_handles_labels()
    ax1.legend(lineas1 + lineas2, etiquetas1 + etiquetas2, loc="lower right", frameon=True)
    
    plt.title("Convergencia del Entrenamiento Q-Learning Tabular en SUMO")
    fig.tight_layout()
    
    ruta_guardado = os.path.join(GRAFICOS_DIR, "convergencia_entrenamiento.png")
    plt.savefig(ruta_guardado, bbox_inches="tight")
    plt.close()
    print(f"[OK] Grafico guardado: {ruta_guardado}")

def graficar_comparativa_espera():
    ruta_comp = os.path.join(BASE_DIR, "resultados_comparativos.csv")
    if not os.path.exists(ruta_comp):
        print(f"Aviso: No se encontro {ruta_comp} para graficar esperas.")
        return
        
    df = pd.read_csv(ruta_comp)
    
    escenarios = df["Escenario"]
    espera_fijo = df["Espera_Fijo_s"]
    espera_ql = df["Espera_QLearning_s"]
    reduccion = df["Reduccion_Espera_%"]
    
    x = np.arange(len(escenarios))
    ancho = 0.35
    
    fig, ax = plt.subplots(figsize=(8.5, 5), dpi=300)
    barras_fijo = ax.bar(x - ancho/2, espera_fijo, ancho, label="Controlador Fijo", color="#7f7f7f", edgecolor="black", linewidth=0.8)
    barras_ql = ax.bar(x + ancho/2, espera_ql, ancho, label="Agente Q-Learning", color="#2ca02c", edgecolor="black", linewidth=0.8)
    
    ax.set_ylabel("Tiempo Medio de Espera (s/veh)")
    ax.set_title("Comparativa de Tiempo Medio de Espera por Escenario")
    ax.set_xticks(x)
    ax.set_xticklabels(escenarios)
    ax.legend(frameon=True)
    
    # Anotaciones de reduccion porcentual sobre cada barra
    for i in range(len(escenarios)):
        y_max = max(espera_fijo[i], espera_ql[i])
        ax.annotate(f"-{reduccion[i]:.1f}%",
                    xy=(x[i] + ancho/2, espera_ql[i]),
                    xytext=(0, 4),
                    textcoords="offset points",
                    ha="center", va="bottom",
                    fontweight="bold", color="#1b631b")
        
    ax.set_ylim(0, max(espera_fijo) * 1.2)
    fig.tight_layout()
    
    ruta_guardado = os.path.join(GRAFICOS_DIR, "comparativa_espera.png")
    plt.savefig(ruta_guardado, bbox_inches="tight")
    plt.close()
    print(f"[OK] Grafico guardado: {ruta_guardado}")

def graficar_comparativa_colas():
    ruta_comp = os.path.join(BASE_DIR, "resultados_comparativos.csv")
    if not os.path.exists(ruta_comp):
        print(f"Aviso: No se encontro {ruta_comp} para graficar colas.")
        return
        
    df = pd.read_csv(ruta_comp)
    
    escenarios = df["Escenario"]
    cola_fijo = df["Cola_Fijo_veh"]
    cola_ql = df["Cola_QLearning_veh"]
    reduccion = df["Reduccion_Cola_%"]
    
    x = np.arange(len(escenarios))
    ancho = 0.35
    
    fig, ax = plt.subplots(figsize=(8.5, 5), dpi=300)
    barras_fijo = ax.bar(x - ancho/2, cola_fijo, ancho, label="Controlador Fijo", color="#7f7f7f", edgecolor="black", linewidth=0.8)
    barras_ql = ax.bar(x + ancho/2, cola_ql, ancho, label="Agente Q-Learning", color="#1f77b4", edgecolor="black", linewidth=0.8)
    
    ax.set_ylabel("Longitud Media de Cola (veh)")
    ax.set_title("Comparativa de Longitud Media de Cola por Escenario")
    ax.set_xticks(x)
    ax.set_xticklabels(escenarios)
    ax.legend(frameon=True)
    
    for i in range(len(escenarios)):
        ax.annotate(f"-{reduccion[i]:.1f}%",
                    xy=(x[i] + ancho/2, cola_ql[i]),
                    xytext=(0, 4),
                    textcoords="offset points",
                    ha="center", va="bottom",
                    fontweight="bold", color="#0b407a")
        
    ax.set_ylim(0, max(cola_fijo) * 1.25)
    fig.tight_layout()
    
    ruta_guardado = os.path.join(GRAFICOS_DIR, "comparativa_colas.png")
    plt.savefig(ruta_guardado, bbox_inches="tight")
    plt.close()
    print(f"[OK] Grafico guardado: {ruta_guardado}")

def main():
    print("Generando graficos en alta resolucion...")
    graficar_convergencia()
    graficar_comparativa_espera()
    graficar_comparativa_colas()
    print("Todos los graficos han sido generados exitosamente.")

if __name__ == "__main__":
    main()
