from cmd import Cmd
from time import time
from hldlib import HLDBasics, HLDLevel
from randomizer import main, OUTPUT_PATH, BACKUP_FOLDER_NAME, ITEMLESS_FOLDER_NAME, DOORLESS_FOLDER_NAME
import shutil
import os
import re


class ManagerCmd(Cmd):
    prompt = "> "
    intro = f"  _    _                       _      _       _     _   _____                 _                 _              \n" \
            f" | |  | |                     | |    (_)     | |   | | |  __ \               | |               (_)             \n" \
            f" | |__| |_   _ _ __   ___ _ __| |     _  __ _| |__ | |_| |__) |__ _ _ __   __| | ___  _ __ ___  _ _______ _ __ \n" \
            f" |  __  | | | | '_ \ / _ \ '__| |    | |/ _` | '_ \| __|  _  // _` | '_ \ / _` |/ _ \| '_ ` _ \| |_  / _ \ '__|\n" \
            f" | |  | | |_| | |_) |  __/ |  | |____| | (_| | | | | |_| | \ \ (_| | | | | (_| | (_) | | | | | | |/ /  __/ |   \n" \
            f" |_|  |_|\__, | .__/ \___|_|  |______|_|\__, |_| |_|\__|_|  \_\__,_|_| |_|\__,_|\___/|_| |_| |_|_/___\___|_|   \n" \
            f"          __/ | |                        __/ |                                                                 \n" \
            f"         |___/|_|                       |___/                                                                  \n" \
            f"\n" \
            f"Type 'help' for help"
    try:
        PATH_TO_HLD = HLDBasics.find_path()
    except ValueError as e:
        input("Create a file named 'hlddir.txt' and place HLD installation directory inside.")
        exit()

    def do_install(self, args):
        """
        Makes a backup of HLD levels and makes itemless and doorless copies of levels
        """

        ITEMS = [",ModuleSocket", ",LibrarianTablet", ",DrifterBones_Outfit", "=GearbitCrate", ",DrifterBones_Key",
                 ",DrifterBones_Weapon", "=Gearbit",
                 ",NoCombat", ",NoShoot", ",Upgrade", "spr_NPC_teddy_idleSup", "spr_NPC_Fatso",
                 "spr_NPC_akashecary_idleGrind", "spr_NPC_seanguin_idleThink", "spr_NPC_beau_idleTap"]
        DOORS = ["j,door,", "j,Televator", "j,Teleporter", ",h=128,cs=3,"]
        start_time = time()
        levels = HLDBasics.omega_load(self.PATH_TO_HLD)

        def _remove_and_dump(levels: list[HLDLevel], objects_to_exclude: list[str], output_folder: str):
            for level in levels:
                objs_to_remove = []
                for obj in level.object_list:
                    if any(item in obj.get_line() for item in objects_to_exclude):
                        objs_to_remove.append(obj)
                for obj in objs_to_remove:
                    level.object_list.remove(obj)
                level.dump_level(os.path.join(OUTPUT_PATH, output_folder, level.dir_))

        # REAL BACKUP
        for level_path, dir_, level_name in HLDBasics.get_levels(self.PATH_TO_HLD, HLDBasics.DIRS):
            os.makedirs(path_to_save := os.path.join(OUTPUT_PATH, BACKUP_FOLDER_NAME, dir_), exist_ok=True)
            shutil.copy(level_path, path_to_save)
        # FAKE BACKUP
        # _remove_and_dump(levels, ["DO NOT EXCLUDE ANYTHING"], BACKUP_FOLDER_NAME)
        _remove_and_dump(levels, ITEMS, ITEMLESS_FOLDER_NAME)
        _remove_and_dump(levels, DOORS, DOORLESS_FOLDER_NAME)

        end_time = time()
        print(f"Done in {end_time-start_time:.2f} s")

    def do_push(self, folder_to_push):
        """
        Pushes selected levels to HLD installation folder
        Usage example: push randomized
        ^ Pushes a folder named 'randomized' from 'game_files' to the HLD installation folder
        """
        if folder_to_push not in os.listdir(OUTPUT_PATH):
            print("No such folder.")
        else:
            start_time = time()
            shutil.copytree(os.path.join(OUTPUT_PATH, folder_to_push), self.PATH_TO_HLD, dirs_exist_ok=True)
            end_time = time()
            print(f"Done in {end_time-start_time:.2f} s")

    def do_del(self, folder_to_del):
        """
        Deletes a folder in 'game_files'
        Usage example: del randomized
        ^ Deletes a folder named 'randomized' from 'game_files'
        """
        if folder_to_del not in os.listdir(OUTPUT_PATH):
            print("No such folder.")
        else:
            start_time = time()
            shutil.rmtree(os.path.join(OUTPUT_PATH, folder_to_del))
            end_time = time()
            print(f"Done in {end_time-start_time:.2f} s")

    def do_gen(self, args):
        """
        Starts the randomized level files creation sequence
        Leave random seed empty if you don't wish to use a seed
        At the end creates a folder named 'randomized' in 'game_files'
        """

        def get_y_n(prompt: str):
            yes = ["y", "yes"]
            no = ["n", "no"]
            while True:
                input_ = input(prompt + " Y/N: ").lower()
                if input_ in yes:
                    return True
                elif input_ in no:
                    return False

        random_doors = get_y_n("Randomize doors?")
        random_enemies = get_y_n("Randomize enemies?")
        output = True  # get_y_n("Output?")
        random_seed = input("Random seed: ")
        output_folder_name = re.sub(r"[^\w_-]", "", input("Output folder name: ")) if output else ""

        start_time = time()

        try:
            main(
                random_doors=random_doors,
                random_enemies=random_enemies,
                output=output,
                output_folder_name=output_folder_name if output_folder_name else "out",
                random_seed=random_seed if random_seed else None
            )
        except IndexError as e:
            print(f"We've encountered an '{e}' error. Try again or try another seed if seed used.")

        end_time = time()
        print(f"Done in {end_time-start_time:.2f} s")

    def do_exit(self, args):
        """Closes the console"""
        exit()


if __name__ == "__main__":
    ManagerCmd().cmdloop()
