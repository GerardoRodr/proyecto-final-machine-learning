import os
import sys

# 1. Verificar SUMO_HOME
if "SUMO_HOME" in os.environ:
    print(f"[OK] SUMO_HOME detectado en: {os.environ['SUMO_HOME']}")
else:
    sys.exit("[ERROR] No se encontró la variable SUMO_HOME en el sistema.")

# 2. Verificar librería TraCI
try:
    import traci
    print("[OK] Librería TraCI importada correctamente.")
except ImportError:
    sys.exit("[ERROR] No se pudo importar TraCI. Ejecuta: pip install traci")

print("-> Entorno listo para construir la red y el agente.")