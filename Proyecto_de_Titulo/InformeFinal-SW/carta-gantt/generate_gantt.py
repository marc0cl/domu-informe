#!/usr/bin/env python3
"""
Genera las cartas Gantt del proyecto DOMU:
  - anteproyecto.pdf  (línea base / planificación original)
  - proyecto.pdf      (ejecución real basada en commits)

Los PDFs se incluyen en LaTeX via sidewaysfigure con width=\textheight,
por lo que se generan en orientación landscape con proporciones que
coinciden con la página rotada (~23cm alto × ~16cm ancho tras rotación).
"""

import locale
import os
from datetime import datetime

# Fechas en español
for loc in ("es_ES.UTF-8", "es_CL.UTF-8", "es_ES", "Spanish_Spain"):
    try:
        locale.setlocale(locale.LC_TIME, loc)
        break
    except locale.Error:
        continue

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.patches as mpatches

# ── Colores por tipo de actividad ──────────────────────────────
COLORS = {
    "Planificación": "#5B9BD5",
    "Diseño":        "#70AD47",
    "Backend":       "#ED7D31",
    "Frontend":      "#4472C4",
    "Pruebas":       "#FFC000",
    "Documentación": "#A5A5A5",
}

PHASE_BG_COLORS = ["#F2F2F2", "#FFFFFF"]

# ── Hitos ──────────────────────────────────────────────────────
MILESTONES_BASELINE = [
    ("Alpha",         datetime(2025, 10, 20)),
    ("Beta",          datetime(2025, 12, 15)),
    ("Release 1.0",   datetime(2026, 1, 26)),
    ("Cierre",        datetime(2026, 3, 2)),
]

MILESTONES_REAL = [
    ("Release 0.1.0", datetime(2025, 10, 23)),
    ("Release 1.0.0", datetime(2025, 11, 20)),
    ("Release 1.1.0", datetime(2025, 12, 6)),
    ("Release 1.2.0", datetime(2026, 1, 7)),
    ("Release 1.3.0", datetime(2026, 1, 22)),
    ("Release 1.4.0", datetime(2026, 2, 4)),
    ("Cierre",        datetime(2026, 3, 2)),
]

# ── Datos de ejecución real (basados en commits) ──────────────
PHASES_REAL = [
    ("Planificación", "Definición de alcance y análisis de mercado",       "Planificación", "2025-10-01", "2025-10-10"),
    ("Planificación", "Especificación de requerimientos (RF/RNF)",         "Planificación", "2025-10-07", "2025-10-15"),
    ("Planificación", "Diseño de arquitectura y selección tecnologías",    "Diseño",        "2025-10-10", "2025-10-18"),

    ("Fase 1: Fundamentos", "Scaffolding Backend (Gradle + Javalin)",     "Backend",       "2025-10-03", "2025-10-10"),
    ("Fase 1: Fundamentos", "Scaffolding Frontend (Vite + React)",        "Frontend",      "2025-10-03", "2025-10-10"),
    ("Fase 1: Fundamentos", "Diseño de BD — esquema de auth",             "Diseño",        "2025-10-10", "2025-10-22"),
    ("Fase 1: Fundamentos", "Implementación JWT + BCrypt",                "Backend",       "2025-10-15", "2025-10-23"),
    ("Fase 1: Fundamentos", "Registro con confirmación email",            "Backend",       "2025-10-20", "2025-10-30"),
    ("Fase 1: Fundamentos", "Templates HTML de correo (Jakarta Mail)",    "Backend",       "2025-10-25", "2025-11-05"),
    ("Fase 1: Fundamentos", "Documentación: arquitectura y auth",         "Documentación", "2025-10-20", "2025-10-28"),

    ("Fase 2: Comunidades", "Modelo multi-comunidad (Backend)",           "Backend",       "2025-11-01", "2025-11-15"),
    ("Fase 2: Comunidades", "CRUD unidades habitacionales",               "Backend",       "2025-11-10", "2025-11-20"),
    ("Fase 2: Comunidades", "Creación de usuarios por rol",               "Backend",       "2025-11-15", "2025-11-24"),
    ("Fase 2: Comunidades", "Emails de invitación y aprobación",          "Backend",       "2025-11-18", "2025-11-26"),
    ("Fase 2: Comunidades", "Frontend: login + registro + dashboard",     "Frontend",      "2025-11-18", "2025-11-28"),
    ("Fase 2: Comunidades", "Documentación: modelo de datos y CUs",       "Documentación", "2025-11-15", "2025-11-25"),

    ("Fase 3: Servicios",   "Módulo de incidentes (Backend)",             "Backend",       "2025-12-01", "2025-12-10"),
    ("Fase 3: Servicios",   "Módulo de incidentes (Frontend Kanban)",     "Frontend",      "2025-12-05", "2025-12-15"),
    ("Fase 3: Servicios",   "Reservas de áreas comunes",                  "Backend",       "2025-12-08", "2025-12-18"),
    ("Fase 3: Servicios",   "Votaciones",                                 "Backend",       "2025-12-12", "2025-12-22"),
    ("Fase 3: Servicios",   "Control de acceso y visitas + QR",           "Backend",       "2025-12-10", "2025-12-20"),
    ("Fase 3: Servicios",   "Frontend: AuthLayout, VisitRegistration",    "Frontend",      "2025-12-03", "2025-12-15"),
    ("Fase 3: Servicios",   "Documentación: servicios y endpoints",       "Documentación", "2025-12-10", "2025-12-20"),

    ("Fase 4: Financiero",  "Períodos de gastos comunes",                 "Backend",       "2025-12-15", "2025-12-28"),
    ("Fase 4: Financiero",  "Flujo de pagos + pasarela simulada",         "Backend",       "2025-12-20", "2026-01-05"),
    ("Fase 4: Financiero",  "Generación de cartola PDF (OpenPDF)",        "Backend",       "2026-01-02", "2026-01-10"),
    ("Fase 4: Financiero",  "Comprobantes de pago y emails de cobro",     "Backend",       "2026-01-06", "2026-01-14"),
    ("Fase 4: Financiero",  "Frontend: cartola + flujo de pago",          "Frontend",      "2026-01-05", "2026-01-15"),
    ("Fase 4: Financiero",  "Documentación: módulo financiero",           "Documentación", "2026-01-05", "2026-01-13"),

    ("Fase 5: Comunicación","Chat WebSocket (Backend)",                   "Backend",       "2026-01-10", "2026-01-20"),
    ("Fase 5: Comunicación","Foro comunitario",                           "Backend",       "2026-01-15", "2026-01-25"),
    ("Fase 5: Comunicación","Marketplace + almacenamiento Box",           "Backend",       "2026-01-18", "2026-01-29"),
    ("Fase 5: Comunicación","Encomiendas",                                "Backend",       "2026-01-20", "2026-01-31"),
    ("Fase 5: Comunicación","Frontend: chat, foro, marketplace",          "Frontend",      "2026-01-22", "2026-02-05"),
    ("Fase 5: Comunicación","Documentación: comunicación y chat",         "Documentación", "2026-01-25", "2026-02-03"),

    ("Fase 6: Personal",    "Gestión de personal + turnos",               "Backend",       "2026-02-01", "2026-02-10"),
    ("Fase 6: Personal",    "Asignación de tareas",                       "Backend",       "2026-02-05", "2026-02-14"),
    ("Fase 6: Personal",    "WebSocket notificaciones",                   "Backend",       "2026-02-08", "2026-02-16"),
    ("Fase 6: Personal",    "Frontend: admin forms, protected routes",    "Frontend",      "2026-02-01", "2026-02-12"),
    ("Fase 6: Personal",    "Documentación: gestión operativa",           "Documentación", "2026-02-10", "2026-02-18"),

    ("Fase 7: Proveedores", "CRUD proveedores (Backend)",                 "Backend",       "2026-02-12", "2026-02-22"),
    ("Fase 7: Proveedores", "Órdenes de servicio",                        "Backend",       "2026-02-18", "2026-02-28"),
    ("Fase 7: Proveedores", "Portal proveedor (Frontend)",                "Frontend",      "2026-02-20", "2026-03-01"),
    ("Fase 7: Proveedores", "Swagger UI / OpenAPI",                       "Documentación", "2026-02-25", "2026-03-02"),

    ("Cierre",              "Pruebas de aceptación",                      "Pruebas",       "2026-02-25", "2026-03-02"),
    ("Cierre",              "Documentación del informe",                  "Documentación", "2026-02-20", "2026-03-02"),
    ("Cierre",              "Deploy PWA + marcha blanca",                 "Pruebas",       "2026-03-01", "2026-03-02"),
]

PHASES_BASELINE = [
    # ── Planificación y diseño (ago–sep 2025) ──
    ("Planificación",          "Levantamiento de requerimientos",              "Planificación", "2025-08-18", "2025-09-01"),
    ("Planificación",          "Análisis de mercado y benchmarking",           "Planificación", "2025-08-25", "2025-09-05"),
    ("Planificación",          "Selección de tecnologías",                     "Planificación", "2025-09-01", "2025-09-08"),
    ("Planificación",          "Diseño de arquitectura",                       "Diseño",        "2025-09-08", "2025-09-19"),
    ("Planificación",          "Diseño de base de datos",                      "Diseño",        "2025-09-15", "2025-09-26"),

    # ── Implementación Backend (oct–dic 2025) ──
    ("Implementación Backend", "Scaffolding y autenticación (JWT)",            "Backend",       "2025-09-29", "2025-10-10"),
    ("Implementación Backend", "Módulo de comunidades y usuarios",             "Backend",       "2025-10-06", "2025-10-20"),
    ("Implementación Backend", "Módulo de visitas y control de acceso",        "Backend",       "2025-10-20", "2025-11-03"),
    ("Implementación Backend", "Módulo de incidentes y votaciones",            "Backend",       "2025-10-27", "2025-11-10"),
    ("Implementación Backend", "Módulo de reservas de áreas comunes",          "Backend",       "2025-11-10", "2025-11-21"),
    ("Implementación Backend", "Módulo financiero (gastos comunes + pagos)",   "Backend",       "2025-11-17", "2025-12-05"),
    ("Implementación Backend", "Módulo de comunicación (chat + foro)",         "Backend",       "2025-12-01", "2025-12-15"),
    ("Implementación Backend", "Módulo de encomiendas y marketplace",          "Backend",       "2025-12-08", "2025-12-22"),
    ("Implementación Backend", "Módulo de personal y proveedores",             "Backend",       "2025-12-15", "2026-01-05"),

    # ── Implementación Frontend (oct 2025–ene 2026) ──
    ("Implementación Frontend","Login, registro y dashboard",                  "Frontend",      "2025-10-13", "2025-10-27"),
    ("Implementación Frontend","Vistas de visitas, incidentes y reservas",     "Frontend",      "2025-10-27", "2025-11-14"),
    ("Implementación Frontend","Vistas de gastos comunes y pagos",             "Frontend",      "2025-11-17", "2025-12-05"),
    ("Implementación Frontend","Chat, foro y marketplace",                     "Frontend",      "2025-12-08", "2025-12-26"),
    ("Implementación Frontend","Panel de administración y proveedores",        "Frontend",      "2026-01-05", "2026-01-19"),

    # ── Integración y pruebas (ene–feb 2026) ──
    ("Integración y Pruebas",  "Pruebas unitarias y de integración",          "Pruebas",       "2026-01-19", "2026-02-02"),
    ("Integración y Pruebas",  "Pruebas de aceptación con usuarios",          "Pruebas",       "2026-02-02", "2026-02-13"),
    ("Integración y Pruebas",  "Corrección de defectos",                      "Backend",       "2026-02-06", "2026-02-16"),
    ("Integración y Pruebas",  "Deploy y marcha blanca",                      "Pruebas",       "2026-02-13", "2026-02-23"),

    # ── Documentación y cierre (feb–mar 2026) ──
    ("Documentación y Cierre", "Redacción del informe de título",             "Documentación", "2026-02-03", "2026-02-27"),
    ("Documentación y Cierre", "Revisión y correcciones finales",             "Documentación", "2026-02-23", "2026-03-02"),
]


def _parse(d: str) -> datetime:
    return datetime.strptime(d, "%Y-%m-%d")


def _build_rows(phases):
    """Build display rows: phase headers + activity rows."""
    rows = []  # list of dicts with keys: label, is_header, type, start, end, phase
    seen_phases = []
    for phase, activity, typ, start, end in phases:
        if phase not in seen_phases:
            seen_phases.append(phase)
            rows.append({
                "label": phase,
                "is_header": True,
                "type": None,
                "start": None,
                "end": None,
                "phase": phase,
            })
        rows.append({
            "label": "   " + activity,
            "is_header": False,
            "type": typ,
            "start": _parse(start),
            "end": _parse(end),
            "phase": phase,
        })
    return rows, seen_phases


def generate_gantt(phases, title, output_path, milestones=None,
                   date_range=None):
    """Render a professional Gantt chart to PDF."""

    rows, phase_order = _build_rows(phases)
    rows_reversed = list(reversed(rows))
    n = len(rows_reversed)

    # ── Proporciones: landscape, ~A3. sidewaysfigure lo rotará 90° ──
    # Ancho grande para el timeline, alto proporcional a las filas
    fig_w = 16       # inches — eje temporal (será el alto tras rotación)
    fig_h = n * 0.24 + 1.0  # inches — eje de actividades
    fig, ax = plt.subplots(figsize=(fig_w, fig_h))

    bar_height = 0.6
    if date_range:
        date_min, date_max = date_range
    else:
        date_min = datetime(2025, 9, 29)
        date_max = datetime(2026, 3, 9)

    # ── Detectar rangos de fase para fondo alternado ──────────
    phase_spans = {}
    for i, r in enumerate(rows_reversed):
        p = r["phase"]
        if p not in phase_spans:
            phase_spans[p] = [i, i]
        else:
            phase_spans[p][1] = i

    for idx, pname in enumerate(phase_order):
        if pname in phase_spans:
            span = phase_spans[pname]
            ax.axhspan(
                span[0] - 0.5, span[1] + 0.5,
                facecolor=PHASE_BG_COLORS[idx % 2],
                edgecolor="none", zorder=0,
            )

    # ── Dibujar barras ────────────────────────────────────────
    for i, r in enumerate(rows_reversed):
        if r["is_header"]:
            continue
        color = COLORS.get(r["type"], "#999999")
        start_num = mdates.date2num(r["start"])
        duration = (r["end"] - r["start"]).days
        ax.barh(
            i, duration, left=start_num,
            height=bar_height, color=color, edgecolor="white",
            linewidth=0.3, zorder=2, alpha=0.92,
        )

    # ── Etiquetas del eje Y ───────────────────────────────────
    y_labels = []
    for r in rows_reversed:
        y_labels.append(r["label"])
    ax.set_yticks(range(n))
    ax.set_yticklabels(
        y_labels, fontsize=8, fontfamily="sans-serif",
    )
    # Bold phase headers
    for i, r in enumerate(rows_reversed):
        if r["is_header"]:
            ax.get_yticklabels()[i].set_fontweight("bold")
            ax.get_yticklabels()[i].set_fontsize(8.5)
            ax.get_yticklabels()[i].set_color("#222222")

    # ── Eje X: fechas ────────────────────────────────────────
    ax.set_xlim(mdates.date2num(date_min), mdates.date2num(date_max))
    ax.set_ylim(-0.5, n - 0.5)

    # Major: cada 2 semanas — horizontal labels
    ax.xaxis.set_major_locator(mdates.WeekdayLocator(byweekday=mdates.MO, interval=2))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%d %b"))
    ax.tick_params(axis="x", labelsize=8, rotation=0, pad=4)

    # Minor: cada semana (grid)
    ax.xaxis.set_minor_locator(mdates.WeekdayLocator(byweekday=mdates.MO))

    # Meses arriba
    ax_top = ax.secondary_xaxis("top")
    ax_top.xaxis.set_major_locator(mdates.MonthLocator())
    ax_top.xaxis.set_major_formatter(mdates.DateFormatter("%B %Y"))
    ax_top.tick_params(labelsize=9, length=0, pad=6)

    # Grid
    ax.xaxis.grid(True, which="minor", linestyle=":", linewidth=0.3, color="#DDDDDD", zorder=0)
    ax.xaxis.grid(True, which="major", linestyle="-", linewidth=0.5, color="#CCCCCC", zorder=0)
    ax.yaxis.grid(False)

    # ── Hitos (líneas verticales + diamantes arriba) ──────────
    if milestones:
        for name, date in milestones:
            x = mdates.date2num(date)
            ax.axvline(x, color="#C00000", linewidth=0.7, linestyle="--", alpha=0.5, zorder=1)
            # Diamante arriba del chart
            ax.plot(
                x, n - 0.5, marker="D", color="#C00000",
                markersize=7, zorder=5, clip_on=False,
            )
            ax.annotate(
                name, xy=(x, n + 0.1), fontsize=6.5,
                ha="center", va="bottom", fontweight="bold",
                color="#C00000", fontfamily="sans-serif",
                zorder=5, clip_on=False,
            )

    # ── Leyenda ───────────────────────────────────────────────
    legend_patches = [
        mpatches.Patch(color=c, label=l)
        for l, c in COLORS.items()
    ]
    if milestones:
        legend_patches.append(
            plt.Line2D([0], [0], marker="D", color="w",
                       markerfacecolor="#C00000", markersize=7,
                       label="Hito / Release")
        )
    ax.legend(
        handles=legend_patches,
        loc="lower right",
        fontsize=7.5,
        framealpha=0.95,
        ncol=len(legend_patches),
        borderpad=0.6,
        edgecolor="#CCCCCC",
    )

    # ── Título ────────────────────────────────────────────────
    ax.set_title(
        title,
        fontsize=13, fontweight="bold", pad=28,
        fontfamily="sans-serif", color="#222222",
    )

    # ── Estilo general ────────────────────────────────────────
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_linewidth(0.4)
    ax.spines["bottom"].set_linewidth(0.4)
    ax.invert_yaxis()

    fig.savefig(output_path, format="pdf", dpi=150, bbox_inches="tight",
                pad_inches=0.1)
    plt.close(fig)
    print(f"  OK  {output_path}")


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))

    print("Generando carta Gantt — Anteproyecto (línea base)...")
    generate_gantt(
        PHASES_BASELINE,
        "Carta Gantt — Anteproyecto (Línea Base)",
        os.path.join(script_dir, "anteproyecto.pdf"),
        milestones=MILESTONES_BASELINE,
        date_range=(datetime(2025, 8, 11), datetime(2026, 3, 9)),
    )

    print("Generando carta Gantt — Proyecto (ejecución real)...")
    generate_gantt(
        PHASES_REAL,
        "Carta Gantt — Proyecto de Título (Ejecución Real)",
        os.path.join(script_dir, "proyecto.pdf"),
        milestones=MILESTONES_REAL,
    )

    print("\nListo. Ambos PDFs generados en carta-gantt/")


if __name__ == "__main__":
    main()
