# Riot Game Ingestion & KPIs

Scripts pour récupérer les données des joueurs top 1% depuis l'API Riot Games
et calculer des indicateurs de performance (KPIs) ainsi que des scores.

## Prérequis
- Python 3.9+
- Créer un fichier `.env` avec:
  ```env
  RIOT_API_KEY=YOUR_API_KEY
  REGION=EUW1
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

## CI
Deux jobs GitLab CI exécutent respectivement l'ingestion puis la transformation,
et conservent les jeux de données générés comme artefacts pendant une semaine.
