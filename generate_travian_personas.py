#!/usr/bin/env python3
"""Generate the base_travian_hq simulation with 9 manager personas.

Creates the full bootstrap directory structure including:
- reverie/meta.json
- environment/0.json
- personas/<name>/bootstrap_memory/ (scratch, spatial_memory, associative_memory)
"""
import json
import os

from generate_travian_hq import get_spawn_coordinates

STORAGE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "environment", "frontend_server", "storage", "base_travian_hq",
)

# ── Spatial memory (shared by all personas — they all know the HQ) ──
SPATIAL_MEMORY = {
    "travian hq": {
        "Command Center": {
            "Strategy Hall": [
                "command_chair", "phase_board", "village_map",
            ],
            "War Room": [
                "war_table", "threat_board", "alarm_bell",
            ],
            "Briefing Room": [
                "briefing_table", "projection_screen",
            ],
        },
        "Economic Wing": {
            "Treasury": [
                "resource_ledger", "merchant_desk", "gold_vault",
            ],
            "Construction Yard": [
                "blueprint_table", "building_queue_board", "tool_rack",
            ],
            "Training Grounds": [
                "training_dummy", "barracks_desk", "troop_roster",
            ],
        },
        "Intelligence Wing": {
            "Archives": [
                "config_scroll", "village_registry", "profile_cabinet",
            ],
            "Scout Tower": [
                "telescope", "statistics_board", "resource_scanner",
            ],
        },
        "Operations Wing": {
            "Focus Chamber": [
                "focus_crystal", "plan_board", "priority_list",
            ],
            "Logic Lab": [
                "validation_orb", "rule_book",
            ],
        },
        "Commons": {
            "Mess Hall": [
                "dining_table", "food_counter", "notice_board",
            ],
            "Courtyard": [
                "fountain", "bench", "garden",
            ],
        },
    }
}

# ── Persona definitions ──
PERSONAS = [
    {
        "name": "Commander Marcus",
        "first_name": "Commander",
        "last_name": "Marcus",
        "age": 45,
        "innate": "authoritative, strategic, decisive",
        "learned": "Commander Marcus is the leader of Travian Bot operations. He coordinates all specialist managers through 14 operational phases each cycle, monitoring progress from the Strategy Hall. He reviews phase boards, issues directives, and ensures each cycle completes successfully.",
        "currently": "Commander Marcus is overseeing the current operational cycle, checking village profiles and coordinating with all managers to ensure smooth resource flow and construction progress across the empire.",
        "lifestyle": "Commander Marcus arrives at the Strategy Hall at 6am and works until midnight, taking short breaks in the Mess Hall.",
        "living_area": "travian hq:Command Center:Strategy Hall",
        "daily_plan_req": "Commander Marcus coordinates all 14 phases of each operational cycle from the Strategy Hall, consulting with each manager as their phase comes up.",
    },
    {
        "name": "Archivist Petra",
        "first_name": "Archivist",
        "last_name": "Petra",
        "age": 38,
        "innate": "meticulous, organized, detail-oriented",
        "learned": "Archivist Petra maintains the village profiles and configuration registry. She classifies villages into tiers (main, developed, developing, grey_zone) and manages focus plans. She ensures all configuration data is accurate and up-to-date.",
        "currently": "Archivist Petra is updating the village registry with the latest tier classifications and reviewing focus plans for the upcoming operational cycle.",
        "lifestyle": "Archivist Petra works from 7am to 9pm in the Archives, organizing scrolls and updating the village registry.",
        "living_area": "travian hq:Intelligence Wing:Archives",
        "daily_plan_req": "Archivist Petra reviews and updates village profiles at the start of each cycle, then maintains configuration records throughout the day.",
    },
    {
        "name": "Scout Varro",
        "first_name": "Scout",
        "last_name": "Varro",
        "age": 32,
        "innate": "observant, quick, analytical",
        "learned": "Scout Varro performs reconnaissance before each operational cycle. He scans statistics pages, caches warehouse capacities, resource levels and production rates, and reports capacity data to the team from his Scout Tower.",
        "currently": "Scout Varro is running preflight scans across all villages, gathering the latest warehouse levels, production rates, and training queues.",
        "lifestyle": "Scout Varro wakes early at 5am to begin his scans. He works from the Scout Tower until 8pm.",
        "living_area": "travian hq:Intelligence Wing:Scout Tower",
        "daily_plan_req": "Scout Varro runs comprehensive preflight reconnaissance at the start of each cycle, scanning all villages for resource levels, warehouse capacity, and training status.",
    },
    {
        "name": "Treasurer Lucius",
        "first_name": "Treasurer",
        "last_name": "Lucius",
        "age": 50,
        "innate": "cautious, calculating, fair",
        "learned": "Treasurer Lucius manages all resource transfers between villages. He handles overflow to main, support to developing villages, crop redistribution, and emergency resource management. He tracks merchant capacity carefully.",
        "currently": "Treasurer Lucius is reviewing resource levels across all villages and planning transfers to optimize storage and prevent overflow.",
        "lifestyle": "Treasurer Lucius works from 7am to 10pm in the Treasury, carefully managing ledgers and calculating optimal transfer routes.",
        "living_area": "travian hq:Economic Wing:Treasury",
        "daily_plan_req": "Treasurer Lucius manages multiple rounds of resource transfers each cycle: developed to grey zone support, overflow to main, developed to developing support, excess back to main, and crop redistribution.",
    },
    {
        "name": "Builder Gaius",
        "first_name": "Builder",
        "last_name": "Gaius",
        "age": 35,
        "innate": "pragmatic, industrious, patient",
        "learned": "Builder Gaius oversees all construction across the empire. He executes CSV-based build queues for developing villages, upgrades grey zone settlements, and manages main village resource field upgrades. He reads blueprint tables and manages the building queue board.",
        "currently": "Builder Gaius is reviewing the current build queues and planning which buildings to upgrade next based on available resources.",
        "lifestyle": "Builder Gaius starts work at 6am in the Construction Yard and works until 9pm, reviewing blueprints and managing queues.",
        "living_area": "travian hq:Economic Wing:Construction Yard",
        "daily_plan_req": "Builder Gaius handles grey zone upgrades, developing village upgrades, and main village field upgrades during different phases of each operational cycle.",
    },
    {
        "name": "Centurion Titus",
        "first_name": "Centurion",
        "last_name": "Titus",
        "age": 40,
        "innate": "disciplined, aggressive, protective",
        "learned": "Centurion Titus manages troop training across all villages. He handles main crop emergencies by training cavalry, runs developed village defense training in barracks and stables, and manages NPC trade when crop is critical.",
        "currently": "Centurion Titus is reviewing troop rosters and planning the next round of barracks and stable training for defense troops.",
        "lifestyle": "Centurion Titus trains from dawn at 5am until 10pm. He is always ready for crop emergencies.",
        "living_area": "travian hq:Economic Wing:Training Grounds",
        "daily_plan_req": "Centurion Titus handles main crop emergency checks, then runs troop training for main and developed villages during their respective phases.",
    },
    {
        "name": "Strategist Livia",
        "first_name": "Strategist",
        "last_name": "Livia",
        "age": 36,
        "innate": "focused, creative, adaptable",
        "learned": "Strategist Livia executes special focus plans that override normal operations. She handles custom build sequences, resource gathering targets, and priority overrides based on the current strategic needs of the empire.",
        "currently": "Strategist Livia is reviewing the current focus plan entries and preparing to execute priority actions for targeted villages.",
        "lifestyle": "Strategist Livia works from 8am to 9pm in the Focus Chamber, studying plans and executing custom operations.",
        "living_area": "travian hq:Operations Wing:Focus Chamber",
        "daily_plan_req": "Strategist Livia executes focus plans during the dedicated focus phase, coordinating with Builder Gaius and Treasurer Lucius for resource support.",
    },
    {
        "name": "Sentinel Felix",
        "first_name": "Sentinel",
        "last_name": "Felix",
        "age": 28,
        "innate": "alert, reactive, fearless",
        "learned": "Sentinel Felix monitors all villages for incoming attacks on a separate thread. He detects hostile movements from the rally point, evaluates threat levels, classifies attack types, and initiates troop and resource evacuation to safe targets.",
        "currently": "Sentinel Felix is monitoring the threat board for incoming attacks and maintaining readiness for emergency dodge operations.",
        "lifestyle": "Sentinel Felix is always on duty in the War Room, monitoring threats 24 hours a day with rotating watch shifts.",
        "living_area": "travian hq:Command Center:War Room",
        "daily_plan_req": "Sentinel Felix continuously monitors for incoming attacks, evaluates threats, and coordinates dodge responses when hostile movements are detected.",
    },
    {
        "name": "Validator Quintus",
        "first_name": "Validator",
        "last_name": "Quintus",
        "age": 55,
        "innate": "thorough, skeptical, precise",
        "learned": "Validator Quintus performs validation and consistency checks on all manager outputs. He verifies build plans against resource availability, checks resource calculations, and ensures operational logic is sound before actions are taken.",
        "currently": "Validator Quintus is reviewing the latest operational data for inconsistencies and validating the resource calculations from Treasurer Lucius.",
        "lifestyle": "Validator Quintus works methodically from 7am to 8pm in the Logic Lab, cross-referencing data and running validation checks.",
        "living_area": "travian hq:Operations Wing:Logic Lab",
        "daily_plan_req": "Validator Quintus runs validation checks throughout the operational cycle, verifying each manager's outputs before actions are committed.",
    },
]


def make_scratch(persona_def):
    """Create a scratch.json for a persona, matching the Isabella format."""
    return {
        "vision_r": 8,
        "att_bandwidth": 8,
        "retention": 8,
        "curr_time": None,
        "curr_tile": None,
        "daily_plan_req": persona_def["daily_plan_req"],
        "name": persona_def["name"],
        "first_name": persona_def["first_name"],
        "last_name": persona_def["last_name"],
        "age": persona_def["age"],
        "innate": persona_def["innate"],
        "learned": persona_def["learned"],
        "currently": persona_def["currently"],
        "lifestyle": persona_def["lifestyle"],
        "living_area": persona_def["living_area"],
        "concept_forget": 100,
        "daily_reflection_time": 180,
        "daily_reflection_size": 5,
        "overlap_reflect_th": 4,
        "kw_strg_event_reflect_th": 10,
        "kw_strg_thought_reflect_th": 9,
        "recency_w": 1,
        "relevance_w": 1,
        "importance_w": 1,
        "recency_decay": 0.995,
        "importance_trigger_max": 150,
        "importance_trigger_curr": 150,
        "importance_ele_n": 0,
        "thought_count": 5,
        "daily_req": [],
        "f_daily_schedule": [],
        "f_daily_schedule_hourly_org": [],
        "act_address": None,
        "act_start_time": None,
        "act_duration": None,
        "act_description": None,
        "act_pronunciatio": None,
        "act_event": [persona_def["name"], None, None],
        "act_obj_description": None,
        "act_obj_pronunciatio": None,
        "act_obj_event": [None, None, None],
        "chatting_with": None,
        "chat": None,
        "chatting_with_buffer": {},
        "chatting_end_time": None,
        "act_path_set": False,
        "planned_path": [],
    }


def main():
    coords = get_spawn_coordinates()

    # ── Create directory structure ──
    print(f"Creating base simulation at: {STORAGE}")

    # reverie/meta.json
    meta_dir = os.path.join(STORAGE, "reverie")
    os.makedirs(meta_dir, exist_ok=True)
    meta = {
        "fork_sim_code": "base_travian_hq",
        "start_date": "February 23, 2026",
        "curr_time": "February 23, 2026, 00:00:00",
        "sec_per_step": 10,
        "maze_name": "travian_hq",
        "persona_names": [p["name"] for p in PERSONAS],
        "step": 0,
    }
    with open(os.path.join(meta_dir, "meta.json"), "w") as f:
        json.dump(meta, f, indent=2)
    print("  Written: reverie/meta.json")

    # environment/0.json
    env_dir = os.path.join(STORAGE, "environment")
    os.makedirs(env_dir, exist_ok=True)
    env_0 = {}
    for p in PERSONAS:
        if p["name"] in coords:
            env_0[p["name"]] = coords[p["name"]]
        else:
            # Fallback: center of map
            env_0[p["name"]] = {"maze": "travian_hq", "x": 30, "y": 25}
    with open(os.path.join(env_dir, "0.json"), "w") as f:
        json.dump(env_0, f, indent=2)
    print("  Written: environment/0.json")

    # Personas
    for p in PERSONAS:
        persona_dir = os.path.join(STORAGE, "personas", p["name"], "bootstrap_memory")
        assoc_dir = os.path.join(persona_dir, "associative_memory")
        os.makedirs(assoc_dir, exist_ok=True)

        # scratch.json
        scratch = make_scratch(p)
        with open(os.path.join(persona_dir, "scratch.json"), "w") as f:
            json.dump(scratch, f, indent=2)

        # spatial_memory.json
        with open(os.path.join(persona_dir, "spatial_memory.json"), "w") as f:
            json.dump(SPATIAL_MEMORY, f, indent=2)

        # associative_memory (empty)
        with open(os.path.join(assoc_dir, "nodes.json"), "w") as f:
            json.dump({}, f)
        with open(os.path.join(assoc_dir, "kw_strength.json"), "w") as f:
            json.dump({"kw_strength_event": {}, "kw_strength_thought": {}}, f)
        with open(os.path.join(assoc_dir, "embeddings.json"), "w") as f:
            json.dump({}, f)

        print(f"  Written: personas/{p['name']}/bootstrap_memory/")

    print()
    print("Done! Base simulation created successfully.")
    print(f"  Personas: {len(PERSONAS)}")
    print(f"  Location: {STORAGE}")


if __name__ == "__main__":
    main()
