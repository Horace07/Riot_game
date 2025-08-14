# -*- coding: utf-8 -*-
import os
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, select
from db import create_tables, ENGINE_URL, Player
from sqlalchemy.orm import Session

load_dotenv()

CSV_PATH = os.getenv("PROCESSED_CSV", "data/processed/players_scores.csv")
PARQUET_PATH = os.getenv("PROCESSED_PARQUET", "data/processed/players_scores.parquet")

# mapping colonnes attendues → modèle
EXPECTED_COLS = [
    "puuid","summonerName",
    "kda","winrate","dpm","cs_per_min","gpm","solo_kills",
    "assists_per_game","vision_per_min","kill_participation","team_damage_pct",
    "time_ccing_others","objectives_taken",
    "kda_score","winrate_score","dpm_score","cs_per_min_score","gpm_score","solo_kills_score",
    "assists_per_game_score","vision_per_min_score","kill_participation_score","team_damage_pct_score",
    "time_ccing_others_score","objectives_taken_score",
    "solo_score","team_score","overall_score"
]

def load_processed_df() -> pd.DataFrame:
    if os.path.exists(PARQUET_PATH):
        df = pd.read_parquet(PARQUET_PATH)
    elif os.path.exists(CSV_PATH):
        df = pd.read_csv(CSV_PATH)
    else:
        raise FileNotFoundError("Aucun fichier trouvé dans data/processed/")
    # garder uniquement les colonnes utiles & types numériques
    missing = [c for c in EXPECTED_COLS if c not in df.columns]
    if missing:
        raise ValueError(f"Colonnes manquantes dans le processed: {missing}")
    # cast sûrs
    for c in EXPECTED_COLS:
        if c in ("puuid","summonerName"):
            continue
        df[c] = pd.to_numeric(df[c], errors="coerce")
    # drop NA puuid
    df = df.dropna(subset=["puuid"]).copy()
    return df[EXPECTED_COLS]

def upsert_players(df: pd.DataFrame):
    engine = create_engine(ENGINE_URL, future=True)
    create_tables()
    with Session(engine) as ses:
        # UPSERT basique : on remplace si puuid existe (delete/insert)
        # (Simple et portable ; si besoin d'UPSERT natif → ON CONFLICT en SQL brut)
        existing = {r[0] for r in ses.execute(select(Player.puuid)).all()}
        insert_rows = []
        for _, row in df.iterrows():
            if row.puuid in existing:
                # update existant
                ses.query(Player).filter(Player.puuid == row.puuid).update(
                    {k: row[k] for k in df.columns if k != "puuid"},
                    synchronize_session=False
                )
            else:
                insert_rows.append(Player(**row.to_dict()))
        if insert_rows:
            ses.add_all(insert_rows)
        ses.commit()

if __name__ == "__main__":
    df = load_processed_df()
    upsert_players(df)
    print(f"OK - {len(df)} joueurs chargés/à jour dans Postgres.")
