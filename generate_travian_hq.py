#!/usr/bin/env python3
"""Generate the Travian HQ map data files for the generative agents simulation.

Creates all CSV maze files, special block definitions, metadata, and a minimal
Phaser-compatible Tiled JSON map for frontend rendering.

Map layout: 60x50 tiles, 4 rows x 3 columns of rooms with corridors.
"""
import csv
import json
import os

# ── Map dimensions ──────────────────────────────────────────────────
WIDTH = 60
HEIGHT = 50
TILE_SIZE = 32
COLLISION_ID = "32125"

# ── Block IDs ───────────────────────────────────────────────────────
WORLD_ID = "40001"

SECTOR_IDS = {
    "40101": "Command Center",
    "40102": "Economic Wing",
    "40103": "Intelligence Wing",
    "40104": "Operations Wing",
    "40105": "Commons",
}

ARENA_IDS = {
    "40201": "Strategy Hall",
    "40202": "War Room",
    "40203": "Briefing Room",
    "40204": "Treasury",
    "40205": "Construction Yard",
    "40206": "Training Grounds",
    "40207": "Archives",
    "40208": "Scout Tower",
    "40209": "Focus Chamber",
    "40210": "Logic Lab",
    "40211": "Mess Hall",
    "40212": "Courtyard",
}

GAME_OBJECT_IDS = {
    "40301": "command_chair",
    "40302": "phase_board",
    "40303": "village_map",
    "40304": "war_table",
    "40305": "threat_board",
    "40306": "alarm_bell",
    "40307": "briefing_table",
    "40308": "projection_screen",
    "40309": "resource_ledger",
    "40310": "merchant_desk",
    "40311": "gold_vault",
    "40312": "blueprint_table",
    "40313": "building_queue_board",
    "40314": "tool_rack",
    "40315": "training_dummy",
    "40316": "barracks_desk",
    "40317": "troop_roster",
    "40318": "config_scroll",
    "40319": "village_registry",
    "40320": "profile_cabinet",
    "40321": "telescope",
    "40322": "statistics_board",
    "40323": "resource_scanner",
    "40324": "focus_crystal",
    "40325": "plan_board",
    "40326": "priority_list",
    "40327": "validation_orb",
    "40328": "rule_book",
    "40329": "dining_table",
    "40330": "food_counter",
    "40331": "notice_board",
    "40332": "fountain",
    "40333": "bench",
    "40334": "garden",
}

SPAWN_IDS = {
    "40401": "marcus-sp-A",
    "40402": "petra-sp-A",
    "40403": "varro-sp-A",
    "40404": "lucius-sp-A",
    "40405": "gaius-sp-A",
    "40406": "titus-sp-A",
    "40407": "livia-sp-A",
    "40408": "felix-sp-A",
    "40409": "quintus-sp-A",
}

# ── Room definitions ────────────────────────────────────────────────
# Each room: (row_start, row_end, col_start, col_end, sector_id, arena_id,
#              game_objects: [(rel_row, rel_col, obj_id), ...],
#              spawn: (rel_row, rel_col, spawn_id))
# Coordinates are inclusive.

# 4 rows of rooms, 3 columns each
# Row 0: wall, Rows 1-2: corridor, Rows 3-12: top rooms, Rows 13-14: corridor,
# Rows 15-24: mid rooms, Rows 25-26: corridor, Rows 27-36: bot-upper rooms,
# Rows 37-38: corridor, Rows 39-48: bot rooms, Row 49: wall
# Col 0: wall, Cols 1-2: corridor, Cols 3-17: col1, Cols 18-19: corridor,
# Cols 20-38: col2, Cols 39-40: corridor, Cols 41-57: col3, Cols 58-59: wall

ROOMS = [
    # ── Top row (rows 3-12) ── Command Center ──
    {
        "rows": (3, 12), "cols": (3, 17),
        "sector": "40101", "arena": "40201",  # Command Center / Strategy Hall
        "objects": [
            (2, 3, "40301"),  # command_chair
            (2, 8, "40302"),  # phase_board
            (5, 5, "40303"),  # village_map
        ],
        "spawn": (4, 7, "40401"),  # marcus-sp-A
    },
    {
        "rows": (3, 12), "cols": (20, 38),
        "sector": "40101", "arena": "40202",  # Command Center / War Room
        "objects": [
            (2, 4, "40304"),  # war_table
            (2, 10, "40305"),  # threat_board
            (5, 7, "40306"),  # alarm_bell
        ],
        "spawn": (4, 9, "40408"),  # felix-sp-A
    },
    {
        "rows": (3, 12), "cols": (41, 57),
        "sector": "40101", "arena": "40203",  # Command Center / Briefing Room
        "objects": [
            (3, 4, "40307"),  # briefing_table
            (3, 10, "40308"),  # projection_screen
        ],
        "spawn": (5, 8, None),  # No dedicated spawn (shared room)
    },

    # ── Middle row (rows 15-24) ── Economic Wing ──
    {
        "rows": (15, 24), "cols": (3, 17),
        "sector": "40102", "arena": "40204",  # Economic Wing / Treasury
        "objects": [
            (2, 3, "40309"),  # resource_ledger
            (2, 8, "40310"),  # merchant_desk
            (5, 5, "40311"),  # gold_vault
        ],
        "spawn": (4, 7, "40404"),  # lucius-sp-A
    },
    {
        "rows": (15, 24), "cols": (20, 38),
        "sector": "40102", "arena": "40205",  # Economic Wing / Construction Yard
        "objects": [
            (2, 4, "40312"),  # blueprint_table
            (2, 10, "40313"),  # building_queue_board
            (5, 7, "40314"),  # tool_rack
        ],
        "spawn": (4, 9, "40405"),  # gaius-sp-A
    },
    {
        "rows": (15, 24), "cols": (41, 57),
        "sector": "40102", "arena": "40206",  # Economic Wing / Training Grounds
        "objects": [
            (2, 4, "40315"),  # training_dummy
            (2, 10, "40316"),  # barracks_desk
            (5, 7, "40317"),  # troop_roster
        ],
        "spawn": (4, 8, "40406"),  # titus-sp-A
    },

    # ── Bottom-upper row (rows 27-36) ── Intelligence + Operations Wing ──
    {
        "rows": (27, 36), "cols": (3, 17),
        "sector": "40103", "arena": "40207",  # Intelligence Wing / Archives
        "objects": [
            (2, 3, "40318"),  # config_scroll
            (2, 8, "40319"),  # village_registry
            (5, 5, "40320"),  # profile_cabinet
        ],
        "spawn": (4, 7, "40402"),  # petra-sp-A
    },
    {
        "rows": (27, 36), "cols": (20, 38),
        "sector": "40103", "arena": "40208",  # Intelligence Wing / Scout Tower
        "objects": [
            (2, 4, "40321"),  # telescope
            (2, 10, "40322"),  # statistics_board
            (5, 7, "40323"),  # resource_scanner
        ],
        "spawn": (4, 9, "40403"),  # varro-sp-A
    },
    {
        "rows": (27, 36), "cols": (41, 57),
        "sector": "40104", "arena": "40209",  # Operations Wing / Focus Chamber
        "objects": [
            (2, 4, "40324"),  # focus_crystal
            (2, 10, "40325"),  # plan_board
            (5, 7, "40326"),  # priority_list
        ],
        "spawn": (4, 8, "40407"),  # livia-sp-A
    },

    # ── Bottom row (rows 39-48) ── Operations + Commons ──
    {
        "rows": (39, 48), "cols": (3, 17),
        "sector": "40104", "arena": "40210",  # Operations Wing / Logic Lab
        "objects": [
            (2, 3, "40327"),  # validation_orb
            (2, 8, "40328"),  # rule_book
        ],
        "spawn": (4, 7, "40409"),  # quintus-sp-A
    },
    {
        "rows": (39, 48), "cols": (20, 38),
        "sector": "40105", "arena": "40211",  # Commons / Mess Hall
        "objects": [
            (2, 4, "40329"),  # dining_table
            (2, 10, "40330"),  # food_counter
            (5, 9, "40331"),  # notice_board
        ],
        "spawn": None,
    },
    {
        "rows": (39, 48), "cols": (41, 57),
        "sector": "40105", "arena": "40212",  # Commons / Courtyard
        "objects": [
            (3, 4, "40332"),  # fountain
            (3, 10, "40333"),  # bench
            (6, 8, "40334"),  # garden
        ],
        "spawn": None,
    },
]


def generate_maze_csvs(base_path):
    """Generate all 5 maze CSV files as flat single-row arrays."""
    maze_dir = os.path.join(base_path, "matrix", "maze")
    os.makedirs(maze_dir, exist_ok=True)

    # Initialize grids with "0"
    collision = [["0"] * WIDTH for _ in range(HEIGHT)]
    sector = [["0"] * WIDTH for _ in range(HEIGHT)]
    arena = [["0"] * WIDTH for _ in range(HEIGHT)]
    game_object = [["0"] * WIDTH for _ in range(HEIGHT)]
    spawning = [["0"] * WIDTH for _ in range(HEIGHT)]

    # ── Collision: outer walls ──
    for col in range(WIDTH):
        collision[0][col] = COLLISION_ID
        collision[HEIGHT - 1][col] = COLLISION_ID
    for row in range(HEIGHT):
        collision[row][0] = COLLISION_ID
        collision[row][WIDTH - 1] = COLLISION_ID

    # ── Collision: room walls (border of each room) ──
    for room in ROOMS:
        r1, r2 = room["rows"]
        c1, c2 = room["cols"]
        # Top and bottom walls of room
        for col in range(c1, c2 + 1):
            collision[r1][col] = COLLISION_ID
            collision[r2][col] = COLLISION_ID
        # Left and right walls of room
        for row in range(r1, r2 + 1):
            collision[row][c1] = COLLISION_ID
            collision[row][c2] = COLLISION_ID
        # Door openings (center of top wall for rooms in rows 2-4,
        # center of left wall for some variety)
        door_col = (c1 + c2) // 2
        collision[r1][door_col] = "0"       # top door
        collision[r1][door_col + 1] = "0"   # wider door
        # Also add a left-side door for accessibility
        door_row = (r1 + r2) // 2
        collision[r1 + 1][c1] = "0"  # remove corner for pathability

    # ── Fill rooms with sector/arena/game_object/spawn data ──
    for room in ROOMS:
        r1, r2 = room["rows"]
        c1, c2 = room["cols"]
        sid = room["sector"]
        aid = room["arena"]

        # Fill interior (non-wall) tiles with sector and arena IDs
        for row in range(r1 + 1, r2):
            for col in range(c1 + 1, c2):
                sector[row][col] = sid
                arena[row][col] = aid

        # Place game objects at specific positions within the room
        for rel_row, rel_col, obj_id in room["objects"]:
            abs_row = r1 + rel_row
            abs_col = c1 + rel_col
            if 0 <= abs_row < HEIGHT and 0 <= abs_col < WIDTH:
                game_object[abs_row][abs_col] = obj_id

        # Place spawn point
        if room["spawn"]:
            rel_row, rel_col, spawn_id = room["spawn"]
            if spawn_id:
                abs_row = r1 + rel_row
                abs_col = c1 + rel_col
                if 0 <= abs_row < HEIGHT and 0 <= abs_col < WIDTH:
                    spawning[abs_row][abs_col] = spawn_id

    # ── Corridors: mark with sector of adjacent rooms ──
    # Horizontal corridors (rows 1-2, 13-14, 25-26, 37-38)
    corridor_rows = [(1, 2), (13, 14), (25, 26), (37, 38)]
    for cr1, cr2 in corridor_rows:
        for row in range(cr1, cr2 + 1):
            for col in range(1, WIDTH - 1):
                if collision[row][col] == "0":
                    # Leave as walkable corridor (no sector assignment needed
                    # for basic pathfinding, but we can assign a sector)
                    pass

    # Vertical corridors (cols 1-2, 18-19, 39-40, 58)
    # These are already walkable (not collision) by default

    # Write CSVs as single-row flat arrays
    def flatten_and_write(grid, filename):
        flat = []
        for row in grid:
            flat.extend(row)
        path = os.path.join(maze_dir, filename)
        with open(path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(flat)
        print(f"  Written: {filename} ({len(flat)} values)")

    flatten_and_write(collision, "collision_maze.csv")
    flatten_and_write(sector, "sector_maze.csv")
    flatten_and_write(arena, "arena_maze.csv")
    flatten_and_write(game_object, "game_object_maze.csv")
    flatten_and_write(spawning, "spawning_location_maze.csv")


def generate_special_blocks(base_path):
    """Generate all 5 special_blocks CSV files."""
    blocks_dir = os.path.join(base_path, "matrix", "special_blocks")
    os.makedirs(blocks_dir, exist_ok=True)

    # world_blocks.csv
    with open(os.path.join(blocks_dir, "world_blocks.csv"), "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([WORLD_ID, " travian hq"])
    print("  Written: world_blocks.csv")

    # sector_blocks.csv
    with open(os.path.join(blocks_dir, "sector_blocks.csv"), "w", newline="") as f:
        writer = csv.writer(f)
        for bid, name in SECTOR_IDS.items():
            writer.writerow([bid, " travian hq", f" {name}"])
    print("  Written: sector_blocks.csv")

    # arena_blocks.csv
    arena_to_sector = {}
    for room in ROOMS:
        arena_to_sector[room["arena"]] = room["sector"]

    with open(os.path.join(blocks_dir, "arena_blocks.csv"), "w", newline="") as f:
        writer = csv.writer(f)
        for aid, aname in ARENA_IDS.items():
            sid = arena_to_sector.get(aid, "40101")
            sname = SECTOR_IDS.get(sid, "Command Center")
            writer.writerow([aid, " travian hq", f" {sname}", f" {aname}"])
    print("  Written: arena_blocks.csv")

    # game_object_blocks.csv
    with open(os.path.join(blocks_dir, "game_object_blocks.csv"), "w", newline="") as f:
        writer = csv.writer(f)
        for gid, gname in GAME_OBJECT_IDS.items():
            writer.writerow([gid, " travian hq", " <all>", f" {gname}"])
    print("  Written: game_object_blocks.csv")

    # spawning_location_blocks.csv
    spawn_to_room = {}
    for room in ROOMS:
        if room["spawn"] and room["spawn"][2]:
            spawn_to_room[room["spawn"][2]] = room

    with open(os.path.join(blocks_dir, "spawning_location_blocks.csv"), "w", newline="") as f:
        writer = csv.writer(f)
        for spid, spname in SPAWN_IDS.items():
            room = spawn_to_room.get(spid)
            if room:
                sname = SECTOR_IDS.get(room["sector"], "")
                aname = ARENA_IDS.get(room["arena"], "")
                writer.writerow([spid, " travian hq", f" {sname}", f" {aname}", f" {spname}"])
    print("  Written: spawning_location_blocks.csv")


def generate_metadata(base_path):
    """Generate maze_meta_info.json."""
    meta = {
        "world_name": "travian hq",
        "maze_width": WIDTH,
        "maze_height": HEIGHT,
        "sq_tile_size": TILE_SIZE,
        "special_constraint": "",
    }
    meta_path = os.path.join(base_path, "matrix", "maze_meta_info.json")
    os.makedirs(os.path.dirname(meta_path), exist_ok=True)
    with open(meta_path, "w") as f:
        json.dump(meta, f, indent=1)
    print(f"  Written: maze_meta_info.json")


def generate_tiled_json(base_path):
    """Generate a minimal Phaser-compatible Tiled JSON map.

    Uses a programmatically-created tileset with colored tiles for different
    room types. This is a functional placeholder -- it can be replaced with
    a proper Tiled map later.
    """
    visuals_dir = os.path.join(base_path, "visuals")
    os.makedirs(visuals_dir, exist_ok=True)

    # Tile IDs for the visual map (using a simple embedded tileset)
    # 0 = empty, 1 = wall, 2-6 = sector colors, 7 = corridor, 8 = door
    TILE_WALL = 1
    TILE_CORRIDOR = 7
    TILE_DOOR = 8

    sector_tiles = {
        "40101": 2,  # Command Center - red
        "40102": 3,  # Economic Wing - gold
        "40103": 4,  # Intelligence Wing - blue
        "40104": 5,  # Operations Wing - green
        "40105": 6,  # Commons - brown
    }

    # Build the visual tile data (single layer for simplicity)
    floor_data = []
    wall_data = []
    for row in range(HEIGHT):
        for col in range(WIDTH):
            # Check if this is a wall (outer boundary)
            is_outer_wall = (row == 0 or row == HEIGHT - 1 or
                             col == 0 or col == WIDTH - 1)

            # Check if inside a room
            in_room = False
            room_sector = None
            is_room_wall = False
            for room in ROOMS:
                r1, r2 = room["rows"]
                c1, c2 = room["cols"]
                if r1 <= row <= r2 and c1 <= col <= c2:
                    room_sector = room["sector"]
                    if row == r1 or row == r2 or col == c1 or col == c2:
                        # Check if this is a door
                        door_col = (c1 + c2) // 2
                        if row == r1 and col in (door_col, door_col + 1):
                            is_room_wall = False  # door
                        else:
                            is_room_wall = True
                    else:
                        in_room = True
                    break

            if is_outer_wall or is_room_wall:
                floor_data.append(0)
                wall_data.append(TILE_WALL)
            elif in_room and room_sector:
                floor_data.append(sector_tiles.get(room_sector, TILE_CORRIDOR))
                wall_data.append(0)
            else:
                floor_data.append(TILE_CORRIDOR)
                wall_data.append(0)

    # Create a simple tileset with colored tiles (8x1 tileset image)
    tileset = {
        "columns": 8,
        "firstgid": 1,
        "image": "../the_ville/visuals/map_assets/Room_Builder_32x32.png",
        "imageheight": 1024,
        "imagewidth": 512,
        "margin": 0,
        "name": "travian_hq_tiles",
        "spacing": 0,
        "tilecount": 512,
        "tileheight": TILE_SIZE,
        "tilewidth": TILE_SIZE,
    }

    # Also include the blocks tileset for collision
    blocks_tileset = {
        "columns": 1,
        "firstgid": 32125,
        "image": "../the_ville/visuals/map_assets/blocks/blocks_1.png",
        "imageheight": 32,
        "imagewidth": 32,
        "margin": 0,
        "name": "blocks",
        "spacing": 0,
        "tilecount": 1,
        "tileheight": TILE_SIZE,
        "tilewidth": TILE_SIZE,
    }

    tiled_map = {
        "compressionlevel": -1,
        "height": HEIGHT,
        "infinite": False,
        "layers": [
            {
                "data": floor_data,
                "height": HEIGHT,
                "id": 1,
                "name": "Bottom Ground",
                "opacity": 1,
                "type": "tilelayer",
                "visible": True,
                "width": WIDTH,
                "x": 0,
                "y": 0,
            },
            {
                "data": wall_data,
                "height": HEIGHT,
                "id": 2,
                "name": "Building",
                "opacity": 1,
                "type": "tilelayer",
                "visible": True,
                "width": WIDTH,
                "x": 0,
                "y": 0,
            },
        ],
        "nextlayerid": 3,
        "nextobjectid": 1,
        "orientation": "orthogonal",
        "renderorder": "right-down",
        "tiledversion": "1.9.2",
        "tileheight": TILE_SIZE,
        "tilesets": [tileset, blocks_tileset],
        "tilewidth": TILE_SIZE,
        "type": "map",
        "version": "1.9",
        "width": WIDTH,
    }

    map_path = os.path.join(visuals_dir, "travian_hq.json")
    with open(map_path, "w") as f:
        json.dump(tiled_map, f, indent=2)
    print(f"  Written: travian_hq.json (Phaser map)")


def get_spawn_coordinates():
    """Return dict of persona_name -> (x, y) spawn coordinates."""
    # Map spawn block IDs to persona names
    spawn_id_to_persona = {
        "40401": "Commander Marcus",
        "40402": "Archivist Petra",
        "40403": "Scout Varro",
        "40404": "Treasurer Lucius",
        "40405": "Builder Gaius",
        "40406": "Centurion Titus",
        "40407": "Strategist Livia",
        "40408": "Sentinel Felix",
        "40409": "Validator Quintus",
    }

    coords = {}
    for room in ROOMS:
        if room["spawn"] and room["spawn"][2]:
            rel_row, rel_col, spawn_id = room["spawn"]
            r1 = room["rows"][0]
            c1 = room["cols"][0]
            abs_col = c1 + rel_col  # x
            abs_row = r1 + rel_row  # y
            persona = spawn_id_to_persona.get(spawn_id)
            if persona:
                coords[persona] = {"maze": "travian_hq", "x": abs_col, "y": abs_row}
    return coords


def main():
    base_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "environment", "frontend_server", "static_dirs", "assets", "travian_hq",
    )

    print(f"Generating Travian HQ map at: {base_path}")
    print()

    print("1. Generating maze CSVs...")
    generate_maze_csvs(base_path)
    print()

    print("2. Generating special blocks...")
    generate_special_blocks(base_path)
    print()

    print("3. Generating metadata...")
    generate_metadata(base_path)
    print()

    print("4. Generating Tiled JSON for Phaser...")
    generate_tiled_json(base_path)
    print()

    print("5. Spawn coordinates for environment/0.json:")
    coords = get_spawn_coordinates()
    for name, pos in sorted(coords.items()):
        print(f"  {name}: ({pos['x']}, {pos['y']})")
    print()

    print("Done! Map files generated successfully.")
    return coords


if __name__ == "__main__":
    main()
