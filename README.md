# Riot Game Ingestion

Script d'ingestion pour récupérer les données des joueurs top 1% depuis l'API Riot Games.

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

## Exécution
```
python src/ingest.py
```
Les données brutes sont stockées dans `data/raw/riot_raw.json` et `data/raw/riot_raw.parquet`.

## CI
Un job GitLab CI exécute le script d'ingestion et conserve les données produites comme artefacts pendant une semaine.
