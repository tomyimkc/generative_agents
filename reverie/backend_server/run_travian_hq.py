#!/usr/bin/env python3
"""Quick launcher for the Travian HQ simulation.

Usage:
    python run_travian_hq.py                    # Interactive
    python run_travian_hq.py --steps 100        # Run 100 steps then save
    python run_travian_hq.py --name my_run_1    # Name the simulation
"""
import argparse
import os
import sys
import time

# Ensure we're using the travian_hq map
os.environ.setdefault("REVERIE_MAZE", "travian_hq")

from reverie import ReverieServer


def main():
    parser = argparse.ArgumentParser(description="Travian HQ Simulation Launcher")
    parser.add_argument("--base", default="base_travian_hq",
                        help="Base simulation to fork from (default: base_travian_hq)")
    parser.add_argument("--name", default=None,
                        help="Name for this simulation run (default: auto-generated)")
    parser.add_argument("--steps", type=int, default=0,
                        help="Run this many steps then save (0 = interactive mode)")
    args = parser.parse_args()

    sim_name = args.name or f"travian_hq_{int(time.time())}"

    print(f"Forking from: {args.base}")
    print(f"Simulation name: {sim_name}")
    print(f"Map: {os.environ.get('REVERIE_MAZE', 'travian_hq')}")
    print(f"Model: {os.environ.get('REVERIE_MODEL', 'qwen2.5:32b')}")
    print()

    rs = ReverieServer(args.base, sim_name)

    if args.steps > 0:
        print(f"Running {args.steps} steps...")
        rs.start_server(args.steps)
        rs.save()
        print(f"Saved simulation: {sim_name}")
    else:
        rs.open_server()


if __name__ == "__main__":
    main()
