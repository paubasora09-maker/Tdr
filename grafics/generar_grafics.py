"""Genera els gràfics de les respostes del qüestionari d'enduro a partir del CSV."""
import csv
import textwrap
from collections import Counter
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ARREL = Path(__file__).resolve().parent.parent
CSV = ARREL / "dades" / "respostes-simulades.csv"
SORTIDA = ARREL / "grafics"

SUPERFICIE = "#fcfcfb"
TEXT = "#0b0b0b"
TEXT_SEC = "#52514e"
GRAELLA = "#e4e3df"
BLAU = "#2a78d6"
ESCALA = ["#86b6ef", "#5598e7", "#2a78d6", "#1c5cab", "#104281"]  # rampa ordinal 1–5
PERFILS_COLORS = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100"]

plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 11,
    "figure.facecolor": SUPERFICIE, "axes.facecolor": SUPERFICIE,
    "axes.edgecolor": GRAELLA, "axes.labelcolor": TEXT_SEC,
    "xtick.color": TEXT_SEC, "ytick.color": TEXT_SEC,
    "axes.spines.top": False, "axes.spines.right": False,
})

with open(CSV, encoding="utf-8-sig") as f:
    files = list(csv.DictReader(f))
N = len(files)
COL = list(files[0].keys())

PERFILS = ["Aficionat/da al motor (practico enduro o motocròs)", "Senderista o ciclista de muntanya",
           "Resident en una zona rural o de muntanya", "Cap dels anteriors"]
PERFILS_CURTS = ["Aficionats al motor", "Senderistes / ciclistes", "Residents rurals", "Cap dels anteriors"]


def titol(ax, t, sub=None):
    ax.set_title(t, loc="left", fontsize=14, fontweight="bold", color=TEXT, pad=26 if sub else 12)
    if sub:
        ax.text(0, 1.02, sub, transform=ax.transAxes, fontsize=10.5, color=TEXT_SEC, va="bottom")


def desa(fig, nom):
    fig.tight_layout()
    fig.savefig(SORTIDA / nom, dpi=200)
    plt.close(fig)


def barres_horitzontals(col, opcions, nom, t, sub=None):
    c = Counter(r[col] for r in files)
    vals = [c[o] for o in opcions]
    etiquetes = ["\n".join(textwrap.wrap(o, 34)) for o in opcions]
    fig, ax = plt.subplots(figsize=(9, 0.75 * len(opcions) + 1.6))
    y = range(len(opcions))[::-1]
    ax.barh(list(y), vals, color=BLAU, height=0.6)
    ax.set_yticks(list(y), etiquetes)
    for yi, v in zip(y, vals):
        ax.text(v + N * 0.008, yi, f"{v}  ({v / N:.0%})", va="center", color=TEXT, fontsize=10.5)
    ax.set_xlim(0, max(vals) * 1.22)
    ax.xaxis.grid(True, color=GRAELLA, linewidth=0.8)
    ax.set_axisbelow(True)
    ax.tick_params(axis="y", length=0)
    ax.set_xlabel("Nombre de respostes")
    titol(ax, t, sub)
    desa(fig, nom)


def escala(col, esq, dre, nom, t):
    vals = [int(r[col]) for r in files]
    c = Counter(vals)
    alt = [c[i] for i in range(1, 6)]
    mitjana = sum(vals) / N
    fig, ax = plt.subplots(figsize=(8, 4.6))
    ax.bar(range(1, 6), alt, color=ESCALA, width=0.62)
    for x, v in zip(range(1, 6), alt):
        ax.text(x, v + max(alt) * 0.02, str(v), ha="center", va="bottom", color=TEXT, fontsize=10.5)
    ax.set_xticks(range(1, 6), [f"1\n{esq}", "2", "3", "4", f"5\n{dre}"])
    ax.set_ylim(0, max(alt) * 1.18)
    ax.yaxis.grid(True, color=GRAELLA, linewidth=0.8)
    ax.set_axisbelow(True)
    ax.tick_params(axis="x", length=0)
    ax.set_ylabel("Nombre de respostes")
    titol(ax, t, f"Mitjana: {mitjana:.1f}".replace(".", ",") + f" sobre 5  ·  n = {N}")
    desa(fig, nom)


# 1. Perfil
barres_horitzontals(COL[2], PERFILS, "01-perfil.png", "Perfil dels enquestats", f"n = {N}")

# 2, 3, 6, 8. Escales
escala(COL[3], "Gens", "Molt", "02-impacte-erosio.png", "Impacte negatiu i erosió als camins")
escala(COL[4], "Gens d'acord", "Totalment d'acord", "03-tallafocs-neteja.png",
       "Les motos ajuden a netejar camins i fan de tallafocs")
escala(COL[7], "En contra", "A favor", "06-senders-homologats.png", "Xarxa de senders homologats per a l'enduro")
escala(COL[9], "Molt dolent", "Excel·lent", "08-respecte-mutu.png", "Respecte mutu entre usuaris de la muntanya")

# 4, 5, 7, 9. Opció múltiple
barres_horitzontals(COL[5], ["Sí, molt", "Sí, però poc", "No gaire", "Gens", "No ho sé"],
                    "04-soroll-fauna.png", "El soroll de les motos afecta la fauna?", f"n = {N}")
barres_horitzontals(COL[6], ["No la conec", "La conec i crec que és adequada",
                             "La conec i crec que és massa restrictiva", "La conec i crec que és massa permissiva"],
                    "05-llei-9-1995.png", "Opinió sobre la Llei 9/1995", f"n = {N}")
barres_horitzontals(COL[8], ["A favor", "A favor, només si els diners es destinen realment als boscos",
                             "En contra", "No ho sé"],
                    "07-vinyeta-verda.png", "Taxa anual o \"vinyeta verda\"", f"n = {N}")
barres_horitzontals(COL[10], ["Sí, molt important", "Sí, però petit", "No, cap", "No ho sé"],
                    "09-impacte-economic.png", "Impacte econòmic positiu als municipis de muntanya", f"n = {N}")

# Comparativa per perfil de les preguntes d'escala
preguntes = [(COL[3], "Impacte i\nerosió"), (COL[4], "Tallafocs i\nneteja"),
             (COL[7], "Senders\nhomologats"), (COL[9], "Respecte\nmutu")]
fig, ax = plt.subplots(figsize=(10, 5.4))
amplada = 0.19
for i, (perfil, curt, color) in enumerate(zip(PERFILS, PERFILS_CURTS, PERFILS_COLORS)):
    grup = [r for r in files if r[COL[2]] == perfil]
    mitjanes = [sum(int(r[c]) for r in grup) / len(grup) for c, _ in preguntes]
    xs = [j + (i - 1.5) * (amplada + 0.012) for j in range(len(preguntes))]
    ax.bar(xs, mitjanes, width=amplada, color=color, label=f"{curt} (n = {len(grup)})")
    for x, m in zip(xs, mitjanes):
        ax.text(x, m + 0.05, f"{m:.1f}".replace(".", ","), ha="center", va="bottom", fontsize=9, color=TEXT)
ax.set_xticks(range(len(preguntes)), [p for _, p in preguntes])
ax.set_ylim(0, 5.6)
ax.set_yticks(range(0, 6))
ax.yaxis.grid(True, color=GRAELLA, linewidth=0.8)
ax.set_axisbelow(True)
ax.tick_params(axis="x", length=0)
ax.set_ylabel("Mitjana (1–5)")
ax.legend(frameon=False, ncol=2, loc="upper left", bbox_to_anchor=(0, -0.13), labelcolor=TEXT)
titol(ax, "Valoració mitjana segons el perfil", "Escala de 1 (gens) a 5 (molt)")
desa(fig, "10-comparativa-perfils.png")

print("Gràfics generats a", SORTIDA)
