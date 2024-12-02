import json
from pathlib import Path
import shutil
from icecream import ic

selected_path = Path.home() / "Downloads"

options = json.load(open('options.json', 'r'))

for folder_category, _ in options.items():
    (selected_path / folder_category).mkdir(exist_ok=True)

files = [f for f in selected_path.iterdir() if f.is_file()]

for file in files:
    extensions = file.suffix.lower()[1:]
    for category in options:
        if extensions in options[category]:
            shutil.move(str(file), str(selected_path / category / file.name))
            # TODO: Remove this for release version
            ic(str(file))
            ic(str(selected_path / category / file.name))
