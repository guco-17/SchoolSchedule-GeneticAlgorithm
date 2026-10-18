import csv
import os
import random

#--------------------------------
#PARAMETROS AJUSTABLES (poner en 0 / False para desactivar una mejora y comparar)

SEMILLA_DEFECTO = 7
W_H = 10.0               # peso de restricciones duras
W_S = 1.0                # peso de restricciones blandas
HOLGURA_MAX = 15         # holgura maxima aceptable entre capacidad del aula y alumnos
USAR_TURNO = True        # grupos Diurnos solo en franjas de manana, Nocturnos solo en tarde/noche
N_MEMETICO = 4           # individuos por generacion a los que se aplica reparacion local (0 = desactivar)
PM_BASE = 0.01           # prob. de mutacion por gen para sesiones SIN conflicto
PM_CONFLICTO = 0.35      # prob. de mutacion por gen para sesiones EN conflicto (mutacion dirigida)

random.seed(SEMILLA_DEFECTO)

#--------------------------------
#DEFINICION DE FUNCIONES PARA CARGAR LOS DATOS DEL DATASET AL ALGORITMO

def _ruta(nombre):
    """Busca el CSV en ./dataset/, junto al script, o en el directorio actual."""
    base = os.path.dirname(os.path.abspath(__file__))
    for carpeta in (os.path.join(base, "dataset"), base, os.path.join(os.getcwd(), "dataset"), os.getcwd()):
        p = os.path.join(carpeta, nombre)
        if os.path.exists(p):
            return p
    raise FileNotFoundError(f"No se encontro {nombre}")

def cargar_aulas(path=None):
    aulas = []
    with open(path or _ruta("aulas.csv"), encoding="utf-8") as f:
        for row in csv.DictReader(f):
            aulas.append({
                "id": row["aula_id"],
                "tipo": row["tipo"],
                "capacidad": int(row["capacidad_estimada"])
            })
    return aulas

def cargar_horarios(path=None):
    horarios = []
    with open(path or _ruta("horarios.csv"), encoding="utf-8") as f:
        for row in csv.DictReader(f):
            horarios.append({
                "id": row["horario_id"],
                "dia": row["dia"],
                "inicio": row["hora_inicio"],
                "fin": row["hora_fin"],
            })
    return horarios

def cargar_sesiones(path=None):
    sesiones = []
    with open(path or _ruta("clases.csv"), encoding="utf-8") as f:
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
                    "turno": row.get("turno_inferido", ""),
                    "sesion_num": k + 1,
                })
    return sesiones

#--------------------------------
#DEFINIR LAS VARIABLES GLOBALES DEL DATASET PARA EL ALGORITMO

AULAS = cargar_aulas()
HORARIOS = cargar_horarios()
SESIONES = cargar_sesiones()

N = len(SESIONES)
NUM_AULAS = len(AULAS)
NUM_HORARIOS = len(HORARIOS)

print(f"Cargado: {len(AULAS)} aulas | {len(HORARIOS)} horarios | "
        f"{N} sesiones a programar (de {len(set(s['clase_id'] for s in SESIONES))} clases)")

#--------------------------------
#PRECALCULOS (se hacen una sola vez; aceleran todo el algoritmo)

def _minutos(hhmm):
    h, m = hhmm.split(":")
    return int(h) * 60 + int(m)

# 1) Matriz de traslape entre franjas: dos franjas chocan si son el mismo dia y sus rangos se cruzan.
#    (el codigo original solo detectaba choques con el MISMO horario_id)
_DIAS = {d: k for k, d in enumerate(dict.fromkeys(h["dia"] for h in HORARIOS))}
DIA = [_DIAS[h["dia"]] for h in HORARIOS]
_ini = [_minutos(h["inicio"]) for h in HORARIOS]
_fin = [_minutos(h["fin"]) for h in HORARIOS]
SOLAPA = [
    [DIA[a] == DIA[b] and _ini[a] < _fin[b] and _ini[b] < _fin[a] for b in range(NUM_HORARIOS)]
    for a in range(NUM_HORARIOS)
]

# 2) Franjas validas por sesion (turno) y aulas validas por sesion (tipo + capacidad).
def _turno_franja(h):
    return "Diurno" if _ini[h] < 13 * 60 else "Nocturno"

HORARIOS_VALIDOS = []
for s in SESIONES:
    v = [h for h in range(NUM_HORARIOS) if _turno_franja(h) == s["turno"]] if USAR_TURNO else []
    HORARIOS_VALIDOS.append(v or list(range(NUM_HORARIOS)))

AULAS_VALIDAS = []
for s in SESIONES:
    v = [k for k, a in enumerate(AULAS)
         if a["tipo"] == s["tipo_requerido"] and a["capacidad"] >= s["alumnos"]]
    if not v:  # ninguna aula cumple tipo Y capacidad: se prioriza la capacidad (restriccion dura)
        v = [k for k, a in enumerate(AULAS) if a["capacidad"] >= s["alumnos"]]
    AULAS_VALIDAS.append(v or list(range(NUM_AULAS)))

HORARIOS_VALIDOS_SET = [set(v) for v in HORARIOS_VALIDOS]

# 3) Penalizaciones por (sesion, aula) en tablas: evita recalcular comparaciones en cada evaluacion.
DURA_AULA = [[1 if s["alumnos"] > a["capacidad"] else 0 for a in AULAS] for s in SESIONES]
BLANDA_AULA = [
    [(1 if s["tipo_requerido"] != a["tipo"] else 0)
     + (1 if a["capacidad"] - s["alumnos"] > HOLGURA_MAX else 0) for a in AULAS]
    for s in SESIONES
]

# 4) Relaciones fijas entre sesiones (no dependen del cromosoma).
#    - pares que comparten profesor o grupo: no pueden traslaparse (dura)
#    - sesiones de una misma clase: conviene que caigan en dias distintos (blanda)
_pares = [(i, j) for i in range(N) for j in range(i + 1, N)
          if SESIONES[i]["profesor"] == SESIONES[j]["profesor"]
          or SESIONES[i]["grupo"] == SESIONES[j]["grupo"]]
PARES_FIJOS = _pares
ADY = [[] for _ in range(N)]
for i, j in _pares:
    ADY[i].append(j)
    ADY[j].append(i)

_por_clase = {}
for i, s in enumerate(SESIONES):
    _por_clase.setdefault(s["clase_id"], []).append(i)
CLASES_IDX = list(_por_clase.values())
VEC_CLASE = [[] for _ in range(N)]
CLASES_MULTI = []
for idxs in CLASES_IDX:
    if len(idxs) > 1:
        CLASES_MULTI.append(idxs)
        for i in idxs:
            VEC_CLASE[i] = [j for j in idxs if j != i]

# 5) Cota inferior de costo imposible de evitar por los datos (p.ej. 35 alumnos y labs de 32 plazas).
_min_costos = [min((W_H * DURA_AULA[i][r] + W_S * BLANDA_AULA[i][r], DURA_AULA[i][r], BLANDA_AULA[i][r])
                   for r in AULAS_VALIDAS[i]) for i in range(N)]
COSTO_MINIMO = sum(m[0] for m in _min_costos)
DURAS_INEVITABLES = sum(m[1] for m in _min_costos)
BLANDAS_INEVITABLES = sum(m[2] for m in _min_costos)

print(f"Espacio reducido: {sum(len(v) for v in AULAS_VALIDAS)/N:.1f} aulas y "
        f"{sum(len(v) for v in HORARIOS_VALIDOS)/N:.1f} franjas candidatas por sesion (de {NUM_AULAS} y {NUM_HORARIOS}) | "
        f"minimo inevitable por los datos: duras = {DURAS_INEVITABLES}, blandas = {BLANDAS_INEVITABLES}")

#--------------------------------
#CROMOSOMA: TUPLA aula_id, horario_id por sesion (solo con valores validos para esa sesion)

def cromosoma_aleatorio():
    return [(random.choice(AULAS_VALIDAS[i]), random.choice(HORARIOS_VALIDOS[i])) for i in range(N)]

#--------------------------------
#FUNCIÓN DE APTITUD (O(N + pares) en lugar de comparar todo contra todo)

def _analizar(c, detalle=False):
    """Devuelve (duras, blandas, conflictivas). 'conflictivas' = indices de sesiones involucradas en
    alguna violacion (solo se calcula si detalle=True)."""
    duras = blandas = 0
    conf = set() if detalle else None
    por_aula = {}

    for i in range(N):
        r, h = c[i]
        if DURA_AULA[i][r]:
            duras += 1
            if detalle: conf.add(i)
        blandas += BLANDA_AULA[i][r]
        por_aula.setdefault(r, []).append(i)

    # choques de aula: misma aula con franjas traslapadas
    for lista in por_aula.values():
        for a in range(len(lista)):
            i = lista[a]
            sol = SOLAPA[c[i][1]]
            for b in range(a + 1, len(lista)):
                j = lista[b]
                if sol[c[j][1]]:
                    duras += 1
                    if detalle: conf.add(i); conf.add(j)

    # choques de profesor / grupo (pares fijos): franjas traslapadas
    for i, j in PARES_FIJOS:
        if SOLAPA[c[i][1]][c[j][1]]:
            duras += 1
            if detalle: conf.add(i); conf.add(j)

    # blanda: sesiones de una misma clase el mismo dia
    for idxs in CLASES_MULTI:
        for a in range(len(idxs)):
            for b in range(a + 1, len(idxs)):
                i, j = idxs[a], idxs[b]
                if DIA[c[i][1]] == DIA[c[j][1]]:
                    blandas += 1
                    if detalle: conf.add(i); conf.add(j)

    return duras, blandas, conf

def aptitud(cromosoma):
    duras, blandas, _ = _analizar(cromosoma)
    costo = W_H * duras + W_S * blandas
    fitness = 1.0 / (1.0 + costo)
    return fitness, duras, blandas

def _costo_local(c, i):
    """Costo de todas las violaciones que involucran a la sesion i (para evaluar cambios en O(N))."""
    r, h = c[i]
    d = DURA_AULA[i][r]
    b = BLANDA_AULA[i][r]
    sol = SOLAPA[h]
    for j in ADY[i]:
        if sol[c[j][1]]:
            d += 1
    for j in range(N):
        if j != i and c[j][0] == r and sol[c[j][1]]:
            d += 1
    dia = DIA[h]
    for j in VEC_CLASE[i]:
        if DIA[c[j][1]] == dia:
            b += 1
    return W_H * d + W_S * b

#--------------------------------
#SELECCIÓN, CRUCE Y MUTACIÓN

def seleccion_torneo(poblacion, fitness, k=3):
    candidatos = random.sample(range(len(poblacion)), k)
    ganador = max(candidatos, key=lambda idx: fitness[idx])
    return poblacion[ganador]

def cruce_por_clase(padre1, padre2, pc=0.8):
    """Cada clase completa (todas sus sesiones) se hereda de un mismo padre: conserva la coherencia
    de los dias/aulas de una clase en lugar de romperla gen por gen."""
    if random.random() > pc:
        return padre1[:], padre2[:]
    hijo1, hijo2 = padre1[:], padre2[:]
    for idxs in CLASES_IDX:
        if random.random() < 0.5:
            for i in idxs:
                hijo1[i], hijo2[i] = padre2[i], padre1[i]
    return hijo1, hijo2

def mutar(cromosoma, pm_base=PM_BASE, pm_conflicto=PM_CONFLICTO, factor=1.0):
    """Mutacion dirigida: las sesiones en conflicto mutan con mucha mas probabilidad que las que ya estan bien."""
    cromosoma = cromosoma[:]
    _, _, conf = _analizar(cromosoma, detalle=True)
    for i in range(N):
        p = (pm_conflicto if i in conf else pm_base) * factor
        if random.random() < min(p, 0.9):
            r, h = cromosoma[i]
            if random.random() < 0.5:
                r = random.choice(AULAS_VALIDAS[i])
            else:
                h = random.choice(HORARIOS_VALIDOS[i])
            cromosoma[i] = (r, h)
    # intercambio de franjas entre dos sesiones (solo si ambas franjas son validas para la otra sesion)
    if random.random() < 0.1 * factor:
        i, j = random.sample(range(N), 2)
        (ri, hi), (rj, hj) = cromosoma[i], cromosoma[j]
        if hj in HORARIOS_VALIDOS_SET[i] and hi in HORARIOS_VALIDOS_SET[j]:
            cromosoma[i], cromosoma[j] = (ri, hj), (rj, hi)
    return cromosoma

def reparar(cromosoma, intentos=25, pasadas=2):
    """Busqueda local (componente memetico): para cada sesion en conflicto prueba 'intentos' pares
    (aula, franja) validos y se queda con el que mas reduce el costo."""
    c = cromosoma[:]
    for _ in range(pasadas):
        _, _, conf = _analizar(c, detalle=True)
        if not conf:
            break
        mejoro = False
        orden = list(conf)
        random.shuffle(orden)
        for i in orden:
            mejor_gen, mejor_costo = c[i], _costo_local(c, i)
            if mejor_costo == 0:
                continue
            original = c[i]
            for _ in range(intentos):
                c[i] = (random.choice(AULAS_VALIDAS[i]), random.choice(HORARIOS_VALIDOS[i]))
                k = _costo_local(c, i)
                if k < mejor_costo:
                    mejor_gen, mejor_costo = c[i], k
            c[i] = mejor_gen
            if mejor_gen != original:
                mejoro = True
        if not mejoro:
            break
    return c

#--------------------------------
#CICLO EVOLUTIVO

HISTORIAL = []  # (generacion, mejor_fitness, duras, blandas) de la ultima ejecucion

def ejecutar_algoritmo(tam_poblacion = 120, generaciones = 400, elite_pct = 0.05,
                       paciencia = 80, inmigrantes_pct = 0.05, semilla = None, verbose = True):
    if semilla is not None:
        random.seed(semilla)
    HISTORIAL.clear()

    poblacion = [cromosoma_aleatorio() for _ in range(tam_poblacion)]
    n_elite = max(1, int(tam_poblacion * elite_pct))
    n_inmigrantes = int(tam_poblacion * inmigrantes_pct)

    mejor_global, mejor_fitness_global = None, -1
    duras_mejor = blandas_mejor = 0
    sin_mejora = 0

    for gen in range(1, generaciones + 1):
        evaluados = [aptitud(c) for c in poblacion]

        # Reparacion local sobre los mejores individuos (lamarckiana: el individuo reparado reemplaza al original)
        if N_MEMETICO:
            top = sorted(range(tam_poblacion), key=lambda i: evaluados[i][0], reverse=True)[:N_MEMETICO]
            for i in top:
                rep = reparar(poblacion[i])
                ev = aptitud(rep)
                if ev[0] > evaluados[i][0]:
                    poblacion[i], evaluados[i] = rep, ev

        fitnesses = [e[0] for e in evaluados]

        idx_mejor = max(range(tam_poblacion), key=lambda i: fitnesses[i])
        if fitnesses[idx_mejor] > mejor_fitness_global:
            mejor_fitness_global = fitnesses[idx_mejor]
            mejor_global = poblacion[idx_mejor]
            duras_mejor, blandas_mejor = evaluados[idx_mejor][1], evaluados[idx_mejor][2]
            sin_mejora = 0
        else:
            sin_mejora += 1
        HISTORIAL.append((gen, mejor_fitness_global, duras_mejor, blandas_mejor))

        costo_mejor = W_H * duras_mejor + W_S * blandas_mejor
        optimo = costo_mejor <= COSTO_MINIMO

        if verbose and (gen == 1 or gen % 25 == 0 or optimo):
            print(f"Gen {gen:4d} | mejor fitness = {mejor_fitness_global:.5f} "
                    f"| duras = {duras_mejor} | blandas = {blandas_mejor}")

        # Paro: se alcanzo el minimo posible, o no hay mejora durante 'paciencia' generaciones
        if optimo:
            break
        if sin_mejora >= paciencia:
            if verbose:
                print(f"Gen {gen:4d} | sin mejora en {paciencia} generaciones: paro anticipado")
            break

        # Mutacion adaptativa: si se estanca, se sube la tasa para escapar del optimo local
        factor = 1.0 + min(sin_mejora // 10, 4)

        orden = sorted(range(tam_poblacion), key=lambda i: fitnesses[i], reverse=True)
        nueva_poblacion = [poblacion[i][:] for i in orden[:n_elite]]
        nueva_poblacion += [cromosoma_aleatorio() for _ in range(n_inmigrantes)]  # diversidad

        while len(nueva_poblacion) < tam_poblacion:
            p1 = seleccion_torneo(poblacion, fitnesses)
            p2 = seleccion_torneo(poblacion, fitnesses)
            h1, h2 = cruce_por_clase(p1, p2)
            h1, h2 = mutar(h1, factor=factor), mutar(h2, factor=factor)
            nueva_poblacion.append(h1)
            if len(nueva_poblacion) < tam_poblacion:
                nueva_poblacion.append(h2)

        poblacion = nueva_poblacion

    # Pulido final del mejor individuo con mas esfuerzo de busqueda local
    if N_MEMETICO:
        rep = reparar(mejor_global, intentos=150, pasadas=10)
        ev = aptitud(rep)
        if ev[0] > mejor_fitness_global:
            mejor_global, mejor_fitness_global = rep, ev[0]

    return mejor_global, mejor_fitness_global

#--------------------------------
#REPORTES

def imprimir_muestra(cromosoma, n = 10):
    print(f"\nMuestra de {n} sesiones del horario encontrado:")
    for i in range(min(n, N)):
        r, h = cromosoma[i]
        s, aula, horario = SESIONES[i], AULAS[r], HORARIOS[h]
        print(f"  {s['grupo']:>6} | {s['materia']:<30} | Prof. {s['profesor']:<30} "
                f"-> {aula['id']} ({aula['tipo']}) | {horario['dia']} {horario['inicio']}-{horario['fin']}")

def imprimir_violaciones(cromosoma):
    """Lista las violaciones que quedan en el horario, para saber exactamente que falta resolver."""
    print("\nViolaciones restantes:")
    hay = False
    por_aula = {}
    for i, (r, h) in enumerate(cromosoma):
        s = SESIONES[i]
        if DURA_AULA[i][r]:
            hay = True
            print(f"  [DURA] capacidad: {s['grupo']} {s['materia']} ({s['alumnos']} alumnos) en {AULAS[r]['id']} ({AULAS[r]['capacidad']})")
        if BLANDA_AULA[i][r]:
            hay = True
            print(f"  [blanda] aula no ideal: {s['grupo']} {s['materia']} (requiere {s['tipo_requerido']}) en {AULAS[r]['id']} ({AULAS[r]['tipo']})")
        por_aula.setdefault(r, []).append(i)
    for r, lista in por_aula.items():
        for a in range(len(lista)):
            for b in range(a + 1, len(lista)):
                if SOLAPA[cromosoma[lista[a]][1]][cromosoma[lista[b]][1]]:
                    hay = True
                    print(f"  [DURA] choque de aula {AULAS[r]['id']}: {SESIONES[lista[a]]['grupo']} vs {SESIONES[lista[b]]['grupo']}")
    for i, j in PARES_FIJOS:
        if SOLAPA[cromosoma[i][1]][cromosoma[j][1]]:
            hay = True
            print(f"  [DURA] traslape: {SESIONES[i]['grupo']} {SESIONES[i]['materia']} / {SESIONES[j]['grupo']} {SESIONES[j]['materia']} "
                  f"(prof. {SESIONES[i]['profesor']} / {SESIONES[j]['profesor']})")
    if not hay:
        print("  ninguna")

def exportar_horario(cromosoma, path="horario_generado.csv"):
    """Guarda el horario en el mismo formato que asignacion_actual.csv."""
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["clase_id", "grupo", "materia", "dia", "hora_inicio", "hora_fin", "aula"])
        for i in sorted(range(N), key=lambda i: (int(SESIONES[i]["clase_id"]), SESIONES[i]["sesion_num"])):
            r, h = cromosoma[i]
            s = SESIONES[i]
            w.writerow([s["clase_id"], s["grupo"], s["materia"], HORARIOS[h]["dia"],
                        HORARIOS[h]["inicio"], HORARIOS[h]["fin"], AULAS[r]["id"]])
    print(f"Horario guardado en {path}")


if __name__ == "__main__":
    mejor, fit = ejecutar_algoritmo()
    print(f"\nMejor fitness final: {fit:.5f}")
    imprimir_muestra(mejor)
    imprimir_violaciones(mejor)
    exportar_horario(mejor)