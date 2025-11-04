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


def validate_file_signature(data: bytes) -> str:
    if len(data) >= 8 and data.startswith(PNG_SIGNATURE):
        return "image/png"

    if (
        len(data) >= 2
        and data.startswith(JPEG_SIGNATURE_START)
        and data.endswith(JPEG_SIGNATURE_END)
    ):
        return "image/jpeg"

    raise InvalidFileTypeError("File type not allowed")


def secure_file_save(
    base_dir: str, original_filename: str, file_data: bytes
) -> Tuple[bool, str]:
    try:
        if len(file_data) > MAX_FILE_SIZE:
            raise FileTooLargeError(
                f"File exceeds maximum size of {MAX_FILE_SIZE} bytes"
            )

        mime_type = validate_file_signature(file_data)

        base_path = Path(base_dir).resolve(strict=True)

        file_extension = ".png" if mime_type == "image/png" else ".jpg"
        safe_filename = f"{uuid.uuid4()}{file_extension}"
        full_path = (base_path / safe_filename).resolve()

        if not str(full_path).startswith(str(base_path)):
            raise PathTraversalError("Path traversal attempt detected")

        full_path.parent.mkdir(parents=True, exist_ok=True)

        with open(full_path, "wb") as f:
            f.write(file_data)

        return True, str(full_path)

    except FileUploadError as e:
        return False, str(e)
    except Exception as e:
        return False, f"upload_failed: {str(e)}"
