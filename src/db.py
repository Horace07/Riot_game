# -*- coding: utf-8 -*-
import os
from dotenv import load_dotenv
from sqlalchemy import (
    create_engine, String, Float, Integer, Column, Index
)
from sqlalchemy.orm import declarative_base

load_dotenv()

PG_HOST = os.getenv("PG_HOST", "localhost")
PG_PORT = os.getenv("PG_PORT", "5432")
PG_DB   = os.getenv("PG_DB", "rg_db")
PG_USER = os.getenv("PG_USER", "rg_user")
PG_PWD  = os.getenv("PG_PASSWORD", "rg_pass")

ENGINE_URL = f"postgresql+psycopg2://{PG_USER}:{PG_PWD}@{PG_HOST}:{PG_PORT}/{PG_DB}"
engine = create_engine(ENGINE_URL, echo=False, future=True)
Base = declarative_base()

class Player(Base):
    __tablename__ = "players"
    # Clé fonctionnelle : puuid unique (un joueur = 1 ligne agrégée)
    puuid = Column(String(128), primary_key=True)
    summonerName = Column(String(64), nullable=True)

    # KPIs “raw” agrégés (moyennes) — étape 2
    kda = Column(Float); winrate = Column(Float); dpm = Column(Float)
    cs_per_min = Column(Float); gpm = Column(Float); solo_kills = Column(Float)
    assists_per_game = Column(Float); vision_per_min = Column(Float)
    kill_participation = Column(Float); team_damage_pct = Column(Float)
    time_ccing_others = Column(Float); objectives_taken = Column(Float)

    # Scores /100
    kda_score = Column(Float); winrate_score = Column(Float); dpm_score = Column(Float)
    cs_per_min_score = Column(Float); gpm_score = Column(Float); solo_kills_score = Column(Float)
    assists_per_game_score = Column(Float); vision_per_min_score = Column(Float)
    kill_participation_score = Column(Float); team_damage_pct_score = Column(Float)
    time_ccing_others_score = Column(Float); objectives_taken_score = Column(Float)

    # Scores finaux
    solo_score = Column(Float); team_score = Column(Float); overall_score = Column(Float)

# Index utiles pour filtres courants
Index("ix_players_overall_desc", Player.overall_score.desc())
Index("ix_players_team_desc", Player.team_score.desc())
Index("ix_players_solo_desc", Player.solo_score.desc())
Index("ix_players_name", Player.summonerName)

def create_tables():
    Base.metadata.create_all(engine)

if __name__ == "__main__":
    create_tables()
    print("OK - Schéma créé.")
