# Riot Game Ingestion & KPIs

Scripts pour récupérer les données des joueurs top 1% depuis l'API Riot Games
et calculer des indicateurs de performance (KPIs) ainsi que des scores.

## Prérequis
- Python 3.9+
- Créer un fichier `.env` avec au minimum:
  ```env
  RIOT_API_KEY=YOUR_API_KEY
  REGION=EUW1

  # Base Postgres locale
  PG_HOST=localhost
  PG_PORT=5432
  PG_DB=rg_db
  PG_USER=rg_user
  PG_PASSWORD=rg_pass

  PROCESSED_CSV=data/processed/players_scores.csv
  PROCESSED_PARQUET=data/processed/players_scores.parquet
  ```

## Installation
```
pip install -r requirements.txt
```

## Ingestion des données
```
python src/ingest.py
```
Les données brutes sont stockées dans `data/raw/riot_raw.json` et `data/raw/riot_raw.parquet`.

## Transformation & KPIs
```bash
python src/transform.py
```
Les scores sont produits dans `data/processed/players_scores.csv` et `data/processed/players_scores.parquet`.

## Chargement en base Postgres
1. Lancer la base locale:
   ```bash
   docker compose up -d
   ```
2. Créer les tables:
   ```bash
   python src/db.py
   ```
3. Charger les joueurs scorés:
   ```bash
   python src/load_db.py
   ```
Les données sont insérées/actualisées dans la table `players` de la base Postgres.

## CI
Trois jobs GitLab CI exécutent l'ingestion, la transformation puis le chargement en base.
Les artefacts produits sont conservés pendant une semaine.
