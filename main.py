from pathlib import Path
import shutil

path = Path.home() / "Downloads"

types = ['Docs', 'Videos', 'Pictures', 'Others']

for folder in types:
    (path / folder).mkdir(exist_ok=True)

files = [f for f in path.iterdir() if f.is_file()]

for file in files:
    ext = file.suffix.lower()

    match ext:
        case '.pdf':
            shutil.move(str(file), str(path / 'Docs' / file.name))
        case '.mp4':
            shutil.move(str(file), str(path / 'Videos' / file.name))
        case '.jpg':
            shutil.move(str(file), str(path / 'Pictures' / file.name))
        case _:
            shutil.move(str(file), str(path / 'Others' / file.name))
