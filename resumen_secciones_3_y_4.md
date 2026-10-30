# Informe Tecnico Experimental: Secciones 3 (Metodologia) y 4 (Resultados)

**Proyecto:** Sistema Inteligente de Control Semaforico mediante Aprendizaje por Refuerzo Tabular (Q-Learning) en Micro-simulacion SUMO  
**Entorno:** Eclipse SUMO v1.28.0 + TraCI en Python 3.14  
**Fecha:** Octubre 2026  

---

## 1. Alineacion con los Objetivos del Proyecto

- **Objetivo General:** Disenar, implementar y evaluar un sistema de control semaforico adaptativo basado en Q-learning tabular que optimice el flujo vehicular en una interseccion semaforizada de 2 ejes y 2 carriles por sentido, superando significativamente el desempeno del controlador de tiempos fijos.
- **Objetivo Especifico 1 (OE1):** Reducir el tiempo medio de espera vehicular en al menos un 15 % respecto a la linea base de tiempos fijos en todos los escenarios de demanda.
- **Objetivo Especifico 2 (OE2):** Disminuir la longitud media de cola y la cola maxima acumulada en al menos un 10 % respecto al controlador fijo.
- **Objetivo Especifico 3 (OE3):** Mantener o incrementar el rendimiento de vehiculos atendidos (throughput) garantizando cero infracciones de seguridad operativa (tiempos minimos de verde y transiciones de amarillo obligatorias).

---

## 2. Seccion 3: Metodologia

### 3.1 Modelado de la Red Vial y Escenarios en SUMO
La red representa una interseccion ortogonal semaforizada compuesta por dos ejes principales:
- **Eje Norte - Sur (NS):** Tramos `N2C` (ingreso norte, 2 carriles, 300 m, 50 km/h) y `S2C` (ingreso sur, 2 carriles, 300 m, 50 km/h) convergiendo en el cruce central `C`. Salidas correspondientes `C2S` y `C2N`.
- **Eje Este - Oeste (EO):** Tramos `E2C` (ingreso este, 2 carriles, 300 m, 50 km/h) y `W2C` (ingreso oeste, 2 carriles, 300 m, 50 km/h). Salidas correspondientes `C2W` y `C2E`.
- **Controlador Semaforico:** Identificador `C`, gestionando las fases:
  - Fase 0: Verde NS (`GGGggrrrrrGGGggrrrrr`)
  - Fase 1: Amarillo NS (`yyyyyrrrrryyyyyrrrrr`, 3 s)
  - Fase 2: Verde EO (`rrrrrGGGggrrrrrGGGgg`)
  - Fase 3: Amarillo EO (`rrrrryyyyyrrrrryyyyy`, 3 s)

Se modelaron cuatro escenarios de demanda durante 3600 segundos (1 hora continua de simulacion):
1. **Baja Demanda (`rutas_baja.rou.xml`):** Tasa de insercion $P_{NS} = 0.08$, $P_{EO} = 0.08$ (547 vehiculos totales).
2. **Media Demanda (`rutas_media.rou.xml`):** Tasa de insercion $P_{NS} = 0.20$, $P_{EO} = 0.20$ (1430 vehiculos totales).
3. **Alta Demanda (`rutas_alta.rou.xml`):** Tasa de insercion $P_{NS} = 0.40$, $P_{EO} = 0.40$ (2879 vehiculos totales).
4. **Demanda Desequilibrada (`rutas_desequilibrada.rou.xml`):** Tasa de insercion $P_{NS} = 0.45$, $P_{EO} = 0.08$ (1902 vehiculos totales, representando saturacion asimetrica).

### 3.2 Formulacion del Agente de Aprendizaje por Refuerzo (Q-Learning)

#### A. Espacio de Estados Discreto ($s \in \mathcal{S}$)
El estado captura la condicion instantanea de congestion y la fase semaforica activa mediante la tupla:
$$s = (q_{NS},\, q_{EO},\, \text{fase\_activa},\, \text{tiempo\_en\_fase})$$
- $q_{NS} \in \{\text{'BAJA'} \le 3\text{ veh},\, \text{'MEDIA' } [4-8]\text{ veh},\, \text{'ALTA'} > 8\text{ veh}\}$: Vehiculos detenidos ($\text{vel} < 0.1\text{ m/s}$) en `N2C` y `S2C`.
- $q_{EO} \in \{\text{'BAJA'} \le 3\text{ veh},\, \text{'MEDIA' } [4-8]\text{ veh},\, \text{'ALTA'} > 8\text{ veh}\}$: Vehiculos detenidos en `E2C` y `W2C`.
- $\text{fase\_activa} \in \{\text{'NS'}, \text{'EO'}\}$: Eje que posee derecho de paso.
- $\text{tiempo\_en\_fase} \in \{\text{'CORTO'} < 15\text{ s},\, \text{'MEDIO' } [15-35]\text{ s},\, \text{'LARGO'} \ge 35\text{ s}\}$: Duracion acumulada de la fase verde actual.
- **Cardinalidad del espacio:** $|\mathcal{S}| = 3 \times 3 \times 2 \times 3 = 54$ estados posibles, permitiendo una convergencia tabular rapida, exacta y sin necesidad de redes neuronales profundas propensas a inestabilidad.

#### B. Espacio de Acciones y Modulo de Seguridad ($a \in \{0, 1\}$)
- Acción $0$: Mantener la fase verde actual.
- Acción $1$: Solicitar cambio de fase hacia el eje transversal.
- **Restricciones fisicas de seguridad incorporadas:**
  - *Tiempo minimo de verde:* 10 segundos obligatorios. Si el tiempo transcurrido es menor a 10 s, cualquier solicitud de cambio se anula forzando la accion 0.
  - *Tiempo maximo de verde:* 60 segundos continuos. Al alcanzarse este limite se fuerza la accion 1 para evitar inanicion (starvation) de la via perpendicular.
  - *Transicion de amarillo garantizada:* Al cambiar de fase verde, se interpone una fase de amarillo de 3 segundos exactos antes de liberar el verde opuesto, eliminando riesgos de colision por frenado intempestivo.

#### C. Funcion de Recompensa
$$r_t = -\left[ \alpha \cdot \frac{W_t}{10} + \beta \cdot Q_t + \gamma \cdot P_t \right]$$
donde:
- $W_t$: Tiempo de espera acumulado (s) de todos los vehiculos en los 4 accesos de entrada.
- $Q_t$: Cantidad total de vehiculos detenidos en la interseccion.
- $P_t$: Penalizacion por equidad, correspondiente al numero de vehiculos individuales con tiempo de espera superior a 60 segundos.
- Coeficientes calibrados: $\alpha = 0.5$, $\beta = 1.0$, $\gamma = 2.0$.

#### D. Actualizacion de Bellman y Politica de Exploracion
$$Q(s_t, a_t) \leftarrow Q(s_t, a_t) + \alpha_{lr} \left[ r_t + \gamma_{df} \max_{a} Q(s_{t+1}, a) - Q(s_t, a_t) \right]$$
- Tasa de aprendizaje: $\alpha_{lr} = 0.1$
- Factor de descuento: $\gamma_{df} = 0.95$
- Politica: $\epsilon$-greedy con decaimiento geometrico $\epsilon_{k+1} = \max(0.01, \epsilon_k \times 0.95)$ a lo largo de 60 episodios.

---

## 3. Seccion 4: Resultados Experimentales y Discusion

### 4.1 Tablas Comparativas Oficiales (Listas para Word)

#### Tabla 4.1: Comparativa General de Desempeno: Controlador Fijo vs. Agente Q-Learning

| Escenario de Demanda | Tiempo Espera Fijo (s/veh) | Tiempo Espera Q-Learning (s/veh) | Reduccion Espera (%) | Meta Espera ($\ge 15\%$) | Longitud Cola Fijo (veh) | Longitud Cola Q-Learning (veh) | Reduccion Cola (%) | Meta Cola ($\ge 10\%$) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Baja** | 10.44 | 4.24 | **-59.39 %** | Cumplido | 1.61 | 0.66 | **-59.01 %** | Cumplido |
| **Media** | 10.87 | 4.01 | **-63.11 %** | Cumplido | 4.37 | 1.61 | **-63.16 %** | Cumplido |
| **Alta** | 12.26 | 3.58 | **-70.80 %** | Cumplido | 9.83 | 2.88 | **-70.70 %** | Cumplido |
| **Desequilibrada** | 12.61 | 3.43 | **-72.80 %** | Cumplido | 6.68 | 1.82 | **-72.75 %** | Cumplido |

#### Tabla 4.2: Rendimiento Operativo, Capacidad y Verificacion de Seguridad

| Escenario | Vehiculos Ingresados | Vehiculos Atendidos (Fijo) | Vehiculos Atendidos (Q-Learning) | Cola Maxima (Fijo) | Cola Maxima (Q-Learning) | Reduccion Cola Maxima | Infracciones de Seguridad |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Baja** | 547 | 536 | 536 | 9 veh | 4 veh | **-55.6 %** | **0** |
| **Media** | 1430 | 1408 | 1408 | 15 veh | 9 veh | **-40.0 %** | **0** |
| **Alta** | 2879 | 2828 | 2831 | 27 veh | 12 veh | **-55.6 %** | **0** |
| **Desequilibrada** | 1902 | 1871 | 1879 | 29 veh | 16 veh | **-44.8 %** | **0** |

---

### 4.2 Analisis Detallado por Objetivos

#### A. Analisis de Reduccion en Tiempos de Espera (OE1)
El agente Q-learning supero ampliamente el umbral meta del 15 % en los 4 escenarios evaluados:
- En demanda **baja**, la reduccion fue del **59.39 %** (de 10.44 s a 4.24 s).
- En demanda **media**, alcanzo una reduccion del **63.11 %** (de 10.87 s a 4.01 s).
- En demanda **alta**, la reduccion alcanzo el **70.80 %** (de 12.26 s a 3.58 s).
- En el escenario **desequilibrado**, la optimizacion registro su mayor impacto con una reduccion del **72.80 %** (de 12.61 s a 3.43 s).

*Interpretacion tecnica:* El semaforo de tiempos fijos asigna sistematicamente 42 segundos de verde a cada eje, independientemente de si hay vehiculos esperando. En contraste, el agente Q-learning detecta de inmediato cuando un peloton de vehiculos ha terminado de cruzar (`q_fase == 'BAJA'`) y conmuta oportunamente el derecho de paso al eje donde la cola comienza a formarse, eliminando tiempos muertos de verde desperdiciado.

#### B. Analisis de Longitudes de Cola y Colas Maximas (OE2)
El criterio de exito requeria reducir la longitud media de cola en al menos un 10 %:
- El agente logro una disminucion del **59.01 %** en demanda baja, **63.16 %** en media, **70.70 %** en alta y **72.75 %** en desequilibrada.
- Respecto a la **cola maxima instantanea**, el controlador fijo alcanzo picos de hasta 27 vehiculos en alta y 29 vehiculos en desequilibrada, mientras que el agente Q-learning contuvo la cola maxima en 12 vehiculos (reduccion del 55.6 %) y 16 vehiculos (reduccion del 44.8 %) respectivamente. En baja demanda la redujo de 9 a 4 vehiculos (-55.6 %) y en media de 15 a 9 vehiculos (-40.0 %).

*Interpretacion tecnica:* Al modular la duracion del verde dinamicamente entre 10 s y 60 s segun el estado discreto, el agente previene la acumulacion de vehiculos en los accesos de alta carga (Norte-Sur), impidiendo que las colas se propaguen aguas arriba hacia los limites de la red.

#### C. Rendimiento y Seguridad Vial (OE3)
- **Tasa de atencion (throughput):** El numero de vehiculos atendidos se mantuvo en niveles equivalentes o superiores: 536 vs 536 en baja, 1408 vs 1408 en media, **2831 vs 2828 (+3 vehiculos) en alta**, y **1879 vs 1871 (+8 vehiculos) en el escenario desequilibrado**.
- **Seguridad operativa estricta:** En los 4 escenarios de evaluacion (14,400 segundos totales de operacion en bucle cerrado) se registraron **0 infracciones de seguridad**:
  - Ninguna fase verde duro menos de 10 segundos continuos.
  - Ninguna fase verde supero los 60 segundos de permanencia forzosa.
  - El 100 % de los cambios de verde a verde se mediaron por 3 segundos de transicion amarilla, garantizando seguridad vehicular total.

#### D. Cumplimiento del Objetivo General
La integracion entre el algoritmo de Q-learning tabular y TraCI demuestra cuantitativamente que el control adaptativo cerrado supera contundentemente al esquema de tiempos fijos tradicional, logrando descongestion instantanea y adaptabilidad precisa a condiciones de flujo asimetrico sin incurrir en complejidad computacional excesiva.

---

## 4. Registro de Figuras Generadas

Las siguientes figuras fueron producidas en resolucion de 300 DPI en la carpeta `graficos/`:
1. `graficos/convergencia_entrenamiento.png`: Curva de evolucion de recompensa acumulada por episodio y decaimiento de epsilon, demostrando estabilizacion del aprendizaje a partir del episodio 35.
2. `graficos/comparativa_espera.png`: Grafico de barras comparativo de tiempo medio de espera vehicular (s/veh) con etiquetas de porcentaje de reduccion.
3. `graficos/comparativa_colas.png`: Grafico de barras comparativo de longitud media de cola (veh) con etiquetas de reduccion.
