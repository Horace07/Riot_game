# -*- coding: utf-8 -*-
import json, os
import pandas as pd
from typing import Dict, Any, List
from metrics import extract_participant_metrics, team_kills_by_team
from config import (
    RAW_JSON_PATH, RAW_PARQUET_PATH, USE_PARQUET_IF_EXISTS,
    MAX_MATCHES_PER_PLAYER, WEIGHTS_SOLO, WEIGHTS_TEAM, NORMALIZATION
)

def load_raw() -> List[Dict[str, Any]]:
    if USE_PARQUET_IF_EXISTS and os.path.exists(RAW_PARQUET_PATH):
        df = pd.read_parquet(RAW_PARQUET_PATH)
        return df.to_dict("records")
    with open(RAW_JSON_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def flatten_records(raw: List[Dict[str, Any]]) -> pd.DataFrame:
    """
    Attendu: raw = [ { "summonerName": "...", "puuid": "...", "matches":[ {match}, ... ] }, ... ]
    Sort un DF au grain "player x match" avec KPIs par match.
    """
    rows = []
    for player in raw:
        puuid = player.get("puuid")
        name = player.get("summonerName") or player.get("name")
        matches = player.get("matches", [])
        if isinstance(matches, list) and MAX_MATCHES_PER_PLAYER:
            matches = matches[:MAX_MATCHES_PER_PLAYER]
        else:
            matches = matches if isinstance(matches, list) else []

        for m in matches:
            info = m.get("info", {})
            parts = info.get("participants", [])
            if not parts:
                continue

            # team kills map
            tmap = team_kills_by_team(parts)

            # participant du joueur
            me = next((p for p in parts if p.get("puuid") == puuid), None)
            if me is None:
                # fallback: si pas de puuid matché, passer (ok)
                continue

            met = extract_participant_metrics(me, tmap)
            rows.append({
                "puuid": puuid,
                "summonerName": name,
                "matchId": m.get("metadata", {}).get("matchId") or m.get("matchId"),
                **met
            })
    return pd.DataFrame(rows)

def aggregate_player_level(df: pd.DataFrame) -> pd.DataFrame:
    """
    Moyennes par joueur. Winrate = moyenne de win (0/1).
    """
    if df.empty:
        return pd.DataFrame(columns=[
            "puuid","summonerName",
            "kda","winrate","dpm","cs_per_min","gpm","solo_kills",
            "assists_per_game","vision_per_min","kill_participation","team_damage_pct",
            "time_ccing_others","objectives_taken"
        ])
    agg_map = {
        "kda": "mean",
        "win": "mean",
        "dpm": "mean",
        "cs_per_min": "mean",
        "gpm": "mean",
        "solo_kills": "mean",

        "assists_per_game": "mean",
        "vision_per_min": "mean",
        "kill_participation": "mean",
        "team_damage_pct": "mean",
        "time_ccing_others": "mean",
        "objectives_taken": "mean",

        "summonerName": "first"
    }
    out = df.groupby("puuid", as_index=False).agg(agg_map)
    out = out.rename(columns={"win": "winrate"})
    return out

# —— Normalisation → scores /100 ——
def minmax_norm(s: pd.Series) -> pd.Series:
    lo, hi = s.min(), s.max()
    if pd.isna(lo) or pd.isna(hi) or hi == lo:
        return pd.Series([50.0]*len(s), index=s.index)
    return (s - lo) / (hi - lo) * 100.0

def zscore_norm(s: pd.Series) -> pd.Series:
    mu, sd = s.mean(), s.std(ddof=0)
    if pd.isna(mu) or pd.isna(sd) or sd == 0:
        return pd.Series([50.0]*len(s), index=s.index)
    mapped = 50.0 + 10.0 * ((s - mu) / sd)
    return mapped.clip(lower=0.0, upper=100.0)

def normalize(df: pd.DataFrame, cols: List[str]) -> pd.DataFrame:
    norm_fn = minmax_norm if NORMALIZATION.lower() == "minmax" else zscore_norm
    res = df.copy()
    for c in cols:
        if c in res.columns:
            res[f"{c}_score"] = norm_fn(res[c].astype(float))
        else:
            res[f"{c}_score"] = 50.0
    return res

def weighted_sum(row: pd.Series, weights: Dict[str, float], suffix="_score") -> float:
    total = 0.0
    for k, w in weights.items():
        total += w * float(row.get(f"{k}{suffix}", 50.0))
    return total

def compute_scores(players: pd.DataFrame) -> pd.DataFrame:
    # Colonnes à normaliser (issues des pondérations)
    kp_solo = list(WEIGHTS_SOLO.keys())
    kp_team = list(WEIGHTS_TEAM.keys())
    norm_cols = sorted(set(kp_solo + kp_team))

    z = normalize(players, norm_cols)

    z["solo_score"] = z.apply(lambda r: weighted_sum(r, WEIGHTS_SOLO), axis=1)
    z["team_score"] = z.apply(lambda r: weighted_sum(r, WEIGHTS_TEAM), axis=1)
    z["overall_score"] = 0.5 * z["solo_score"] + 0.5 * z["team_score"]

    cols = [
        "puuid","summonerName",
        # Raw KPIs
        "kda","winrate","dpm","cs_per_min","gpm","solo_kills",
        "assists_per_game","vision_per_min","kill_participation","team_damage_pct",
        "time_ccing_others","objectives_taken",
        # Scores
        "kda_score","winrate_score","dpm_score","cs_per_min_score","gpm_score","solo_kills_score",
        "assists_per_game_score","vision_per_min_score","kill_participation_score","team_damage_pct_score",
        "time_ccing_others_score","objectives_taken_score",
        "solo_score","team_score","overall_score"
    ]
    return z[cols]

def main():
    raw = load_raw()
    match_df = flatten_records(raw)
    players = aggregate_player_level(match_df)
    scores = compute_scores(players)

    os.makedirs("data/processed", exist_ok=True)
    scores.to_csv("data/processed/players_scores.csv", index=False)
    scores.to_parquet("data/processed/players_scores.parquet", index=False)
    print(f"OK - {len(scores)} joueurs scorés → data/processed/players_scores.*")

if __name__ == "__main__":
    main()
