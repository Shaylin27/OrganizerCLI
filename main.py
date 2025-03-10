import json
from pathlib import Path
import shutil
import argparse
import sys

parser = argparse.ArgumentParser(description="Process user flags.")
parser.add_argument("-f", "--folder", action="store_true", help="Show the folder creations")
parser.add_argument("--copy", action="store_true", help="Copy instead of moving")
#parser.add_argument("-c", "--confirm", action="store_true", help="Require confirmation before proceeding")
parser.add_argument("-o", "--other-files", action="store_true", help="Include other files in copy/move")
parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose output")
parser.add_argument("-vs", "--verbose-small", action="store_true", help="Enable smaller verbose output")
parser.add_argument("--verify-options", action="store_true", help="Verify the options.json")

args = parser.parse_args()
print(args)

#region JSON validation code
def validate_json(json_data):
    if not isinstance(json_data, dict):
        return False, "JSON must be a dictionary."

    for categoryJSON, extensions in json_data.items():
        if not isinstance(categoryJSON, str):
            return False, f"Invalid key: {categoryJSON}. Keys must be strings."

        if not isinstance(extensions, list):
            return False, f"Invalid value for '{categoryJSON}'. Expected a list."

        if not all(isinstance(ext, str) for ext in extensions):
            return False, f"Invalid extensions in '{categoryJSON}'. List must contain only strings."

    return True, "JSON structure is valid."
#endregion

if args.verify_options:
    with open("options.json", "r") as file:
        is_valid, output = validate_json(json.load(file))
        if not is_valid:
            print(output)
            sys.exit(1)

#region Loading the JSON with error handling and creating the folders
input_path = Path(input("Please input the path to organise:"))

try:
    with open("options.json", "r") as file:
        options = json.load(file)
except FileNotFoundError:
    print("Error: The file 'options.json' was not found.")
    sys.exit(1)
except json.JSONDecodeError as e:
    print(f"Error: Invalid JSON format in 'options.json' - {e}")
    sys.exit(1)
except PermissionError:
    print("Error: Permission denied when trying to read 'options.json'.")
    sys.exit(1)
except Exception as e:
    print(f"Unexpected error: {e}")
    sys.exit(1)

# Validate JSON structure
is_valid, message = validate_json(options)
if not is_valid:
    print(message)
    sys.exit(1)

for folder_category, _ in options.items():
    (input_path / folder_category).mkdir(exist_ok=True)

other_files_folder_name = ""
if args.other_files:
    other_files_folder_name = input('Input the name of the "Other files" folder (Other is default)').strip()
    if not other_files_folder_name:
        print("Error: Folder name cannot be empty.")
        sys.exit()
    else:
        try:
            (input_path / other_files_folder_name).mkdir(exist_ok=True)
            print(f"Folder created at: {(input_path / other_files_folder_name).resolve()}")
        except Exception as e:
            print(f"Error creating folder: {e}")
            sys.exit()
#endregion

files = [f for f in input_path.iterdir() if f.is_file()]

for file in files:
    extension = file.suffix.lower()[1:]
    found_category = False

    for category in options:
        if extension in options[category]:
            found_category = True
            # region Copy/Move known files
            if args.copy:
                if args.verbose:
                    print(f'Copying "{str(file)}" to "{str(input_path / category / file.name)}"')
                elif args.verbose_small:
                    print(f'Copying "{file.name}"')
                shutil.copy(str(file), str(input_path / category / file.name))
            else:
                if args.verbose:
                    print(f'Moving "{str(file)}" to "{str(input_path / category / file.name)}"')
                elif args.verbose_small:
                    print(f'Moving "{file.name}"')
                shutil.move(str(file), str(input_path / category / file.name))
            # endregion
            break

    if not found_category and args.other_files:
        # region Copy/Move unknown files
        if args.copy:
            if args.verbose:
                print(f'Copying "{str(file)}" to "{str(input_path / other_files_folder_name / file.name)}"')
            elif args.verbose_small:
                print(f'Copying "{file.name}"')
            shutil.copy(str(file), str(input_path / other_files_folder_name / file.name))
        else:
            if args.verbose:
                print(f'Moving "{str(file)}" to "{str(input_path / other_files_folder_name / file.name)}"')
            elif args.verbose_small:
                print(f'Moving "{file.name}"')
            shutil.move(str(file), str(input_path / other_files_folder_name / file.name))
        # endregion