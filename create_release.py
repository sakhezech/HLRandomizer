from json_generators import generate_all_jsons
from datetime import datetime
import shutil
import os


def main():
    generate_all_jsons()
    release_folder = "out"
    shutil.rmtree(release_folder, ignore_errors=True)
    shutil.copytree("hldlib", os.path.join(release_folder, "hldlib"), dirs_exist_ok=True)
    shutil.copytree("jsons", os.path.join(release_folder, "jsons"), dirs_exist_ok=True)
    shutil.rmtree(os.path.join(release_folder, "hldlib", "__pycache__"))
    shutil.copy("randomizer.py", release_folder)
    shutil.copy("console.py", release_folder)
    shutil.make_archive(f"hlr-release{datetime.now().strftime('-%Y-%m-%d-%H-%M-%S')}", 'zip', release_folder)


if __name__ == "__main__":
    main()
    input("Done!")
