import json
from pathlib import Path
import shutil

path = Path.home() / "Downloads"

options = json.load(open('options.json', 'r'))

for i, _ in options.items():
    (path / i).mkdir(exist_ok=True)

files = [f for f in path.iterdir() if f.is_file()]

for file in files:
    ext = file.suffix.lower()[1:]
    for category in options:
        if ext in options[category]:
            # Leaving these debug statements here incase someone wants to under this better
            # print(f'{ext=}, {category=}')
            # print(f'{str(file)}')
            shutil.move(str(file), str(path / category / file.name))
