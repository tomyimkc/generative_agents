"""
Author: Joon Sung Park (joonspk@stanford.edu)

File: compress_sim_storage.py
Description: Compresses a simulation for replay demos. 
"""
import shutil
import json
from global_methods import *

def compress(sim_code):
  sim_storage = f"../environment/frontend_server/storage/{sim_code}"
  compressed_storage = f"../environment/frontend_server/compressed_storage/{sim_code}"
  persona_folder = sim_storage + "/personas"
  move_folder = sim_storage + "/movement"
  meta_file = sim_storage + "/reverie/meta.json"

  persona_names = []
  for i in find_filenames(persona_folder, ""): 
    x = i.split("/")[-1].strip()
    if x[0] != ".": 
      persona_names += [x]

  max_move_count = max([int(i.split("/")[-1].split(".")[0]) 
                 for i in find_filenames(move_folder, "json")])
  
  persona_last_move = dict()
  master_move = dict()

  # Determine the actual persona keys used in movement files
  with open(f"{move_folder}/0.json") as json_file:
    movement_personas = list(json.load(json_file)["persona"].keys())

  # If there is a mismatch (e.g., 'Visual Manager' vs 'Klaus Mueller'),
  # fall back to movement keys to avoid KeyError.
  if set(persona_names) != set(movement_personas):
    print("WARNING: Persona names in folder do not match movement keys.")
    print(f"Folder personas: {persona_names}")
    print(f"Movement personas: {movement_personas}")
    persona_names = movement_personas

  for i in range(max_move_count+1): 
    master_move[i] = dict()
    with open(f"{move_folder}/{str(i)}.json") as json_file:  
      i_move_dict = json.load(json_file)["persona"]
      for p in persona_names: 
        if p not in i_move_dict:
          # Skip personas missing in this movement frame
          continue
        move = False
        if i == 0: 
          move = True
        elif (i_move_dict[p]["movement"] != persona_last_move[p]["movement"]
          or i_move_dict[p]["pronunciatio"] != persona_last_move[p]["pronunciatio"]
          or i_move_dict[p]["description"] != persona_last_move[p]["description"]
          or i_move_dict[p]["chat"] != persona_last_move[p]["chat"]): 
          move = True

        if move: 
          persona_last_move[p] = {"movement": i_move_dict[p]["movement"],
                                  "pronunciatio": i_move_dict[p]["pronunciatio"], 
                                  "description": i_move_dict[p]["description"], 
                                  "chat": i_move_dict[p]["chat"]}
          master_move[i][p] = {"movement": i_move_dict[p]["movement"],
                               "pronunciatio": i_move_dict[p]["pronunciatio"], 
                               "description": i_move_dict[p]["description"], 
                               "chat": i_move_dict[p]["chat"]}


  create_folder_if_not_there(compressed_storage)
  with open(f"{compressed_storage}/master_movement.json", "w") as outfile:
    outfile.write(json.dumps(master_move, indent=2))

  shutil.copyfile(meta_file, f"{compressed_storage}/meta.json")
  shutil.copytree(persona_folder, f"{compressed_storage}/personas/")


if __name__ == '__main__':
  import sys
  if len(sys.argv) > 1:
    compress(sys.argv[1])
  else:
    print('Usage: python3 compress_sim_storage.py <sim_code>')









  









