import random

def generar_escenario_trafico(nombre_archivo, probabilidad_NS, probabilidad_EO, duracion_segundos=3600, semilla=42):
    random.seed(semilla)
    
    with open(nombre_archivo, "w") as f:
        f.write("""<routes>
    <vType id="auto" accel="2.6" decel="4.5" sigma="0.5" length="4.5" minGap="2.5" maxSpeed="13.89"/>
    
    <route id="r_NS" edges="N2C C2S" />
    <route id="r_SN" edges="S2C C2N" />
    <route id="r_WE" edges="W2C C2E" />
    <route id="r_EW" edges="E2C C2W" />
""")
        vehiculo_id = 0
        for t in range(duracion_segundos):
            # Eje Norte-Sur
            if random.random() < probabilidad_NS:
                ruta = "r_NS" if random.random() < 0.5 else "r_SN"
                f.write(f'    <vehicle id="veh_{vehiculo_id}" type="auto" route="{ruta}" depart="{t}" />\n')
                vehiculo_id += 1
            # Eje Este-Oeste
            if random.random() < probabilidad_EO:
                ruta = "r_WE" if random.random() < 0.5 else "r_EW"
                f.write(f'    <vehicle id="veh_{vehiculo_id}" type="auto" route="{ruta}" depart="{t}" />\n')
                vehiculo_id += 1
                
        f.write("</routes>\n")
    print(f"[OK] Archivo '{nombre_archivo}' generado con {vehiculo_id} vehiculos.")

if __name__ == "__main__":
    # Generar los cuatro escenarios del informe
    generar_escenario_trafico("rutas_baja.rou.xml", probabilidad_NS=0.08, probabilidad_EO=0.08)
    generar_escenario_trafico("rutas_media.rou.xml", probabilidad_NS=0.20, probabilidad_EO=0.20)
    generar_escenario_trafico("rutas_alta.rou.xml", probabilidad_NS=0.40, probabilidad_EO=0.40)
    generar_escenario_trafico("rutas_desequilibrada.rou.xml", probabilidad_NS=0.45, probabilidad_EO=0.08)
