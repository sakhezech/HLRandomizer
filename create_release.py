from json_generators import generate_all_jsons
from datetime import datetime
import PyInstaller.__main__


def main():
    generate_all_jsons()
    PyInstaller.__main__.run([
        "console.py", "-F", "--add-data", "jsons;jsons", "-n", f"hlr-release{datetime.now().strftime('-%Y-%m-%d-%H-%M-%S')}"
    ])

if __name__ == "__main__":
    main()
    input("Done!")
