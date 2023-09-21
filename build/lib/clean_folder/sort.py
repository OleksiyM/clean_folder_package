import shutil
from pathlib import Path
import sys
import os

transliteration_dict = {
    "а": "a",
    "б": "b",
    "в": "v",
    "г": "g",
    "д": "d",
    "е": "e",
    "ё": "yo",
    "ж": "zh",
    "з": "z",
    "и": "i",
    "й": "y",
    "к": "k",
    "л": "l",
    "м": "m",
    "н": "n",
    "о": "o",
    "п": "p",
    "р": "r",
    "с": "s",
    "т": "t",
    "у": "u",
    "ф": "f",
    "х": "kh",
    "ц": "ts",
    "ч": "ch",
    "ш": "sh",
    "щ": "shch",
    "ъ": "",
    "ы": "y",
    "ь": "",
    "э": "e",
    "ю": "yu",
    "я": "ya",

    # Ukrainian characters
    "є": "ye",
    "і": "i",
    "ї": "yi",
    "ґ": "g",

    # Uppercase Cyrillic letters
    "А": "A",
    "Б": "B",
    "В": "V",
    "Г": "G",
    "Д": "D",
    "Е": "E",
    "Ё": "Yo",
    "Ж": "Zh",
    "З": "Z",
    "И": "I",
    "Й": "Y",
    "К": "K",
    "Л": "L",
    "М": "M",
    "Н": "N",
    "О": "O",
    "П": "P",
    "Р": "R",
    "С": "S",
    "Т": "T",
    "У": "U",
    "Ф": "F",
    "Х": "Kh",
    "Ц": "Ts",
    "Ч": "Ch",
    "Ш": "Sh",
    "Щ": "Shch",
    "Ъ": "",
    "Ы": "Y",
    "Ь": "",
    "Э": "E",
    "Ю": "Yu",
    "Я": "Ya",

    # Uppercase Ukrainian characters
    "Є": "YE",
    "І": "I",
    "Ї": "YI",
    "Ґ": "G"

}
CATEGORIES = {"images": [".jpeg", ".png", ".jpg", ".svg", ".gif"],
              "video": [".avi", ".mp4", ".mov", ".mkv", ".wmv"],
              "documents": [".doc", ".docx", ".txt", ".pdf", ".xlsx", ".xls", ".pptx", ".ppt", ".csv", ".odt", ".ods"],
              "audio": [".mp3", ".ogg", ".wav", ".amr"],
              "archives": [".zip", ".gz", ".tar"]}

log = []
known_extensions = set()
unknown_extensions = set()


def normalize(filename: str) -> str:
    # Split into filename and extension
    file_ext = ""
    extension_start_index = filename.rfind(".")
    if extension_start_index != -1:
        file_ext = filename[extension_start_index:]
        filename = filename[:extension_start_index]

        # print(f"normilize debug: filename {filename}, ext {file_ext}")

    normalized_filename = ""

    # Transliterate Cyrillic characters
    for character in filename:
        if character in transliteration_dict:
            normalized_filename += transliteration_dict[character]
            # print(character, "->", transliteration_dict[character])
        else:
            if character.isalnum():
                # Keep alphanumeric characters
                normalized_filename += character
                # print(character, "=")
            else:
                # Pass through non-alphanumeric characters unchanged
                normalized_filename += "_"
                # print(character, "->", "_")
    # Return the normalized filename with extension
    return normalized_filename + file_ext


def get_category_name(file: Path) -> str:
    """
    Determine category name based on file extension.

    Parameters:
        file (Path): Path object for file

    Returns:
        str: Category name if extension matches, 'other' otherwise
    """

    ext = file.suffix.lower()
    for category, exts in CATEGORIES.items():
        if ext in exts:
            return category
    return "other"


def move_file(file: Path, category: str, root_dir: Path) -> None:
    """
    Move a file to a category folder within the given root directory.
        Parameters:
            file (Path): The file to move
            category (str): The category folder name 
            root_dir (Path): The parent directory to move the file into

        Returns:
            None
    """
    target_dir = root_dir.joinpath(category)
    if not target_dir.exists():
        target_dir.mkdir()
        log.append(f"DIR: {target_dir} was created\n")
    # TODO check exist - count existing files, add increment to the file name
    new_path = target_dir.joinpath(normalize(file.name))
    if file.stem != new_path.stem:
        log.append(f"NORMALIZE: File renamed {file.name} -> {new_path.name}\n")

    if not new_path.exists():
        file.replace(new_path)
        log.append(f"SORT: File moved {file} -> {new_path}\n")
    else:
        file.replace(new_path)
        # log.append(f"SORT: Duplicate File moved {file} -> {new_path}\n")

    return


def sort_folder(path: Path) -> None:
    """
    Sorts the files in a given folder into different categories based on their file extensions.

    Args:
        path (Path): The path of the folder to be sorted.

    Returns:
        None
    """

    log.append(f"LOG: started sorting folder {path}\n")
    for element in path.glob("**/*"):

        if element.is_file():
            #print(element, "\n")
            category = get_category_name(element)
            if category != "other":
                known_extensions.add(element.suffix)
            else:
                unknown_extensions.add(element.suffix)
            # if category == "archives":
            #    unpack_archive(element, category, path)
            # else:
            # print(element, category, path)
            move_file(element, category, path)
    return


def unpack_archive(file: Path, category: str, root_dir: Path) -> None:
    """
    Unpacks an archive file.

    Args:
        file (Path): The path of the archive file to be unpacked.
        category (str): The category the archive file belongs to.
        root_dir (Path): The root directory where the archive file is located.

    Returns:
        None
    """
    path_to_unpack = root_dir.joinpath(category).joinpath(normalize(file.stem))
    new_path = root_dir.joinpath(category).joinpath(normalize(file.name))
    try:
        shutil.unpack_archive(file, path_to_unpack)
        file.replace(new_path)
        # os.remove(file)
        log.append(f"SORT: Archive unpacked {file} -> {path_to_unpack}\n")
    except:

        log.append(f"SORT: Error unpacking Archive {file}\n")
    return


def unpack_archives(root_dir: Path) -> None:
    category = "archives"
    path = root_dir.joinpath(category)
    for element in path.glob("**/*"):
        if element.is_file():
            path_to_unpack = path.joinpath(normalize(element.stem))
            try:
                shutil.unpack_archive(element, path_to_unpack)
                log.append(
                    f"SORT: Archive unpacked {element} -> {path_to_unpack}\n")
            except:
                log.append(f"SORT: Error unpacking Archive {element}\n")

    return


def delete_empty_folders(root_dir) -> None:
    """
    Delete any empty subfolders within the given root directory.

    Parameters:
        root_dir (Path): The parent directory to check for empty folders

    Returns:
        None

    Uses os.walk() to traverse root_dir recursively. Checks each 
    subfolder if empty using os.listdir(). Deletes empty folders with 
    os.rmdir(). Logs any deletions.
    """
    for dirpath, dirnames, filenames in os.walk(root_dir, topdown=False):
        for dirname in dirnames:
            full_path = os.path.join(dirpath, dirname)
            if not os.listdir(full_path):
                os.rmdir(full_path)
                log.append(f"DIR: Empty Directory {full_path} was removed\n")
    return


def count_files_in_folders(root_dir: Path) -> None:
    """
    Count total files in each category folder under the given root directory.

    Parameters:
        root_dir (Path): The parent directory containing category folders

    Returns:
        None

    Logs the total file count per category folder to the global log.
    Also logs known and unknown file extensions encountered.
    """
    all_categories = []
    for el in CATEGORIES.items():
        all_categories.append(el[0])
    all_categories.append("other")
    log.append(
        "------------------------- Sorting results -------------------------")
    log.append("\nKnown extensions: " + ", ".join(known_extensions))
    log.append("\nUnknown extensions: " + ", ".join(unknown_extensions))

    for el in all_categories:
        category = el

        path_dir = root_dir.joinpath(category)
        files_count = sum(1 for element in path_dir.glob(
            '**/*') if element.is_file())

        log.append(f"\nFiles in the {category}: {files_count}")
    return


def write_log_file(path: Path) -> bool:
    """
    Write the log list to a log file at the given path.

    Parameters:
        path (Path): Path to directory to write log file in

    Returns:
        bool: True if write succeeded, False otherwise

    Opens a log file named 'log.txt' in the given path. 
    Writes each log message in the global log list to the file.
    Returns True if writing succeeded, False if any errors occur.
    """
    log_file = path.joinpath("log.txt")
    print(f"Sorting Done. Log file saved in {log_file}")
    # Open log file and write logs
    with open(log_file, "w") as fh:
        for l in log:
            try:
                fh.write(l)
            except:
                print("ERROR writing to the log file:")
                print(l)
                return False
    return True


def main():
    """
    Main entry point for the sort script.

    Handles command line arguments, validates input folder, 
    calls sorting functions, deletes empty folders, and writes log file.

    Returns exit code based on success or failure:
        0: Success
        1: No folder specified
        2: Specified folder does not exist
        3: Specified path is not a folder

    """

    if len(sys.argv) < 2:
        print("Mandatory parameter was not specified")
        print("Usage sort.py <Directory>")
        print("Error Code: 1")
        return 1

    path = Path(sys.argv[1])

    if not path.exists():
        print(f"Specified folder {path} does not exist\nError Code: 2")
        return 2

    if not path.is_dir():
        print(
            f"Parameter: {path} is not a irectory (probably file)\nError Code: 3")
        return 3

    sort_folder(path)

    unpack_archives(path)

    delete_empty_folders(path)

    count_files_in_folders(path)

    write_log_file(path)

    return 0


if __name__ == '__main__':
    main()
