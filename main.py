#region Imports
import json
from pathlib import Path
import shutil
import argparse
import sys
import tempfile
import atexit
import logging
#endregion

#region Command Line Arguments
parser = argparse.ArgumentParser(description="Process user flags.")
parser.add_argument("-f", "--folder", action="store_true", help="Show the folder creations")
parser.add_argument("--copy", action="store_true", help="Copy instead of moving")
#parser.add_argument("-c", "--confirm", action="store_true", help="Require confirmation before proceeding")
parser.add_argument("-o", "--other-files", action="store_true", help="Include other files in copy/move")
parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose output")
parser.add_argument("-vs", "--verbose-small", action="store_true", help="Enable smaller verbose output")
parser.add_argument("--verify-options", action="store_true", help="Verify the options.json")
parser.add_argument("--log", action="store_true", help="Enable logging to a file")

args = parser.parse_args()
print(args)

#endregion

#region JSON validation code
def validate_json(json_data):
    if not isinstance(json_data, dict):
        return False, "JSON must be a dictionary."

    for categoryJSON, json_extensions in json_data.items():
        if not isinstance(categoryJSON, str):
            return False, f"Invalid key: {categoryJSON}. Keys must be strings."

        if not isinstance(json_extensions, list):
            return False, f"Invalid value for '{categoryJSON}'. Expected a list."

        if not all(isinstance(ext, str) for ext in json_extensions):
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
#endregion

#region Validate JSON structure
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

#region Logging code
if args.log:
    temp_log_file = Path(tempfile.gettempdir()) / "organizer.log"

    logging.basicConfig(
        filename=temp_log_file,
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )

    def move_log_back():
        """Moves the log file back to the working directory after execution."""
        final_log_path = Path.cwd() / "organizer.log"
        shutil.move(temp_log_file, final_log_path)

    # Register function to run at exit
    atexit.register(move_log_back)
#endregion

files = [f for f in input_path.iterdir() if f.is_file()]

#region Process Files function
def process_file(origin_file, destination, action, verbose, verbose_small):
    # Currently this will always prioritise verbose over small_verbose, but I might need to edit that
    action_text = "Copying" if action == "copy" else "Moving"
    if verbose:
        print(f'{action_text} "{str(origin_file)}" to "{str(destination)}"')
    elif verbose_small:
        print(f'{action_text} "{origin_file.name}"')

    try:
        if action == "copy":
            shutil.copy(str(origin_file), str(destination))
        else:
            shutil.move(str(origin_file), str(destination))

        if args.log:
            logging.info(f'{action_text} "{origin_file}" -> "{destination}"')
    except Exception as logging_error:
        if args.log:
            logging.error(f'Failed to {action_text.lower()} "{origin_file}" -> "{destination}": {logging_error}')
#endregion

#region File copying/moving
for file in files:
    extension = file.suffix.lower()[1:]
    found_category = False

    for category, extensions in options.items():
        if extension in extensions:
            found_category = True
            process_file(file, input_path / category / file.name,
                         "copy" if args.copy else "move",
                         args.verbose, args.verbose_small)
            break

    if not found_category and args.other_files:
        process_file(file, input_path / other_files_folder_name / file.name,
                     "copy" if args.copy else "move",
                     args.verbose, args.verbose_small)
# endregion