import hashlib
import os


def format_size(size):
    """Convert bytes to a readable file size."""

    if size < 1024:
        return f"{size} B"

    if size < 1024 ** 2:
        return f"{size / 1024:.1f} KB"

    if size < 1024 ** 3:
        return f"{size / (1024 ** 2):.1f} MB"

    return f"{size / (1024 ** 3):.1f} GB"


def get_file_hash(file_path):
    """Return the SHA-256 hash of a file."""

    sha256 = hashlib.sha256()

    try:
        with open(file_path, "rb") as file:
            while True:
                chunk = file.read(1024 * 1024)

                if not chunk:
                    break

                sha256.update(chunk)

        return sha256.hexdigest()

    except (OSError, PermissionError):
        return None


def get_unique_destination(destination):
    """Return a unique path without overwriting an existing file."""

    if not os.path.exists(destination):
        return destination

    folder = os.path.dirname(destination)
    filename = os.path.basename(destination)

    name, extension = os.path.splitext(filename)

    counter = 1

    while True:
        new_filename = f"{name}_{counter}{extension}"
        new_destination = os.path.join(
            folder,
            new_filename
        )

        if not os.path.exists(new_destination):
            return new_destination

        counter += 1