import os
import sys
import pandas as pd
import traci

# Comprobar variable de entorno SUMO_HOME
if "SUMO_HOME" in os.environ:
    tools = os.path.join(os.environ["SUMO_HOME"], "tools")
    if tools not in sys.path:
        sys.path.append(tools)
else:
    sys.exit("Error: SUMO_HOME no esta definida en el sistema.")

# Configuracion de rutas y accesos
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SIM_DIR = os.path.join(BASE_DIR, "simulacion") if os.path.exists(os.path.join(BASE_DIR, "simulacion")) else BASE_DIR
NET_FILE = os.path.join(SIM_DIR, "interseccion.net.xml")
INBOUND_EDGES = ["N2C", "S2C", "E2C", "W2C"]

ESCENARIOS = [
    ("Baja", "rutas_baja.rou.xml"),
    ("Media", "rutas_media.rou.xml"),
    ("Alta", "rutas_alta.rou.xml"),
    ("Desequilibrada", "rutas_desequilibrada.rou.xml")
]

def evaluar_escenario_fijo(nombre_escenario, archivo_rutas, duracion_pasos=3600):
    ruta_rutas = os.path.join(SIM_DIR, archivo_rutas)
    cmd = [
        "sumo",
        "-n", NET_FILE,
        "-r", ruta_rutas,
        "--no-step-log", "true",
        "--waiting-time-memory", str(duracion_pasos),
        "--time-to-teleport", "-1"
    ]
    
    traci.start(cmd)
    
    colas_historial = []
    esperas_vehiculos = {}
    vehiculos_ingresados = 0
    vehiculos_atendidos = 0
    
    for _ in range(duracion_pasos):
        traci.simulationStep()
        
        # Registrar vehiculos ingresados y atendidos
        vehiculos_ingresados += traci.simulation.getDepartedNumber()
        vehiculos_atendidos += traci.simulation.getArrivedNumber()
        
        # Calcular cola instantanea en accesos
        cola_paso = sum(traci.edge.getLastStepHaltingNumber(e) for e in INBOUND_EDGES)
        colas_historial.append(cola_paso)
        
        # Registrar tiempo de espera acumulado de vehiculos activos
        for v in traci.vehicle.getIDList():
            esperas_vehiculos[v] = traci.vehicle.getAccumulatedWaitingTime(v)
            
    traci.close()
    
    tiempo_medio_espera = sum(esperas_vehiculos.values()) / len(esperas_vehiculos) if esperas_vehiculos else 0.0
    longitud_media_cola = sum(colas_historial) / len(colas_historial) if colas_historial else 0.0
    cola_maxima = max(colas_historial) if colas_historial else 0
    
    print(f"[{nombre_escenario}] Espera media: {tiempo_medio_espera:.2f} s/veh | Cola media: {longitud_media_cola:.2f} veh | Atendidos: {vehiculos_atendidos}")
    
    return {
        "Escenario": nombre_escenario,
        "Tiempo_Medio_Espera_s": round(tiempo_medio_espera, 2),
        "Longitud_Media_Cola_veh": round(longitud_media_cola, 2),
        "Vehiculos_Ingresados": vehiculos_ingresados,
        "Vehiculos_Atendidos": vehiculos_atendidos,
        "Cola_Maxima_veh": int(cola_maxima)
    }

def main():
    resultados = []
    print("Iniciando evaluacion de linea base con semaforo de tiempos fijos...")
    for nombre, archivo in ESCENARIOS:
        res = evaluar_escenario_fijo(nombre, archivo)
        resultados.append(res)
        
    df = pd.DataFrame(resultados)
    ruta_salida = os.path.join(BASE_DIR, "resultados_linea_base.csv")
    df.to_csv(ruta_salida, index=False)
    print(f"Resultados guardados exitosamente en: {ruta_salida}")

if __name__ == "__main__":
    main()
