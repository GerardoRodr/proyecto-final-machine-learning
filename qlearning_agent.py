import random
import pickle
from collections import defaultdict

class QLearningAgent:
    def __init__(self, alpha_lr=0.1, gamma_df=0.95, epsilon=1.0, epsilon_min=0.01, decay=0.96):
        self.alpha_lr = alpha_lr
        self.gamma_df = gamma_df
        self.epsilon = epsilon
        self.epsilon_min = epsilon_min
        self.decay = decay
        
        # Tabla Q inicializada con ceros para cada accion (0: mantener, 1: cambiar)
        self.q_table = defaultdict(lambda: [0.0, 0.0])

    @staticmethod
    def categorizar_cola(vehiculos):
        if vehiculos <= 3:
            return "BAJA"
        elif vehiculos <= 8:
            return "MEDIA"
        return "ALTA"

    @staticmethod
    def categorizar_tiempo(segundos):
        if segundos < 15:
            return "CORTO"
        elif segundos <= 35:
            return "MEDIO"
        return "LARGO"

    def discretizar_estado(self, cola_ns, cola_eo, fase_activa, tiempo_en_fase):
        q_ns = self.categorizar_cola(cola_ns)
        q_eo = self.categorizar_cola(cola_eo)
        t_fase = self.categorizar_tiempo(tiempo_en_fase)
        return (q_ns, q_eo, fase_activa, t_fase)

    def elegir_accion(self, estado, epsilon=None):
        eps = self.epsilon if epsilon is None else epsilon
        if random.random() < eps:
            return random.choice([0, 1])
        
        q_valores = self.q_table[estado]
        if q_valores[0] == q_valores[1]:
            return random.choice([0, 1])
        return 0 if q_valores[0] > q_valores[1] else 1

    def aprender(self, estado, accion, recompensa, siguiente_estado, finalizado=False):
        q_actual = self.q_table[estado][accion]
        if finalizado:
            target = recompensa
        else:
            max_siguiente = max(self.q_table[siguiente_estado])
            target = recompensa + self.gamma_df * max_siguiente
            
        td_error = target - q_actual
        self.q_table[estado][accion] += self.alpha_lr * td_error

    def decaer_epsilon(self):
        if self.epsilon > self.epsilon_min:
            self.epsilon = max(self.epsilon_min, self.epsilon * self.decay)

    def guardar_politica(self, ruta_archivo):
        # Convertir a dict normal para serializacion limpia
        data = {
            "q_table": dict(self.q_table),
            "alpha_lr": self.alpha_lr,
            "gamma_df": self.gamma_df,
            "epsilon": self.epsilon
        }
        with open(ruta_archivo, "wb") as f:
            pickle.dump(data, f)

    def cargar_politica(self, ruta_archivo):
        with open(ruta_archivo, "rb") as f:
            data = pickle.load(f)
        self.q_table = defaultdict(lambda: [0.0, 0.0], data["q_table"])
        self.alpha_lr = data.get("alpha_lr", self.alpha_lr)
        self.gamma_df = data.get("gamma_df", self.gamma_df)
        self.epsilon = data.get("epsilon", self.epsilon_min)
