import os
import sys
import random
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

ESCENARIOS = [
    ("Baja", "rutas_baja.rou.xml"),
    ("Media", "rutas_media.rou.xml"),
    ("Alta", "rutas_alta.rou.xml"),
    ("Desequilibrada", "rutas_desequilibrada.rou.xml")
]

PHASE_NS_GREEN = 0
PHASE_NS_YELLOW = 1
PHASE_EO_GREEN = 2
PHASE_EO_YELLOW = 3

TIEMPO_VERDE_MINIMO = 10
TIEMPO_VERDE_MAXIMO = 60
DURACION_AMARILLO = 3

def evaluar_escenario_agente(agent, nombre_escenario, archivo_rutas, duracion_pasos=3600):
    ruta_rutas = os.path.join(SIM_DIR, archivo_rutas)
    cmd = [
        "sumo",
        "-n", NET_FILE,
        "-r", ruta_rutas,
        "--no-step-log", "true",
        "--waiting-time-memory", str(duracion_pasos),
        "--time-to-teleport", "-1",
        "--seed", "42"
    ]
    
    traci.start(cmd)
    
    traci.trafficlight.setPhase("C", PHASE_NS_GREEN)
    fase_verde_actual = PHASE_NS_GREEN
    fase_str = "NS"
    tiempo_en_fase = 0
    
    colas_historial = []
    esperas_vehiculos = {}
    vehiculos_ingresados = 0
    vehiculos_atendidos = 0
    infracciones_seguridad = 0
    
    paso = 0
    while paso < duracion_pasos:
        cola_ns = sum(traci.edge.getLastStepHaltingNumber(e) for e in EDGES_NS)
        cola_eo = sum(traci.edge.getLastStepHaltingNumber(e) for e in EDGES_EO)
        estado_actual = agent.discretizar_estado(cola_ns, cola_eo, fase_str, tiempo_en_fase)
        
        # Decision con politica voraz (epsilon = 0) y restricciones de seguridad
        if tiempo_en_fase < TIEMPO_VERDE_MINIMO:
            accion = 0
        elif tiempo_en_fase >= TIEMPO_VERDE_MAXIMO:
            accion = 1
        else:
            accion = agent.elegir_accion(estado_actual, epsilon=0.0)
            
        if accion == 0:
            traci.simulationStep()
            paso += 1
            tiempo_en_fase += 1
            
            # Registro de metricas por paso
            vehiculos_ingresados += traci.simulation.getDepartedNumber()
            vehiculos_atendidos += traci.simulation.getArrivedNumber()
            cola_paso = sum(traci.edge.getLastStepHaltingNumber(e) for e in INBOUND_EDGES)
            colas_historial.append(cola_paso)
            for v in traci.vehicle.getIDList():
                esperas_vehiculos[v] = traci.vehicle.getAccumulatedWaitingTime(v)
        else:
            # Comprobar seguridad del cambio
            if tiempo_en_fase < TIEMPO_VERDE_MINIMO:
                infracciones_seguridad += 1
                
            # Transicion amarilla obligatoria
            if fase_verde_actual == PHASE_NS_GREEN:
                traci.trafficlight.setPhase("C", PHASE_NS_YELLOW)
                for _ in range(DURACION_AMARILLO):
                    traci.simulationStep()
                    paso += 1
                    vehiculos_ingresados += traci.simulation.getDepartedNumber()
                    vehiculos_atendidos += traci.simulation.getArrivedNumber()
                    cola_paso = sum(traci.edge.getLastStepHaltingNumber(e) for e in INBOUND_EDGES)
                    colas_historial.append(cola_paso)
                    for v in traci.vehicle.getIDList():
                        esperas_vehiculos[v] = traci.vehicle.getAccumulatedWaitingTime(v)
                        
                traci.trafficlight.setPhase("C", PHASE_EO_GREEN)
                fase_verde_actual = PHASE_EO_GREEN
                fase_str = "EO"
            else:
                traci.trafficlight.setPhase("C", PHASE_EO_YELLOW)
                for _ in range(DURACION_AMARILLO):
                    traci.simulationStep()
                    paso += 1
                    vehiculos_ingresados += traci.simulation.getDepartedNumber()
                    vehiculos_atendidos += traci.simulation.getArrivedNumber()
                    cola_paso = sum(traci.edge.getLastStepHaltingNumber(e) for e in INBOUND_EDGES)
                    colas_historial.append(cola_paso)
                    for v in traci.vehicle.getIDList():
                        esperas_vehiculos[v] = traci.vehicle.getAccumulatedWaitingTime(v)
                        
                traci.trafficlight.setPhase("C", PHASE_NS_GREEN)
                fase_verde_actual = PHASE_NS_GREEN
                fase_str = "NS"
            tiempo_en_fase = 0
            
    traci.close()
    
    tiempo_medio_espera = sum(esperas_vehiculos.values()) / len(esperas_vehiculos) if esperas_vehiculos else 0.0
    longitud_media_cola = sum(colas_historial) / len(colas_historial) if colas_historial else 0.0
    cola_maxima = max(colas_historial) if colas_historial else 0
    
    print(f"[{nombre_escenario}] Q-Learning -> Espera media: {tiempo_medio_espera:.2f} s/veh | Cola media: {longitud_media_cola:.2f} veh | Atendidos: {vehiculos_atendidos} | Infracciones: {infracciones_seguridad}")
    
    return {
        "Escenario": nombre_escenario,
        "Tiempo_Medio_Espera_s": round(tiempo_medio_espera, 2),
        "Longitud_Media_Cola_veh": round(longitud_media_cola, 2),
        "Vehiculos_Ingresados": vehiculos_ingresados,
        "Vehiculos_Atendidos": vehiculos_atendidos,
        "Cola_Maxima_veh": int(cola_maxima),
        "Infracciones_Seguridad": infracciones_seguridad
    }

def main():
    random.seed(42)
    ruta_modelo = os.path.join(BASE_DIR, "q_table.pkl")
    if not os.path.exists(ruta_modelo):
        sys.exit(f"Error: No se encontro el modelo {ruta_modelo}. Ejecuta primero entrenar_agente.py.")
        
    ruta_fijo = os.path.join(BASE_DIR, "resultados_linea_base.csv")
    if not os.path.exists(ruta_fijo):
        sys.exit(f"Error: No se encontro {ruta_fijo}. Ejecuta primero evaluar_fijo.py.")
        
    df_fijo = pd.read_csv(ruta_fijo).set_index("Escenario")
    
    agent = QLearningAgent()
    agent.cargar_politica(ruta_modelo)
    
    resultados_ql = []
    print("Iniciando evaluacion del agente Q-learning...")
    for nombre, archivo in ESCENARIOS:
        res = evaluar_escenario_agente(agent, nombre, archivo)
        resultados_ql.append(res)
        
    df_ql = pd.DataFrame(resultados_ql).set_index("Escenario")
    
    # Construir tabla comparativa
    comparativa = []
    for esc in df_ql.index:
        esp_fijo = df_fijo.loc[esc, "Tiempo_Medio_Espera_s"]
        esp_ql = df_ql.loc[esc, "Tiempo_Medio_Espera_s"]
        red_esp = ((esp_fijo - esp_ql) / esp_fijo) * 100
        
        cola_fijo = df_fijo.loc[esc, "Longitud_Media_Cola_veh"]
        cola_ql = df_ql.loc[esc, "Longitud_Media_Cola_veh"]
        red_cola = ((cola_fijo - cola_ql) / cola_fijo) * 100
        
        atend_fijo = df_fijo.loc[esc, "Vehiculos_Atendidos"]
        atend_ql = df_ql.loc[esc, "Vehiculos_Atendidos"]
        
        cola_max_fijo = df_fijo.loc[esc, "Cola_Maxima_veh"]
        cola_max_ql = df_ql.loc[esc, "Cola_Maxima_veh"]
        
        cumple_espera = red_esp >= 15.0
        cumple_cola = red_cola >= 10.0
        cumple_rendimiento = atend_ql >= atend_fijo
        
        comparativa.append({
            "Escenario": esc,
            "Espera_Fijo_s": esp_fijo,
            "Espera_QLearning_s": esp_ql,
            "Reduccion_Espera_%": round(red_esp, 2),
            "Cumple_Meta_Espera_15%": cumple_espera,
            "Cola_Fijo_veh": cola_fijo,
            "Cola_QLearning_veh": cola_ql,
            "Reduccion_Cola_%": round(red_cola, 2),
            "Cumple_Meta_Cola_10%": cumple_cola,
            "Atendidos_Fijo": atend_fijo,
            "Atendidos_QLearning": atend_ql,
            "Cola_Max_Fijo": cola_max_fijo,
            "Cola_Max_QLearning": cola_max_ql,
            "Infracciones_Seguridad": df_ql.loc[esc, "Infracciones_Seguridad"]
        })
        
    df_comp = pd.DataFrame(comparativa)
    ruta_comparativa = os.path.join(BASE_DIR, "resultados_comparativos.csv")
    df_comp.to_csv(ruta_comparativa, index=False)
    print(f"\nTabla comparativa guardada exitosamente en: {ruta_comparativa}")
    print(df_comp[["Escenario", "Reduccion_Espera_%", "Reduccion_Cola_%", "Atendidos_QLearning", "Cumple_Meta_Espera_15%", "Cumple_Meta_Cola_10%"]].to_string())

if __name__ == "__main__":
    main()
