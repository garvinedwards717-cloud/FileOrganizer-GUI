from pathlib import Path
import shutil
from datetime import datetime
import json
import sys


def get_base_path() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys._MEIPASS)
    return Path(__file__).resolve().parents[1]


def load_rules() -> dict:
    base_path = get_base_path()
    rules_file = base_path / "config" / "file_rules.json"

    with open(rules_file, "r", encoding="utf-8") as file:
        return json.load(file)


FILE_CATEGORIES = load_rules()


def get_category(file_path: Path) -> str:
    extension = file_path.suffix.lower()

    for category, extensions in FILE_CATEGORIES.items():
        if extension in extensions:
            return category

    return "Others"


def get_project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def get_unique_destination(destination: Path) -> Path:
    if not destination.exists():
        return destination

    stem = destination.stem
    suffix = destination.suffix
    parent = destination.parent
    counter = 1

    while True:
        new_destination = parent / f"{stem}_{counter}{suffix}"
        if not new_destination.exists():
            return new_destination
        counter += 1


def preview_organization(folder_path: str) -> list[tuple[str, str]]:
    source_folder = Path(folder_path)

    if not source_folder.exists() or not source_folder.is_dir():
        raise ValueError("Selected folder does not exist or is not a valid directory.")

    preview_results: list[tuple[str, str]] = []

    for item in source_folder.iterdir():
        if item.is_file():
            category = get_category(item)
            preview_results.append((item.name, category))

    return preview_results


def write_log(folder_path: str, moved_files: int, renamed_files: int) -> None:
    project_root = get_project_root()
    logs_dir = project_root / "logs"
    logs_dir.mkdir(exist_ok=True)

    log_file = logs_dir / "activity.log"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with log_file.open("a", encoding="utf-8") as file:
        file.write(
            f"[{timestamp}] Folder: {folder_path} | "
            f"Moved: {moved_files} | Renamed: {renamed_files}\n"
        )


def save_undo_data(moves: list[dict]) -> None:
    project_root = get_project_root()
    logs_dir = project_root / "logs"
    logs_dir.mkdir(exist_ok=True)

    undo_file = logs_dir / "last_operation.json"

    with undo_file.open("w", encoding="utf-8") as file:
        json.dump(moves, file, indent=4)


def load_undo_data() -> list[dict]:
    project_root = get_project_root()
    undo_file = project_root / "logs" / "last_operation.json"

    if not undo_file.exists():
        return []

    with undo_file.open("r", encoding="utf-8") as file:
        return json.load(file)


def organize_folder(folder_path: str) -> tuple[int, int]:
    source_folder = Path(folder_path)

    if not source_folder.exists() or not source_folder.is_dir():
        raise ValueError("Selected folder does not exist or is not a valid directory.")

    moved_files = 0
    renamed_files = 0
    moves: list[dict] = []

    for item in source_folder.iterdir():
        if item.is_file():
            original_path = item.resolve()
            category = get_category(item)
            category_folder = source_folder / category
            category_folder.mkdir(exist_ok=True)

            destination = category_folder / item.name
            final_destination = get_unique_destination(destination)

            if final_destination != destination:
                renamed_files += 1

            shutil.move(str(item), str(final_destination))
            moved_files += 1

            moves.append(
                {
                    "from": str(final_destination.resolve()),
                    "to": str(original_path)
                }
            )

    save_undo_data(moves)
    write_log(folder_path, moved_files, renamed_files)
    return moved_files, renamed_files


def undo_last_operation() -> int:
    moves = load_undo_data()

    if not moves:
        raise ValueError("No previous operation found to undo.")

    restored_files = 0

    for move in reversed(moves):
        current_path = Path(move["from"])
        original_path = Path(move["to"])

        if current_path.exists():
            original_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(current_path), str(original_path))
            restored_files += 1

    save_undo_data([])
    return restored_files


def organize_new_file(file_path: str) -> str:
    item = Path(file_path)

    if not item.exists() or not item.is_file():
        return "Skipped: file does not exist."

    source_folder = item.parent
    category = get_category(item)
    category_folder = source_folder / category
    category_folder.mkdir(exist_ok=True)

    destination = category_folder / item.name
    final_destination = get_unique_destination(destination)

    shutil.move(str(item), str(final_destination))
    return f"Auto-organized: {item.name} -> {category}"