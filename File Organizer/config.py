import json
import os


CONFIG_FILE = "config.json"


DEFAULT_CATEGORIES = {
    "Images": [
        ".jpg",
        ".jpeg",
        ".png",
        ".gif",
        ".bmp",
        ".webp",
        ".svg"
    ],
    "Documents": [
        ".pdf",
        ".doc",
        ".docx",
        ".txt",
        ".xlsx",
        ".xls",
        ".ppt",
        ".pptx",
        ".csv"
    ],
    "Videos": [
        ".mp4",
        ".avi",
        ".mkv",
        ".mov",
        ".wmv",
        ".webm"
    ],
    "Audio": [
        ".mp3",
        ".wav",
        ".flac",
        ".aac",
        ".ogg",
        ".m4a"
    ],
    "Archives": [
        ".zip",
        ".rar",
        ".7z",
        ".tar",
        ".gz"
    ],
    "Others": []
}


def load_config():
    """Load categories from the JSON configuration file."""

    if not os.path.exists(CONFIG_FILE):
        save_config(DEFAULT_CATEGORIES)
        return DEFAULT_CATEGORIES.copy()

    try:
        with open(
            CONFIG_FILE,
            "r",
            encoding="utf-8"
        ) as file:
            data = json.load(file)

        if not isinstance(data, dict):
            raise ValueError

        return data

    except (
        OSError,
        json.JSONDecodeError,
        ValueError
    ):
        save_config(DEFAULT_CATEGORIES)
        return DEFAULT_CATEGORIES.copy()


def save_config(categories):
    """Save categories to the JSON configuration file."""

    with open(
        CONFIG_FILE,
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(
            categories,
            file,
            indent=4
        )


def get_category_for_extension(extension, categories):
    """Return the category matching a file extension."""

    extension = extension.lower()

    for category, extensions in categories.items():

        if extension in [
            item.lower()
            for item in extensions
        ]:
            return category

    return "Others"