"""Compara el algoritmo genetico original con su version mejorada.

Ejemplo:
    python comparar_algoritmos.py --runs 5 --population 120 --generations 400
"""

import argparse
import contextlib
import csv
import importlib
import os
import random
import re
import sys
import time
from io import StringIO
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
COLUMNAS = [
    "algoritmo",
    "ejecucion",
    "semilla",
    "tiempo_segundos",
    "generaciones",
    "fitness_propio",
    "duras_propio",
    "blandas_propio",
    "fitness_comun",
    "duras_comun",
    "blandas_comun",
]


def cargar_algoritmos():
    """Importa los algoritmos desde la carpeta del proyecto y silencia sus mensajes iniciales."""
    sys.path.insert(0, str(BASE_DIR))
    directorio_anterior = Path.cwd()
    try:
        os.chdir(BASE_DIR)
        with contextlib.redirect_stdout(StringIO()):
            original = importlib.import_module("genetic_schedule")
            mejorado = importlib.import_module("better_genetic_schedule")
    finally:
        os.chdir(directorio_anterior)
        sys.path.remove(str(BASE_DIR))
    return original, mejorado


def crear_argumentos():
    parser = argparse.ArgumentParser(
        description="Mide y compara ambos algoritmos con las mismas semillas."
    )
    parser.add_argument("--runs", type=int, default=3, help="Ejecuciones por algoritmo (default: 3).")
    parser.add_argument("--population", type=int, default=120, help="Tamano de poblacion (default: 120).")
    parser.add_argument("--generations", type=int, default=400, help="Limite de generaciones (default: 400).")
    parser.add_argument("--seed", type=int, default=7, help="Semilla inicial (default: 7).")
    parser.add_argument(
        "--output",
        type=Path,
        default=BASE_DIR / "comparacion_algoritmos.csv",
        help="Ruta del CSV de resultados.",
    )
    args = parser.parse_args()
    if args.runs < 1:
        parser.error("--runs debe ser al menos 1.")
    if args.population < 3:
        parser.error("--population debe ser al menos 3.")
    if args.generations < 1:
        parser.error("--generations debe ser al menos 1.")
    return args


def ejecutar_comparacion(args):
    original, mejorado = cargar_algoritmos()
    resultados = []

    for ejecucion in range(1, args.runs + 1):
        semilla = args.seed + ejecucion - 1

        random.seed(semilla)
        salida_original = StringIO()
        inicio = time.perf_counter()
        with contextlib.redirect_stdout(salida_original):
            cromosoma_original, fitness_original = original.ejecutar_algoritmo(
                tam_poblacion=args.population,
                generaciones=args.generations,
            )
        tiempo_original = time.perf_counter() - inicio

        generaciones_reportadas = re.findall(
            r"Gen\s+(\d+)\s*\|", salida_original.getvalue()
        )
        generaciones_original = (
            int(generaciones_reportadas[-1])
            if fitness_original == 1.0 and generaciones_reportadas
            else args.generations
        )

        inicio = time.perf_counter()
        with contextlib.redirect_stdout(StringIO()):
            cromosoma_mejorado, fitness_mejorado = mejorado.ejecutar_algoritmo(
                tam_poblacion=args.population,
                generaciones=args.generations,
                semilla=semilla,
                verbose=False,
            )
        tiempo_mejorado = time.perf_counter() - inicio
        generaciones_mejorado = len(mejorado.HISTORIAL)

        for nombre, cromosoma, fitness, tiempo, generaciones, modulo in (
            (
                "Original",
                cromosoma_original,
                fitness_original,
                tiempo_original,
                generaciones_original,
                original,
            ),
            (
                "Mejorado",
                cromosoma_mejorado,
                fitness_mejorado,
                tiempo_mejorado,
                generaciones_mejorado,
                mejorado,
            ),
        ):
            _, duras_propias, blandas_propias = modulo.aptitud(cromosoma)
            fitness_comun, duras_comunes, blandas_comunes = original.aptitud(cromosoma)
            resultados.append(
                {
                    "algoritmo": nombre,
                    "ejecucion": ejecucion,
                    "semilla": semilla,
                    "tiempo_segundos": f"{tiempo:.6f}",
                    "generaciones": generaciones,
                    "fitness_propio": f"{fitness:.8f}",
                    "duras_propio": duras_propias,
                    "blandas_propio": blandas_propias,
                    "fitness_comun": f"{fitness_comun:.8f}",
                    "duras_comun": duras_comunes,
                    "blandas_comun": blandas_comunes,
                }
            )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="", encoding="utf-8-sig") as archivo:
        escritor = csv.DictWriter(archivo, fieldnames=COLUMNAS)
        escritor.writeheader()
        escritor.writerows(resultados)

    imprimir_resumen(resultados, args.output)


def imprimir_resumen(resultados, ruta_csv):
    print("\nRESULTADOS POR EJECUCION")
    print(
        f"{'Algoritmo':<12} {'Run':>3} {'Segundos':>10} {'Generaciones':>13} "
        f"{'Fitness propio':>15} {'Duras comunes':>14} {'Blandas comunes':>16}"
    )
    for fila in resultados:
        print(
            f"{fila['algoritmo']:<12} {fila['ejecucion']:>3} "
            f"{float(fila['tiempo_segundos']):>10.3f} {fila['generaciones']:>13} "
            f"{float(fila['fitness_propio']):>15.6f} "
            f"{fila['duras_comun']:>14} {fila['blandas_comun']:>16}"
        )

    print("\nPROMEDIOS")
    promedios = {}
    for algoritmo in ("Original", "Mejorado"):
        filas = [fila for fila in resultados if fila["algoritmo"] == algoritmo]
        promedios[algoritmo] = {
            "tiempo": sum(float(fila["tiempo_segundos"]) for fila in filas) / len(filas),
            "fitness_comun": sum(float(fila["fitness_comun"]) for fila in filas) / len(filas),
            "duras_comun": sum(fila["duras_comun"] for fila in filas) / len(filas),
            "blandas_comun": sum(fila["blandas_comun"] for fila in filas) / len(filas),
        }
        promedio = promedios[algoritmo]
        print(
            f"{algoritmo:<12} tiempo={promedio['tiempo']:.3f} s | "
            f"fitness comun={promedio['fitness_comun']:.6f} | "
            f"violaciones comunes duras={promedio['duras_comun']:.2f}, "
            f"blandas={promedio['blandas_comun']:.2f}"
        )

    tiempo_original = promedios["Original"]["tiempo"]
    tiempo_mejorado = promedios["Mejorado"]["tiempo"]
    if tiempo_original > 0:
        cambio = (tiempo_mejorado - tiempo_original) / tiempo_original * 100
        etiqueta = "mas lento" if cambio > 0 else "mas rapido"
        print(f"Tiempo promedio del mejorado: {abs(cambio):.1f}% {etiqueta} que el original.")
    print(f"\nResultados detallados guardados en: {ruta_csv}")
    print(
        "Nota: 'fitness propio' usa las reglas de cada algoritmo; "
        "'comun' evalua ambos horarios con las reglas del algoritmo original."
    )


if __name__ == "__main__":
    ejecutar_comparacion(crear_argumentos())
