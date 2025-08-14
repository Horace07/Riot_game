# -*- coding: utf-8 -*-

RAW_JSON_PATH = "data/raw/riot_raw.json"
RAW_PARQUET_PATH = "data/raw/riot_raw.parquet"
USE_PARQUET_IF_EXISTS = True

# Limiter le nb de matchs par joueur utilisés pour les moyennes
MAX_MATCHES_PER_PLAYER = 50

# —— Pondérations des scores (somme = 1.0) ——
WEIGHTS_SOLO = {
    "kda": 0.25,
    "winrate": 0.20,
    "dpm": 0.20,
    "cs_per_min": 0.15,
    "gpm": 0.15,              # Gold per minute
    "solo_kills": 0.05
}

WEIGHTS_TEAM = {
    "assists_per_game": 0.25,
    "vision_per_min": 0.20,
    "kill_participation": 0.20,
    "team_damage_pct": 0.20,  # challenges.teamDamagePercentage
    "time_ccing_others": 0.10,
    "objectives_taken": 0.05  # dragons + baron + herald + towers
}

# Normalisation: "minmax" (0..100) ou "zscore" (centrée)
NORMALIZATION = "minmax"
