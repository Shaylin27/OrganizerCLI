import json
from pathlib import Path
import shutil
import argparse


parser = argparse.ArgumentParser(description="Process user flags.")

#TODO FIX THIS THING
parser.add_argument("--copy", action="store_true", help="Copy instead of moving")
#parser.add_argument("-c", "--confirm", action="store_true", help="Require confirmation before proceeding")
#TODO Modify the code to allow the processing of other files
#parser.add_argument("-o", "--other-files", action="store_true", help="Include other files in operation")
parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose output")
parser.add_argument("-vs", "--verbose-small", action="store_true", help="Enable smaller verbose output")

args = parser.parse_args()
print(args)

input_path = Path(input("Please input the path to organise:"))
#region Loading the JSON and creating the folders
options = json.load(open('options.json', 'r'))

for folder_category, _ in options.items():
    (input_path / folder_category).mkdir(exist_ok=True)
#endregion

files = [f for f in input_path.iterdir() if f.is_file()]

for file in files:
    extensions = file.suffix.lower()[1:]
    for category in options:
        if extensions in options[category]:
            if args.copy:
                if args.verbose:
                    print(f'Copying "{str(file)}" to "{str(input_path / category / file.name)}"')
                elif args.vebose_small:
                    print(f'Copying "{file.name}"')
                shutil.copy(str(file), str(input_path / category / file.name))
            else:
                if args.verbose:
                    print(f'Moving "{str(file)}" to "{str(input_path / category / file.name)}"')
                elif args.vebose_small:
                    print(f'Moving "{file.name}"')
                shutil.move(str(file), str(input_path / category / file.name))
