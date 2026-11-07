"""Regenera las gráficas estáticas del README desde los CSV del proyecto."""

import csv
import statistics
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


ROOT = Path(__file__).resolve().parent
OUTPUT_DIR = ROOT / "docs" / "figures"
DIAS = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes"]
COLORS = {"Original": "#64748b", "Mejorado": "#0f766e", "Nuevo": "#0f766e"}


def read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as file:
        return list(csv.DictReader(file))


def minutes(value):
    hours, mins = map(int, value.split(":"))
    return hours * 60 + mins


def load_inputs():
    dataset = ROOT / "dataset"
    classes = {row["clase_id"]: row for row in read_csv(dataset / "clases.csv")}
    rooms = {row["aula_id"]: row for row in read_csv(dataset / "aulas.csv")}
    schedules = {
        "Original": read_csv(dataset / "asignacion_actual.csv"),
        "Nuevo": read_csv(ROOT / "horario_generado.csv"),
    }
    results = read_csv(ROOT / "comparacion_algoritmos.csv")
    return classes, rooms, schedules, results


def schedule_metrics(rows, classes, rooms):
    conflicts = Counter()
    for first, second in combinations(rows, 2):
        if first["dia"] != second["dia"]:
            continue
        overlap = (
            minutes(first["hora_inicio"]) < minutes(second["hora_fin"])
            and minutes(second["hora_inicio"]) < minutes(first["hora_fin"])
        )
        if not overlap:
            continue
        if first["grupo"] == second["grupo"]:
            conflicts["Empalmes de grupo"] += 1
        if classes[first["clase_id"]]["profesor"] == classes[second["clase_id"]]["profesor"]:
            conflicts["Empalmes de profesor"] += 1
        if first["aula"] == second["aula"]:
            conflicts["Empalmes de aula"] += 1

    over_capacity = 0
    wrong_room_type = 0
    wrong_shift = 0
    for row in rows:
        course = classes[row["clase_id"]]
        room = rooms[row["aula"]]
        over_capacity += int(int(course["alumnos_estimado"]) > int(room["capacidad_estimada"]))
        wrong_room_type += int(course["tipo_aula_requerido"] != room["tipo"])
        is_day_slot = minutes(row["hora_inicio"]) < 13 * 60
        wrong_shift += int((course["turno_inferido"] == "Diurno") != is_day_slot)

    conflicts["Exceso de capacidad"] = over_capacity
    conflicts["Tipo de aula incorrecto"] = wrong_room_type
    conflicts["Fuera del turno"] = wrong_shift
    return conflicts


def group_day_counts(rows):
    counts = Counter((row["grupo"], row["dia"]) for row in rows)
    return counts


def mean_daily_gaps(rows):
    by_group_day = defaultdict(list)
    for row in rows:
        by_group_day[(row["grupo"], row["dia"])].append(
            (minutes(row["hora_inicio"]), minutes(row["hora_fin"]))
        )

    gaps = []
    for intervals in by_group_day.values():
        intervals.sort()
        previous_end = None
        total_gap = 0
        for start, end in intervals:
            if previous_end is not None:
                total_gap += max(0, start - previous_end)
                previous_end = max(previous_end, end)
            else:
                previous_end = end
        gaps.append(total_gap)
    return statistics.mean(gaps) if gaps else 0


def save_algorithm_runtime(results):
    by_algorithm = defaultdict(list)
    for row in results:
        by_algorithm[row["algoritmo"]].append(float(row["tiempo_segundos"]))

    names = ["Original", "Mejorado"]
    means = [statistics.mean(by_algorithm[name]) for name in names]
    errors = [statistics.stdev(by_algorithm[name]) for name in names]
    ratio = means[0] / means[1]

    fig, ax = plt.subplots(figsize=(8, 4.8))
    bars = ax.bar(
        names,
        means,
        yerr=errors,
        capsize=7,
        color=[COLORS[name] for name in names],
        width=0.58,
    )
    ax.set_yscale("log")
    ax.set_ylabel("Segundos por ejecución (escala logarítmica)")
    ax.set_title(
        f"Tiempo medio de ejecución (10 semillas pareadas)\n"
        f"Razón entre tiempos medios: {ratio:.2f}×"
    )
    ax.grid(axis="y", alpha=0.25, which="both")
    ax.bar_label(bars, labels=[f"{value:.3f} s" for value in means], padding=8)
    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / "tiempo_ejecucion.png", dpi=180, bbox_inches="tight")
    plt.close(fig)


def save_schedule_violations(schedules, classes, rooms):
    names = ["Original", "Nuevo"]
    metrics = {name: schedule_metrics(schedules[name], classes, rooms) for name in names}
    categories = [
        "Empalmes de grupo",
        "Empalmes de profesor",
        "Empalmes de aula",
        "Exceso de capacidad",
        "Tipo de aula incorrecto",
        "Fuera del turno",
    ]
    positions = np.arange(len(categories))
    width = 0.36

    fig, ax = plt.subplots(figsize=(11, 5.4))
    for offset, name in zip((-width / 2, width / 2), names):
        values = [metrics[name][category] for category in categories]
        bars = ax.bar(
            positions + offset,
            values,
            width,
            label=name,
            color=COLORS[name],
        )
        ax.bar_label(bars, padding=2, fontsize=8)
    ax.set_xticks(positions, categories, rotation=20, ha="right")
    ax.set_ylabel("Número de pares en conflicto o sesiones que incumplen")
    ax.set_title("Validación del horario original y el generado")
    ax.grid(axis="y", alpha=0.25)
    ax.legend(title="Horario")
    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / "restricciones_horarios.png", dpi=180, bbox_inches="tight")
    plt.close(fig)


def save_weekday_counts(schedules):
    fig, ax = plt.subplots(figsize=(9, 4.7))
    positions = np.arange(len(DIAS))
    width = 0.36
    for offset, name in zip((-width / 2, width / 2), ("Original", "Nuevo")):
        counts = Counter(row["dia"] for row in schedules[name])
        values = [counts[day] for day in DIAS]
        bars = ax.bar(
            positions + offset,
            values,
            width,
            label=name,
            color=COLORS[name],
        )
        ax.bar_label(bars, padding=3)
    ax.set_xticks(positions, DIAS)
    ax.set_ylabel("Sesiones")
    ax.set_title("Distribución de clases por día")
    ax.grid(axis="y", alpha=0.25)
    ax.legend(title="Horario")
    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / "sesiones_por_dia.png", dpi=180, bbox_inches="tight")
    plt.close(fig)


def save_group_heatmaps(schedules):
    groups = sorted({row["grupo"] for rows in schedules.values() for row in rows})
    fig, axes = plt.subplots(1, 2, figsize=(13, max(5, len(groups) * 0.38)), sharey=True)
    image = None
    for ax, name in zip(axes, ("Original", "Nuevo")):
        counts = group_day_counts(schedules[name])
        values = np.array([[counts[(group, day)] for day in DIAS] for group in groups])
        image = ax.imshow(values, cmap="Blues", aspect="auto", vmin=0)
        ax.set_title(name)
        ax.set_xticks(np.arange(len(DIAS)), DIAS, rotation=35, ha="right")
        ax.set_yticks(np.arange(len(groups)), groups)
        ax.set_xlabel("Día de la semana")
        for i in range(len(groups)):
            for j in range(len(DIAS)):
                value = values[i, j]
                if value:
                    ax.text(
                        j,
                        i,
                        str(value),
                        ha="center",
                        va="center",
                        color="white" if value >= 3 else "#17324d",
                        fontsize=8,
                    )
    axes[0].set_ylabel("Grupo")
    fig.suptitle("Sesiones por grupo y día", fontsize=14)
    fig.subplots_adjust(top=0.92, bottom=0.17, wspace=0.08, right=0.86)
    colorbar_axis = fig.add_axes([0.89, 0.22, 0.018, 0.62])
    fig.colorbar(image, cax=colorbar_axis, label="Sesiones")
    fig.savefig(OUTPUT_DIR / "grupos_por_dia.png", dpi=180, bbox_inches="tight")
    plt.close(fig)


def save_compactness(schedules):
    names = ["Original", "Nuevo"]
    days_per_group = {}
    gaps_per_group_day = {}
    for name in names:
        rows = schedules[name]
        day_counts = defaultdict(set)
        for row in rows:
            day_counts[row["grupo"]].add(row["dia"])
        days_per_group[name] = statistics.mean(len(days) for days in day_counts.values())
        gaps_per_group_day[name] = mean_daily_gaps(rows)

    fig, axes = plt.subplots(1, 2, figsize=(9, 4.5))
    for ax, values, title, ylabel, fmt in (
        (
            axes[0],
            days_per_group,
            "Días de asistencia por grupo",
            "Días por semana (promedio)",
            "{:.2f}",
        ),
        (
            axes[1],
            gaps_per_group_day,
            "Huecos durante el día",
            "Minutos libres por grupo-día (promedio)",
            "{:.1f}",
        ),
    ):
        bars = ax.bar(
            names,
            [values[name] for name in names],
            color=[COLORS[name] for name in names],
            width=0.58,
        )
        ax.bar_label(bars, labels=[fmt.format(values[name]) for name in names], padding=3)
        ax.set_title(title)
        ax.set_ylabel(ylabel)
        ax.grid(axis="y", alpha=0.25)
    fig.suptitle("Compacidad de la semana: dos indicadores distintos", fontsize=13)
    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / "compactacion_semanal.png", dpi=180, bbox_inches="tight")
    plt.close(fig)


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    classes, rooms, schedules, results = load_inputs()
    save_algorithm_runtime(results)
    save_schedule_violations(schedules, classes, rooms)
    save_weekday_counts(schedules)
    save_group_heatmaps(schedules)
    save_compactness(schedules)
    print(f"Gráficas guardadas en {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
