import os
import uuid
from pathlib import Path
from typing import Tuple

MAX_FILE_SIZE = 5_242_880
ALLOWED_MIME_TYPES = {"image/png", "image/jpeg"}

PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
JPEG_SIGNATURE_START = b"\xff\xd8"
JPEG_SIGNATURE_END = b"\xff\xd9"


class FileUploadError(Exception):
    pass


class FileTooLargeError(FileUploadError):
    pass


class InvalidFileTypeError(FileUploadError):
    pass


class PathTraversalError(FileUploadError):
    pass


class SymlinkError(FileUploadError):
    pass


def validate_file_signature(data: bytes) -> str:
    if len(data) >= 8 and data.startswith(PNG_SIGNATURE):
        return "image/png"

    if (
        len(data) >= 2
        and data.startswith(JPEG_SIGNATURE_START)
        and data.endswith(JPEG_SIGNATURE_END)
    ):
        return "image/jpeg"

    raise InvalidFileTypeError(
        "File type not allowed. Only PNG and JPEG are supported."
    )


def check_symlinks(path: Path) -> None:
    for parent in path.parents:
        if parent.is_symlink():
            raise SymlinkError(f"Symlink detected in path: {parent}")

    if path.exists() and path.is_symlink():
        raise SymlinkError(f"Target path is a symlink: {path}")


def is_path_traversal(base_path: Path, target_path: Path) -> bool:
    try:
        base_absolute = base_path.resolve().absolute()
        target_absolute = target_path.resolve().absolute()

        return not str(target_absolute).startswith(str(base_absolute))
    except Exception:
        return True


def is_dangerous_filename(filename: str) -> bool:
    dangerous_patterns = [
        "..",  # Path traversal
        "~",  # Home directory reference
        "//",  # Network paths
        "\\",  # Windows path separators in wrong context
        "%2e%2e",  # URL encoded path traversal
    ]

    return any(pattern in filename for pattern in dangerous_patterns)


def secure_file_save(
    base_dir: str, original_filename: str, file_data: bytes
) -> Tuple[bool, str]:
    try:
        if len(file_data) > MAX_FILE_SIZE:
            raise FileTooLargeError(
                f"File exceeds maximum size of {MAX_FILE_SIZE} bytes"
            )

        if is_dangerous_filename(original_filename):
            raise PathTraversalError("Filename contains dangerous patterns")

        mime_type = validate_file_signature(file_data)

        base_path = Path(base_dir).resolve(strict=True)

        if not base_path.exists():
            raise FileUploadError(f"Base directory does not exist: {base_dir}")
        if not base_path.is_dir():
            raise FileUploadError(f"Base path is not a directory: {base_dir}")

        file_extension = ".png" if mime_type == "image/png" else ".jpg"
        safe_filename = f"{uuid.uuid4()}{file_extension}"
        full_path = (base_path / safe_filename).resolve()

        if is_path_traversal(base_path, full_path):
            raise PathTraversalError("Path traversal attempt detected")

        check_symlinks(full_path)

        full_path.parent.mkdir(parents=True, exist_ok=True)

        with open(full_path, "wb") as f:
            f.write(file_data)

        return True, str(full_path)

    except FileUploadError as e:
        return False, str(e)
    except Exception as e:
        print(f"Unexpected error during file upload: {e}")
        return False, "File upload failed due to server error"


def validate_upload_directory(base_dir: str) -> bool:
    try:
        base_path = Path(base_dir).resolve(strict=True)

        if not base_path.is_dir():
            return False

        if not os.access(base_path, os.W_OK):
            return False

        check_symlinks(base_path)

        return True

    except Exception:
        return False
