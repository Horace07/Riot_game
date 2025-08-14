import json
import os
from pathlib import Path
from typing import List, Dict

import pandas as pd
import requests
from dotenv import load_dotenv


load_dotenv()
API_KEY = os.getenv("RIOT_API_KEY")
REGION = os.getenv("REGION", "EUW1")

HEADERS = {"X-Riot-Token": API_KEY} if API_KEY else {}

LEAGUE_URL = f"https://{REGION}.api.riotgames.com/lol/league/v4/challengerleagues/by-queue/RANKED_SOLO_5x5"
SUMMONER_URL = f"https://{REGION}.api.riotgames.com/lol/summoner/v4/summoners/{{}}"
MATCHLIST_URL = f"https://{REGION}.api.riotgames.com/lol/match/v5/matches/by-puuid/{{}}/ids"
MATCH_URL = f"https://{REGION}.api.riotgames.com/lol/match/v5/matches/{{}}"


def get_json(url: str) -> Dict:
    resp = requests.get(url, headers=HEADERS, timeout=10)
    resp.raise_for_status()
    return resp.json()


def main(limit_players: int = 5, limit_matches: int = 5) -> None:
    if not API_KEY or API_KEY == "YOUR_API_KEY":
        raise RuntimeError("RIOT_API_KEY is not set. Please update the .env file.")

    raw_dir = Path("data/raw")
    raw_dir.mkdir(parents=True, exist_ok=True)

    league_data = get_json(LEAGUE_URL)
    players = league_data.get("entries", [])[:limit_players]

    results: List[Dict] = []

    for player in players:
        summoner_id = player.get("summonerId")
        summoner_name = player.get("summonerName")
        summoner_info = get_json(SUMMONER_URL.format(summoner_id))
        puuid = summoner_info.get("puuid")

        match_ids = get_json(MATCHLIST_URL.format(puuid))[:limit_matches]
        match_details = []
        for match_id in match_ids:
            match = get_json(MATCH_URL.format(match_id))
            participant = next((p for p in match["info"]["participants"] if p["puuid"] == puuid), {})
            match_details.append({
                "matchId": match_id,
                "championName": participant.get("championName"),
                "kills": participant.get("kills"),
                "deaths": participant.get("deaths"),
                "assists": participant.get("assists"),
                "win": participant.get("win"),
                "teamId": participant.get("teamId"),
            })

        results.append({
            "summonerName": summoner_name,
            "soloRank": "Challenger",
            "puuid": puuid,
            "matches": match_details,
        })

    json_path = raw_dir / "riot_raw.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    records = []
    for player in results:
        for match in player["matches"]:
            records.append({
                "summonerName": player["summonerName"],
                "puuid": player["puuid"],
                **match,
            })

    df = pd.DataFrame(records)
    df.to_parquet(raw_dir / "riot_raw.parquet", index=False)
    print(f"Saved {json_path} and {raw_dir / 'riot_raw.parquet'}")


if __name__ == "__main__":
    main()
