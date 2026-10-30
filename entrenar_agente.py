import os
import sys
import pandas as pd
import traci
from qlearning_agent import QLearningAgent

# Comprobar variable de entorno SUMO_HOME
if "SUMO_HOME" in os.environ:
    tools = os.path.join(os.environ["SUMO_HOME"], "tools")
    if tools not in sys.path:
        sys.path.append(tools)
else:
    sys.exit("Error: SUMO_HOME no esta definida en el sistema.")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SIM_DIR = os.path.join(BASE_DIR, "simulacion") if os.path.exists(os.path.join(BASE_DIR, "simulacion")) else BASE_DIR
NET_FILE = os.path.join(SIM_DIR, "interseccion.net.xml")
INBOUND_EDGES = ["N2C", "S2C", "E2C", "W2C"]
EDGES_NS = ["N2C", "S2C"]
EDGES_EO = ["E2C", "W2C"]

ESCENARIOS_ENTRENAMIENTO = [
    os.path.join(SIM_DIR, "rutas_baja.rou.xml"),
    os.path.join(SIM_DIR, "rutas_media.rou.xml"),
    os.path.join(SIM_DIR, "rutas_alta.rou.xml"),
    os.path.join(SIM_DIR, "rutas_desequilibrada.rou.xml")
]

PHASE_NS_GREEN = 0
PHASE_NS_YELLOW = 1
PHASE_EO_GREEN = 2
PHASE_EO_YELLOW = 3

TIEMPO_VERDE_MINIMO = 10
TIEMPO_VERDE_MAXIMO = 60
DURACION_AMARILLO = 3

def calcular_recompensa(alpha=0.5, beta=1.0, gamma=2.0):
    w_t = 0.0
    q_t = 0
    p_t = 0
    
    for e in INBOUND_EDGES:
        espera_arista = traci.edge.getWaitingTime(e)
        w_t += espera_arista
        q_t += traci.edge.getLastStepHaltingNumber(e)
        
        # Penalizar vehiculos individuales con espera excesiva (> 60s)
        if espera_arista >= 60.0:
            for v in traci.edge.getLastStepVehicleIDs(e):
                if traci.vehicle.getWaitingTime(v) > 60:
                    p_t += 1
                    
    recompensa = -(alpha * (w_t / 10.0) + beta * q_t + gamma * p_t)
    return recompensa

def entrenar(num_episodios=60, duracion_episodio=1200):
    agent = QLearningAgent(alpha_lr=0.1, gamma_df=0.95, epsilon=1.0, epsilon_min=0.01, decay=0.95)
    historial = []
    
    print(f"Iniciando entrenamiento por {num_episodios} episodios ({duracion_episodio} s por episodio)...")
    
    for ep in range(1, num_episodios + 1):
        archivo_rutas = ESCENARIOS_ENTRENAMIENTO[(ep - 1) % len(ESCENARIOS_ENTRENAMIENTO)]
        cmd = [
            "sumo",
            "-n", NET_FILE,
            "-r", archivo_rutas,
            "--no-step-log", "true",
            "--waiting-time-memory", str(duracion_episodio),
            "--time-to-teleport", "-1"
        ]
        
        traci.start(cmd)
        
        traci.trafficlight.setPhase("C", PHASE_NS_GREEN)
        fase_verde_actual = PHASE_NS_GREEN
        fase_str = "NS"
        tiempo_en_fase = 0
        recompensa_acumulada = 0.0
        
        cola_ns = sum(traci.edge.getLastStepHaltingNumber(e) for e in EDGES_NS)
        cola_eo = sum(traci.edge.getLastStepHaltingNumber(e) for e in EDGES_EO)
        estado_actual = agent.discretizar_estado(cola_ns, cola_eo, fase_str, tiempo_en_fase)
        
        paso = 0
        while paso < duracion_episodio:
            # Control estricto de restricciones de seguridad
            if tiempo_en_fase < TIEMPO_VERDE_MINIMO:
                accion = 0
            elif tiempo_en_fase >= TIEMPO_VERDE_MAXIMO:
                accion = 1
            else:
                accion = agent.elegir_accion(estado_actual)
                
            if accion == 0:
                traci.simulationStep()
                paso += 1
                tiempo_en_fase += 1
            else:
                # Transicion obligatoria de amarillo
                if fase_verde_actual == PHASE_NS_GREEN:
                    traci.trafficlight.setPhase("C", PHASE_NS_YELLOW)
                    for _ in range(DURACION_AMARILLO):
                        traci.simulationStep()
                        paso += 1
                    traci.trafficlight.setPhase("C", PHASE_EO_GREEN)
                    fase_verde_actual = PHASE_EO_GREEN
                    fase_str = "EO"
                else:
                    traci.trafficlight.setPhase("C", PHASE_EO_YELLOW)
                    for _ in range(DURACION_AMARILLO):
                        traci.simulationStep()
                        paso += 1
                    traci.trafficlight.setPhase("C", PHASE_NS_GREEN)
                    fase_verde_actual = PHASE_NS_GREEN
                    fase_str = "NS"
                tiempo_en_fase = 0
                
            recompensa = calcular_recompensa()
            recompensa_acumulada += recompensa
            
            cola_ns = sum(traci.edge.getLastStepHaltingNumber(e) for e in EDGES_NS)
            cola_eo = sum(traci.edge.getLastStepHaltingNumber(e) for e in EDGES_EO)
            siguiente_estado = agent.discretizar_estado(cola_ns, cola_eo, fase_str, tiempo_en_fase)
            
            finalizado = (paso >= duracion_episodio)
            agent.aprender(estado_actual, accion, recompensa, siguiente_estado, finalizado)
            estado_actual = siguiente_estado
            
        traci.close()
        agent.decaer_epsilon()
        
        nombre_escenario = os.path.basename(archivo_rutas).replace("rutas_", "").replace(".rou.xml", "")
        historial.append({
            "Episodio": ep,
            "Recompensa_Acumulada": round(recompensa_acumulada, 2),
            "Epsilon": round(agent.epsilon, 4),
            "Escenario": nombre_escenario
        })
        
        if ep % 5 == 0 or ep == 1:
            print(f"Episodio {ep:02d}/{num_episodios} | Escenario: {nombre_escenario:<14} | Recompensa: {recompensa_acumulada:>8.1f} | Epsilon: {agent.epsilon:.3f}")
            
    # Guardar modelo final entrenado
    ruta_modelo = os.path.join(BASE_DIR, "q_table.pkl")
    agent.guardar_politica(ruta_modelo)
    print(f"Modelo final entrenado guardado en: {ruta_modelo}")
    
    # Guardar registro de entrenamiento
    df_historial = pd.DataFrame(historial)
    ruta_historial = os.path.join(BASE_DIR, "historial_entrenamiento.csv")
    df_historial.to_csv(ruta_historial, index=False)
    print(f"Historial de entrenamiento guardado en: {ruta_historial}")

if __name__ == "__main__":
    entrenar(num_episodios=60, duracion_episodio=1200)
