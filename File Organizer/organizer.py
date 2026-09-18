import logging
import os
import shutil
from datetime import datetime

from config import get_category_for_extension
from utils import get_file_hash, get_unique_destination


logging.basicConfig(
    filename="organizer.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


def scan_folder(folder, categories):
    """Scan a folder and return information about its files."""

    files = []

    if not folder or not os.path.isdir(folder):
        return files

    try:
        entries = os.listdir(folder)

    except (OSError, PermissionError) as error:
        logging.error(
            "Could not read folder %s: %s",
            folder,
            error
        )
        return files

    for filename in entries:

        path = os.path.join(
            folder,
            filename
        )

        if not os.path.isfile(path):
            continue

        try:
            extension = os.path.splitext(
                filename
            )[1].lower()

            category = get_category_for_extension(
                extension,
                categories
            )

            size = os.path.getsize(
                path
            )

            modified = datetime.fromtimestamp(
                os.path.getmtime(path)
            )

            files.append({
                "name": filename,
                "path": path,
                "category": category,
                "size": size,
                "modified": modified
            })

        except (
            OSError,
            PermissionError
        ) as error:

            logging.error(
                "Could not read file %s: %s",
                path,
                error
            )

    return files


def find_duplicates(files):
    """
    Find duplicate files using SHA-256.

    The file with the shortest name in each duplicate group
    is considered the original and will be kept.
    """
    hashes = {}

    for file_data in files:
        path = file_data["path"]

        if not os.path.isfile(path):
            continue

        file_hash = get_file_hash(path)

        if file_hash is None:
            continue

        if file_hash not in hashes:
            hashes[file_hash] = []

        hashes[file_hash].append(file_data)

    duplicate_groups = []

    for file_hash, group in hashes.items():
        if len(group) <= 1:
            continue

        # The shortest filename is considered the original.
        # If two filenames have the same length,
        # alphabetical order is used as a secondary criterion.
        group.sort(
            key=lambda file_data: (
                len(file_data["name"]),
                file_data["name"].lower()
            )
        )

        duplicate_groups.append({
            "hash": file_hash,
            "files": group
        })

    return duplicate_groups



def organize_files(folder, files):
    """
    Move files into category folders.

    Returns a list of operations:
    (source, destination)
    """

    operations = []

    for file_data in files:

        source = file_data["path"]
        category = file_data["category"]

        if not os.path.isfile(source):
            continue

        destination_folder = os.path.join(
            folder,
            category
        )

        try:
            os.makedirs(
                destination_folder,
                exist_ok=True
            )

            destination = os.path.join(
                destination_folder,
                file_data["name"]
            )

            destination = get_unique_destination(
                destination
            )

            shutil.move(
                source,
                destination
            )

            operations.append(
                (
                    source,
                    destination
                )
            )

            logging.info(
                "Moved %s -> %s",
                source,
                destination
            )

        except (
            OSError,
            PermissionError
        ) as error:

            logging.error(
                "Could not move %s: %s",
                source,
                error
            )

    return operations


def undo_operations(operations):
    """Undo the latest organization operation."""

    successful = 0

    for source, destination in reversed(
        operations
    ):

        if not os.path.exists(destination):
            continue

        try:

            original_folder = os.path.dirname(
                source
            )

            os.makedirs(
                original_folder,
                exist_ok=True
            )

            restored_path = get_unique_destination(
                source
            )

            shutil.move(
                destination,
                restored_path
            )

            successful += 1

            logging.info(
                "Restored %s -> %s",
                destination,
                restored_path
            )

        except (
            OSError,
            PermissionError
        ) as error:

            logging.error(
                "Could not restore %s: %s",
                destination,
                error
            )

    return successful


def delete_files(file_paths):
    """Delete selected files."""

    deleted = 0

    for path in file_paths:

        if not os.path.isfile(path):
            continue

        try:

            os.remove(
                path
            )

            deleted += 1

            logging.info(
                "Deleted duplicate: %s",
                path
            )

        except (
            OSError,
            PermissionError
        ) as error:

            logging.error(
                "Could not delete %s: %s",
                path,
                error
            )

    return deleted

