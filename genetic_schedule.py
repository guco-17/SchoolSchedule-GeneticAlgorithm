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
        (random.randrange(NUM_AULAS), random.randrange(NUM_HORARIOS)) for _ in range(N)
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

#--------------------------------
#SELECCIÓN, CRUCE Y MUTACIÓN

def seleccion_torneo(poblacion, fitness, k=3):
    candidatos = random.sample(range(len(poblacion)), k)
    ganador = max(candidatos, key=lambda idx: fitness[idx])
    return poblacion[ganador]

def cruce_uniforme_por_bloques(padre1, padre2, pc=0.8):
    if random.random() > pc:
        return padre1[:], padre2[:]
    hijo1, hijo2 = [], []
    for gen1, gen2 in zip(padre1, padre2):
        if random.randint(0,1) == 0:
            hijo1.append(gen1); hijo2.append(gen2)
        else:
            hijo1.append(gen2); hijo2.append(gen1)
    return hijo1, hijo2

def mutar(cromosoma, pm= 0.03):
    cromosoma = cromosoma[:]
    for i in range(len(cromosoma)):
        if random.random() < pm:
            r, h = cromosoma[i]
            if random.random() < 0.5:
                r = random.randrange(NUM_AULAS)
            else:
                h = random.randrange(NUM_HORARIOS)
            cromosoma[i] = (r, h)
    if random.random() < pm:
        i, j = random.sample(range(len(cromosoma)), 2)
        cromosoma[i], cromosoma[j] = cromosoma[j], cromosoma[i]
    return cromosoma

#--------------------------------
#CICLO EVOLUTIVO

def ejecutar_algoritmo(tam_poblacion = 120, generaciones = 400, elite_pct = 0.05):
    poblacion = [cromosoma_aleatorio() for _ in range(tam_poblacion)]
    n_elite = max(1, int(tam_poblacion * elite_pct))

    mejor_global, mejor_fitness_global = None, -1

    for gen in range(1, generaciones + 1):
        evaluados = [aptitud(c) for c in poblacion]
        fitnesses = [e[0] for e in evaluados]

        idx_mejor = max(range(tam_poblacion), key=lambda i: fitnesses[i])
        if fitnesses[idx_mejor] > mejor_fitness_global:
            mejor_fitness_global = fitnesses[idx_mejor]
            mejor_global = poblacion[idx_mejor]
            duras_mejor, blandas_mejor = evaluados[idx_mejor][1], evaluados[idx_mejor][2]

        if gen == 1 or gen % 25 == 0 or mejor_fitness_global == 1.0:
            print(f"Gen {gen:4d} | mejor fitness = {mejor_fitness_global:.5f} "
                    f"| duras = {duras_mejor} | blandas = {blandas_mejor}")

        if mejor_fitness_global == 1.0:
            break

        orden = sorted(range(tam_poblacion), key=lambda i: fitnesses[i], reverse=True)
        nueva_poblacion = [poblacion[i][:] for i in orden[:n_elite]]

        while len(nueva_poblacion) < tam_poblacion:
            p1 = seleccion_torneo(poblacion, fitnesses)
            p2 = seleccion_torneo(poblacion, fitnesses)
            h1, h2 = cruce_uniforme_por_bloques(p1, p2)
            h1, h2 = mutar(h1), mutar(h2)
            nueva_poblacion.append(h1)
            if len(nueva_poblacion) < tam_poblacion:
                nueva_poblacion.append(h2)

        poblacion = nueva_poblacion

    return mejor_global, mejor_fitness_global

def imprimir_muestra(cromosoma, n = 10):
    print(f"\nMuestra de {n} sesiones del horario encontrado:")
    for i in range(min(n, N)):
        r, h = cromosoma[i]
        s, aula, horario = SESIONES[i], AULAS[r], HORARIOS[h]
        print(f"  {s['grupo']:>6} | {s['materia']:<30} | Prof. {s['profesor']:<30} "
                f"-> {aula['id']} ({aula['tipo']}) | {horario['dia']} {horario['inicio']}-{horario['fin']}")


if __name__ == "__main__":
    mejor, fit = ejecutar_algoritmo()
    print(f"\nMejor fitness final: {fit:.5f}")
    imprimir_muestra(mejor)