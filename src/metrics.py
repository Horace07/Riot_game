# -*- coding: utf-8 -*-
from __future__ import annotations
from typing import Dict, Any, List

def safe_div(a: float, b: float) -> float:
    return a / b if b else 0.0

def kda(kills: float, deaths: float, assists: float) -> float:
    return (kills + assists) / max(1.0, deaths)

def per_min(val: float, time_seconds: float) -> float:
    return safe_div(val, max(1.0, time_seconds / 60.0))

def extract_challenge(p: Dict[str, Any], key: str, default: float = 0.0) -> float:
    ch = p.get("challenges") or {}
    try:
        v = float(ch.get(key, default))
        # Certaines métriques sont déjà normalisées (ex: teamDamagePercentage 0..1)
        return v
    except Exception:
        return default

def team_kills_by_team(participants: List[Dict[str, Any]]) -> Dict[int, int]:
    agg = {}
    for m in participants:
        tid = int(m.get("teamId", 0))
        agg[tid] = agg.get(tid, 0) + int(m.get("kills", 0))
    return agg

def kill_participation(kills: float, assists: float, team_kills: float) -> float:
    # 0..1+
    return safe_div(kills + assists, max(1.0, team_kills))

def extract_participant_metrics(p: Dict[str, Any], team_kills_map: Dict[int, int]) -> Dict[str, float]:
    """
    p = participant (info.participants[i])
    team_kills_map = { teamId -> total team kills }
    Sort une dict de KPIs par match.
    """
    # Champs de base
    kills   = float(p.get("kills", 0))
    deaths  = float(p.get("deaths", 0))
    assists = float(p.get("assists", 0))
    win     = 1.0 if bool(p.get("win", False)) else 0.0

    time_sec = float(
        p.get("timePlayed", p.get("gameDuration", 0))
    )
    dmg_champ = float(p.get("totalDamageDealtToChampions", 0))
    cs_total  = float(p.get("totalMinionsKilled", 0)) + float(p.get("neutralMinionsKilled", 0))
    gold_earned = float(p.get("goldEarned", 0))
    vision_score = float(p.get("visionScore", 0))
    team_id = int(p.get("teamId", 0))
    team_k = float(team_kills_map.get(team_id, 0))

    # Challenges (quand dispo)
    dpm_chal = extract_challenge(p, "damagePerMinute", None)
    gpm_chal = extract_challenge(p, "goldPerMinute", None)
    vpm_chal = extract_challenge(p, "visionScorePerMinute", None)
    team_dmg_pct = extract_challenge(p, "teamDamagePercentage", 0.0)  # 0..1
    solo_kills = extract_challenge(p, "soloKills", float(p.get("soloKills", 0)))

    # Objectifs pris
    dragon_k = float(p.get("dragonKills", 0))
    baron_k  = float(p.get("baronKills", 0))
    herald_k = float(p.get("riftHeraldTakedowns", 0))
    tower_td = float(p.get("turretTakedowns", p.get("turretKills", 0)))

    # KPIs
    out = {
        # Solo side
        "win": win,
        "kda": kda(kills, deaths, assists),
        "dpm": dpm_chal if dpm_chal is not None else per_min(dmg_champ, time_sec),
        "cs_per_min": per_min(cs_total, time_sec),
        "gpm": gpm_chal if gpm_chal is not None else per_min(gold_earned, time_sec),
        "solo_kills": float(solo_kills),

        # Team side
        "assists_per_game": assists,
        "vision_per_min": vpm_chal if vpm_chal is not None else per_min(vision_score, time_sec),
        "kill_participation": kill_participation(kills, assists, team_k),  # 0..1+
        "team_damage_pct": float(team_dmg_pct),                            # 0..1
        "time_ccing_others": float(p.get("timeCCingOthers", 0.0)),         # secondes
        "objectives_taken": dragon_k + baron_k + herald_k + tower_td
    }
    return out
