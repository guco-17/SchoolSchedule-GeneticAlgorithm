import csv
import random

random.seed(7)

#--------------------------------
#DEFINICION DE FUNCIONES PARA CARGAR LOS DATOS DEL DATASET AL ALGORITMO

def cargar_aulas(path="./dataset/aulas.csv"):
    aulas = []
    with open(path, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            aulas.append({
                "id": row["aula_id"],
                "tipo": row["tipo"],
                "capacidad": int(row["capacidad_estimada"])
            })
    return aulas

def cargar_horarios(path="./dataset/horarios.csv"):
    horarios = []
    with open(path, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            horarios.append({
                "id": row["horario_id"],
                "dia": row["dia"],
                "inicio": row["hora_inicio"],
                "fin": row["hora_fin"],
            })
    return horarios

def cargar_sesiones(path="./dataset/clases.csv"):
    sesiones = []
    with open(path, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            n = int(row["num_sesiones_requeridas"])
            for k in range(n):
                sesiones.append({
                    "clase_id": row["clase_id"],
                    "grupo": row["grupo"],
                    "materia": row["materia"],
                    "profesor": row["profesor"],
                    "alumnos": int(row["alumnos_estimado"]),
                    "tipo_requerido": row["tipo_aula_requerido"],
                    "sesion_num": k + 1,
                })
    return sesiones

#--------------------------------
#DEFINIR LAS VARIABLES GLOBALES DEL DATASET PARA EL ALGORITMO

AULAS = cargar_aulas()
HORARIOS = cargar_horarios()
SESIONES = cargar_sesiones()
W_H = 10.0
W_S = 1.0

N = len(SESIONES)
NUM_AULAS = len(AULAS)
NUM_HORARIOS = len(HORARIOS)

print(f"Cargado: {len(AULAS)} aulas | {len(HORARIOS)} horarios | "
        f"{N} sesiones a programar (de {len(set(s['clase_id'] for s in SESIONES))} clases)")

#--------------------------------
#CROMOSOMA: TUPLA aula_id, horario_id por sesion

def cromosoma_aleatorio():
    return[
        {random.randrange(NUM_AULAS), random.randrange(NUM_HORARIOS)} for _ in range(N)
    ]

#--------------------------------
#FUNCIÓN DE APTITUD

def aptitud(cromosoma):
    #RESTRICCIONES
    duras = 0
    blandas = 0

    #AGRUPAR POR HORARIO PARA DETECTAR CHOQUES SIN COMPARAR TODO CONTRA TODO
    por_horario ={}

    for i in range (N):
        r_i, h_i = cromosoma[i]
        por_horario.setdefault(h_i, []).append(i)

        sesion_i = SESIONES[i]
        aula_i = AULAS[r_i]

        if sesion_i["alumnos"] > aula_i["capacidad"]:
            duras += 1
        if sesion_i["tipo_requerido"] != aula_i["tipo"]:
            blandas += 1
        if aula_i["capacidad"] - sesion_i["alumnos"] > 15:
            blandas += 1

    for h_i, indices in por_horario.items():
        for a in range(len(indices)):
            for b in range(a + 1, len(indices)):
                i, j = indices[a], indices[b]
                r_i, _ = cromosoma[i]
                r_j, _ = cromosoma[j]
                sesion_i, sesion_j = SESIONES[i], SESIONES[j]

                if r_i == r_j:
                    duras += 1
                if sesion_i["profesor"] == sesion_j["profesor"]:
                    duras += 1
                if sesion_i["grupo"] == sesion_j["grupo"]:
                    duras += 1
                if sesion_i["clase_id"] == sesion_j["clase_id"]:
                    duras += 1

    costo = W_H * duras + W_S * blandas
    fitness = 1.0 / (1.0 + costo)
    return fitness, duras, blandas