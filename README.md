# Sistema Inteligente de Control Semaforico con Q-Learning Tabular en SUMO

Este repositorio contiene la implementacion completa, entrenamiento y evaluacion experimental de un sistema de control semaforico adaptativo basado en **Aprendizaje por Refuerzo Tabular (Q-learning)** y micro-simulacion de trafico vehicular con **Eclipse SUMO** mediante la libreria **TraCI** en Python.

El agente optimiza los tiempos de luz verde en una interseccion semaforizada ortogonal de dos ejes y dos carriles por sentido, evaluado bajo cuatro escenarios de demanda vehicular y comparado de manera cuantitativa contra un controlador semaforico determinista de tiempos fijos.

---

## Tabla de Contenidos
1. [Caracteristicas y Criterios de Exito](#caracteristicas-y-criterios-de-exito)
2. [Estructura del Repositorio](#estructura-del-repositorio)
3. [Requisitos Previos del Sistema](#requisitos-previos-del-sistema)
4. [Instalacion de Eclipse SUMO](#instalacion-de-eclipse-sumo)
   - [Instalacion en Windows](#instalacion-en-windows)
   - [Instalacion en Linux (Ubuntu/Debian)](#instalacion-en-linux-ubuntudebian)
   - [Instalacion en macOS](#instalacion-en-macos)
   - [Verificacion de la Instalacion de SUMO](#verificacion-de-la-instalacion-de-sumo)
5. [Instalacion del Entorno Python y Dependencias](#instalacion-del-entorno-python-y-dependencias)
6. [Garantia de Reproducibilidad entre Computadoras](#garantia-de-reproducibilidad-entre-computadoras)
7. [Guia de Ejecucion Paso a Paso](#guia-de-ejecucion-paso-a-paso)
   - [Paso 1: Generacion de la Red y Escenarios de Rutas](#paso-1-generacion-de-la-red-y-escenarios-de-rutas)
   - [Paso 2: Evaluacion de Linea Base (Semaforo Fijo)](#paso-2-evaluacion-de-linea-base-semaforo-fijo)
   - [Paso 3: Entrenamiento del Agente Q-Learning](#paso-3-entrenamiento-del-agente-q-learning)
   - [Paso 4: Evaluacion Experimental Comparativa](#paso-4-evaluacion-experimental-comparativa)
   - [Paso 5: Generacion de Figuras y Graficos](#paso-5-generacion-de-figuras-y-graficos)
8. [Visualizacion Interactiva en SUMO-GUI](#visualizacion-interactiva-en-sumo-gui)
9. [Resultados Experimentales Obtenidos](#resultados-experimentales-obtenidos)
10. [Solucion de Problemas Frecuentes](#solucion-de-problemas-frecuentes)

---

## Caracteristicas y Criterios de Exito

El proyecto cumple de forma estricta con los siguientes criterios academicos y operativos:
- **Reduccion del tiempo medio de espera vehicular:** Mayor al 15 % frente a tiempos fijos en todos los escenarios (alcanzado: **59.39 % a 72.80 %**).
- **Reduccion de la longitud media de cola:** Mayor al 10 % frente a tiempos fijos (alcanzado: **59.01 % a 72.75 %**).
- **Rendimiento de evacuacion (throughput):** Igual o superior al controlador fijo, sin provocar congestion inducida.
- **Restricciones estrictas de seguridad vial:**
  - Minimo de 10 segundos continuos de luz verde antes de permitir cambios de fase.
  - Maximo de 60 segundos de verde continuo para evitar la inanicion de ejes opuestos.
  - Transicion obligatoria de luz amarilla de 3 segundos exactos.
  - Cero infracciones de seguridad registradas en 14,400 segundos totales evaluados.

---

## Estructura del Repositorio

```text
ml_proyecto-final/
│
├── simulacion/                              # Definiciones de la red y trafico en SUMO
│   ├── red.nod.xml                          # Definicion de nodos de la interseccion (nodo C con semaforo)
│   ├── red.edg.xml                          # Definicion de calles y carriles (2 carriles por sentido a 50 km/h)
│   ├── interseccion.net.xml                 # Red vial compilada mediante netconvert
│   ├── generar_rutas.py                     # Script generador de flujos vehiculares
│   ├── rutas_baja.rou.xml                   # Escenario de baja demanda (547 veh)
│   ├── rutas_media.rou.xml                  # Escenario de media demanda (1430 veh)
│   ├── rutas_alta.rou.xml                   # Escenario de alta demanda (2879 veh)
│   ├── rutas_desequilibrada.rou.xml         # Escenario con saturacion asimetrica (1902 veh)
│   └── simulacion.sumocfg                   # Archivo maestro para SUMO y SUMO-GUI
│
├── graficos/                                # Figuras generadas en alta resolucion (300 DPI)
│   ├── convergencia_entrenamiento.png       # Curva de recompensa acumulada y decaimiento de epsilon
│   ├── comparativa_espera.png               # Barras comparativas de tiempo de espera (s/veh)
│   └── comparativa_colas.png                # Barras comparativas de longitud de cola (veh)
│
├── test.py                                  # Script de comprobacion rapida del entorno y TraCI
├── qlearning_agent.py                       # Clase QLearningAgent (estados discretos, tabla Q y Bellman)
├── entrenar_agente.py                       # Script de entrenamiento headless por 60 episodios
├── evaluar_fijo.py                          # Evaluacion experimental del semaforo de tiempos fijos
├── evaluar_agente.py                        # Evaluacion experimental comparativa del agente Q-learning
├── generar_graficos.py                      # Generador de figuras y graficos comparativos
├── q_table.pkl                              # Politica aprendida serializada
├── historial_entrenamiento.csv              # Registro de recompensa por episodio de entrenamiento
├── resultados_linea_base.csv                # Metricas cuantitativas del controlador fijo
├── resultados_comparativos.csv              # Tabla comparativa con reducciones porcentuales
├── resumen_secciones_3_y_4.md               # Informe tecnico para documentacion y memoria academica
├── requirements.txt                         # Dependencias de Python fijadas
└── README.md                                # Guia principal del proyecto
```

---

## Requisitos Previos del Sistema

- **Sistema Operativo:** Windows 10/11 (64-bit), Ubuntu 20.04/22.04/24.04 LTS o macOS 12+.
- **Python:** Version 3.10 o superior (verificado y compatible en Python 3.14).
- **Eclipse SUMO:** Version 1.20.0 o superior (recomendada version 1.28.0).
- **Terminal:** PowerShell, Command Prompt (cmd) o Bash.

---

## Instalacion de Eclipse SUMO

Eclipse SUMO (Simulation of Urban MObility) es el motor de micro-simulacion de codigo abierto utilizado por este proyecto.

Descarga oficial: [https://eclipse.dev/sumo/](https://eclipse.dev/sumo/)

### Instalacion en Windows

1. Ingresa a la seccion de descargas: [https://eclipse.dev/sumo/](https://eclipse.dev/sumo/) -> **Downloads**.
2. Descarga el instalador para Windows de 64 bits: `sumo-win64-<version>.msi`.
3. Ejecuta el archivo `.msi` y sigue el asistente de instalacion. La ruta predeterminada suele ser:
   - `C:\Program Files (x86)\Eclipse\Sumo\` o `C:\Program Files (x86)\SUMO\`
4. **Configurar las variables de entorno (Obligatorio):**
   - Presiona `Win + R`, escribe `sysdm.cpl` y pulsa Enter.
   - Ve a la pestana **Opciones avanzadas** y haz clic en **Variables de entorno**.
   - En **Variables del sistema**, haz clic en **Nueva**:
     - Nombre de la variable: `SUMO_HOME`
     - Valor de la variable: `C:\Program Files (x86)\SUMO` *(o la ruta donde se instalo SUMO)*.
   - En las mismas **Variables del sistema**, busca la variable `Path`, seleccionala y haz clic en **Editar**.
   - Haz clic en **Nuevo** y agrega la ruta a la subcarpeta binaria:
     - `%SUMO_HOME%\bin` *(o `C:\Program Files (x86)\SUMO\bin`)*.
   - Acepta y cierra todas las ventanas.

> **Configuracion rapida desde PowerShell (como Administrador):**
> ```powershell
> [System.Environment]::SetEnvironmentVariable("SUMO_HOME", "C:\Program Files (x86)\SUMO", "Machine")
> $currentPath = [System.Environment]::GetEnvironmentVariable("Path", "Machine")
> if ($currentPath -notlike "*SUMO\bin*") {
>     [System.Environment]::SetEnvironmentVariable("Path", "$currentPath;C:\Program Files (x86)\SUMO\bin", "Machine")
> }
> ```

### Instalacion en Linux (Ubuntu/Debian)

Ejecuta en tu terminal:

```bash
sudo add-apt-repository ppa:sumo/stable
sudo apt-get update
sudo apt-get install sumo sumo-tools sumo-doc

# Configurar SUMO_HOME en tu archivo ~/.bashrc
echo 'export SUMO_HOME="/usr/share/sumo"' >> ~/.bashrc
echo 'export PATH="$SUMO_HOME/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

### Instalacion en macOS

Utilizando Homebrew:

```bash
brew tap dlr-ts/sumo
brew install sumo

# Configurar SUMO_HOME en ~/.zshrc
echo 'export SUMO_HOME="/opt/homebrew/opt/sumo/share/sumo"' >> ~/.zshrc
echo 'export PATH="/opt/homebrew/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

### Verificacion de la Instalacion de SUMO

Abre una **nueva ventana de terminal** y ejecuta:

```bash
sumo --version
netconvert --version
```

Ambos comandos deben responder indicando la version de Eclipse SUMO instalada (por ejemplo, `Eclipse SUMO sumo 1.28.0`).

---

## Instalacion del Entorno Python y Dependencias

Se recomienda utilizar un entorno virtual de Python para aislar las librerias.

### 1. Clonar o abrir el repositorio

```bash
cd D:\Proyectos\ml_proyecto-final
```

### 2. Crear y activar el entorno virtual

- En **Windows (PowerShell)**:
  ```powershell
  python -m venv venv
  .\venv\Scripts\Activate.ps1
  ```
  *(Si PowerShell restringe la ejecucion de scripts, ejecuta una vez: `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`)*

- En **Linux / macOS**:
  ```bash
  python3 -m venv venv
  source venv/bin/activate
  ```

### 3. Instalar librerias requeridas

Instala las dependencias congeladas en `requirements.txt`:

```bash
pip install -r requirements.txt
```

Las librerias principales instaladas son:
- `traci==1.28.0`: Interfaz cliente TraCI para comunicarse por socket TCP con SUMO en bucle cerrado.
- `sumolib==1.28.0`: Utilidades complementarias de SUMO para redes y configuraciones.
- `pandas>=2.2.0`: Procesamiento de datos tabulares y generacion de archivos CSV.
- `matplotlib>=3.8.0`: Generacion de graficos vectoriales y mapas de evaluacion a 300 DPI.
- `numpy>=1.26.0`: Operaciones vectorizadas y calculos estadisticos.

### 4. Validar el entorno con `test.py`

Ejecuta el script de diagnostico:

```bash
python test.py
```

Salida esperada:
```text
[OK] SUMO_HOME detectado en: C:\Program Files (x86)\SUMO\
[OK] Libreria TraCI importada correctamente.
-> Entorno listo para construir la red y el agente.
```

---

## Garantia de Reproducibilidad entre Computadoras

Para asegurar que los resultados numericos y las metricas comparativas sean **exactamente iguales** en cualquier computadora donde se ejecute el proyecto:
1. **Semilla fija en SUMO:** Los comandos de ejecucion de SUMO invocan el parametro `--seed 42`, garantizando que la insercion vehicular, las fluctuaciones de velocidad y el comportamiento del simulador no sufran desvios estocasticos entre corridas.
2. **Semilla fija en Python:** Tanto la generacion de rutas (`generar_rutas.py`), el entrenamiento (`entrenar_agente.py`) y la evaluacion voraz (`evaluar_agente.py`) utilizan `random.seed(42)`.
3. **Politica Voraz Determinista:** Durante la evaluacion experimental, la exploracion se fija en $\epsilon = 0.0$.
4. **Desactivacion de teleport:** Se incluye `--time-to-teleport -1` para evitar que vehiculos en cola sean removidos arbitrariamente por SUMO, asegurando mediciones reales de espera.

---

## Guia de Ejecucion Paso a Paso

Sigue esta secuencia para compilar la red, entrenar el agente, realizar la evaluacion comparativa y generar los reportes.

### Paso 1: Generacion de la Red y Escenarios de Rutas

Si deseas reconstruir la red vial y los archivos XML de rutas:

```bash
# Entrar a la carpeta de simulacion
cd simulacion

# Compilar los archivos de nodos y aristas a formato de red SUMO
netconvert --node-files=red.nod.xml --edge-files=red.edg.xml --output-file=interseccion.net.xml

# Generar los 4 escenarios de trafico (baja, media, alta y desequilibrada)
python generar_rutas.py

# Volver a la raiz del proyecto
cd ..
```

Esto generara los archivos `rutas_baja.rou.xml` (547 veh), `rutas_media.rou.xml` (1430 veh), `rutas_alta.rou.xml` (2879 veh) y `rutas_desequilibrada.rou.xml` (1902 veh).

### Paso 2: Evaluacion de Linea Base (Semaforo Fijo)

Ejecuta la simulacion del semaforo de tiempos fijos (42s verde NS / 3s amarillo / 42s verde EO / 3s amarillo) durante 3600 segundos por cada escenario:

```bash
python evaluar_fijo.py
```

Este proceso generara el archivo [resultados_linea_base.csv](file:///D:/Proyectos/ml_proyecto-final/resultados_linea_base.csv) con las metricas de espera media, cola media, vehiculos ingresados, vehiculos atendidos y cola maxima.

### Paso 3: Entrenamiento del Agente Q-Learning

Entrena al agente a traves de 60 episodios (1200 segundos por episodio) alternando entre los cuatro escenarios de demanda:

```bash
python entrenar_agente.py
```

El script imprimira el progreso cada 5 episodios y generara:
- [q_table.pkl](file:///D:/Proyectos/ml_proyecto-final/q_table.pkl): Tabla Q serializada con los pesos de valor aprendidos.
- [historial_entrenamiento.csv](file:///D:/Proyectos/ml_proyecto-final/historial_entrenamiento.csv): Registro de recompensa acumulada y decaimiento de epsilon por episodio.

### Paso 4: Evaluacion Experimental Comparativa

Evalua el modelo entrenado con exploracion desactivada ($\epsilon = 0.0$) sobre los 4 escenarios a 3600 segundos continuos:

```bash
python evaluar_agente.py
```

El script confrontara directamente el agente contra la linea base fija y generara [resultados_comparativos.csv](file:///D:/Proyectos/ml_proyecto-final/resultados_comparativos.csv), mostrando las reducciones porcentuales y verificando el cumplimiento de los criterios de exito.

### Paso 5: Generacion de Figuras y Graficos

Genera los graficos de publicacion en formato PNG a 300 DPI:

```bash
python generar_graficos.py
```

Las figuras se almacenaran en la carpeta `graficos/`:
- `graficos/convergencia_entrenamiento.png`: Curva de recompensa y media movil por episodio.
- `graficos/comparativa_espera.png`: Grafico de barras con porcentaje de reduccion en tiempos de espera.
- `graficos/comparativa_colas.png`: Grafico de barras comparativo de longitud media de cola.

---

## Visualizacion Interactiva en SUMO-GUI

Para observar visualmente el comportamiento de los vehiculos y el semaforo interactuando en la interfaz grafica:

```bash
sumo-gui -c simulacion/simulacion.sumocfg
```

1. Se abrira la ventana interactiva de SUMO mostrando la interseccion en cruz de dos carriles por sentido.
2. En la barra de herramientas superior, ajusta el control **Delay** a `50` o `100` ms para observar la circulacion a una velocidad adecuada para el ojo humano.
3. Haz clic en el boton **Play** (icono de triangulo verde) para iniciar la simulacion.

---

## Resultados Experimentales Obtenidos

Tabla resumen extraida de [resultados_comparativos.csv](file:///D:/Proyectos/ml_proyecto-final/resultados_comparativos.csv):

| Escenario de Demanda | Espera Fijo (s/veh) | Espera Q-Learning (s/veh) | Reduccion de Espera (%) | Meta Espera ($\ge 15\%$) | Cola Fijo (veh) | Cola Q-Learning (veh) | Reduccion de Cola (%) | Meta Cola ($\ge 10\%$) | Atendidos (Fijo vs QL) | Infracciones Seguridad |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Baja** | 10.44 | 4.24 | **-59.39 %** | Cumplido | 1.61 | 0.66 | **-59.01 %** | Cumplido | 536 / 536 | **0** |
| **Media** | 10.87 | 4.01 | **-63.11 %** | Cumplido | 4.37 | 1.61 | **-63.16 %** | Cumplido | 1408 / 1408 | **0** |
| **Alta** | 12.26 | 3.58 | **-70.80 %** | Cumplido | 9.83 | 2.88 | **-70.70 %** | Cumplido | 2828 / **2831** | **0** |
| **Desequilibrada** | 12.61 | 3.43 | **-72.80 %** | Cumplido | 6.68 | 1.82 | **-72.75 %** | Cumplido | 1871 / **1879** | **0** |

Para un analisis academico extendido de la metodologia y resultados vinculados a los Objetivos Especificos (OE1, OE2, OE3), consulta el documento [resumen_secciones_3_y_4.md](file:///D:/Proyectos/ml_proyecto-final/resumen_secciones_3_y_4.md).

---

## Solucion de Problemas Frecuentes

### 1. `Error: No se encontro la variable SUMO_HOME en el sistema`
- Causa: La variable de entorno `SUMO_HOME` no esta definida o la terminal actual se abrio antes de configurar la variable.
- Solucion: Cierra todas las terminales, verifica que `SUMO_HOME` apunte al directorio base de SUMO (por ejemplo, `C:\Program Files (x86)\SUMO`) y abre una nueva ventana de terminal. En PowerShell puedes probar temporalmente con:
  ```powershell
  $env:SUMO_HOME = "C:\Program Files (x86)\SUMO"
  ```

### 2. `Error: No se pudo importar TraCI`
- Causa: La libreria `traci` no esta instalada en el interprete de Python activo.
- Solucion: Verifica que el entorno virtual este activado y ejecuta:
  ```bash
  pip install traci==1.28.0
  ```

### 3. `netconvert` o `sumo` no se reconocen como un comando interno o externo
- Causa: La carpeta `bin` de SUMO no se encuentra en la variable `Path` del sistema.
- Solucion: Agrega `%SUMO_HOME%\bin` a la variable de entorno `Path` del sistema y reinicia la terminal.

### 4. Permisos de ejecucion en PowerShell (`ExecutionPolicy`)
- Causa: Windows bloquea por defecto la activacion de entornos virtuales (`Activate.ps1`).
- Solucion: Ejecuta en la sesion actual:
  ```powershell
  Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
  ```
