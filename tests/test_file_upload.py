from pathlib import Path

import pytest

from app.core.file_upload import (
    MAX_FILE_SIZE,
    InvalidFileTypeError,
    secure_file_save,
    validate_file_signature,
    validate_upload_directory,
)


class TestFileUploadSecurity:

    def test_valid_png_upload(self, tmp_path):
        png_data = b"\x89PNG\r\n\x1a\n" + b"x" * 100

        success, result = secure_file_save(str(tmp_path), "test.png", png_data)

        assert success is True
        assert Path(result).exists()
        assert result.endswith(".png")
        assert "test.png" not in result

    def test_valid_jpeg_upload(self, tmp_path):
        jpeg_data = b"\xff\xd8" + b"x" * 100 + b"\xff\xd9"

        success, result = secure_file_save(str(tmp_path), "test.jpg", jpeg_data)

        assert success is True
        assert Path(result).exists()
        assert result.endswith(".jpg")

    def test_file_too_large(self, tmp_path):
        large_data = b"\x89PNG\r\n\x1a\n" + b"x" * (MAX_FILE_SIZE + 1)

        success, result = secure_file_save(str(tmp_path), "large.png", large_data)

        assert success is False
        assert "exceeds maximum size" in result

    def test_invalid_file_type(self, tmp_path):
        text_data = b"This is a text file, not an image"

        success, result = secure_file_save(str(tmp_path), "shell.txt.jpg", text_data)

        assert success is False
        assert "File type not allowed" in result

    def test_path_traversal_attempt(self, tmp_path):
        png_data = b"\x89PNG\r\n\x1a\nvalid_png"

        traversal_attempts = [
            "../../sensitive_file.png",
            "../" * 10 + "etc/passwd",
            "..\\..\\windows\\system32\\config",
            "subdir/../../sensitive_file.png",
        ]

        for attempt in traversal_attempts:
            success, result = secure_file_save(str(tmp_path), attempt, png_data)

            assert (
                success is False
            ), f"Path traversal attempt '{attempt}' was not blocked"
            assert any(
                keyword in result.lower()
                for keyword in [
                    "path traversal",
                    "dangerous",
                    "filename",
                    "pattern",
                    "invalid",
                ]
            )

    def test_symlink_protection(self, tmp_path):
        if "github" in str(tmp_path).lower() or "/tmp/pytest-of-runner/" in str(
            tmp_path
        ):
            pytest.skip(
                "Symlink test skipped in CI environment due to filesystem differences"
            )
            return

        try:
            target_dir = tmp_path / "target"
            target_dir.mkdir()

            symlink_dir = tmp_path / "symlink"
            symlink_dir.symlink_to(target_dir)

            if not symlink_dir.is_symlink():
                pytest.skip("Symlink creation failed")

            png_data = b"\x89PNG\r\n\x1a\nvalid_png"

            success, result = secure_file_save(str(symlink_dir), "test.png", png_data)

            assert success is False
            assert "symlink" in result.lower()

        except (OSError, NotImplementedError):
            pytest.skip("Symlinks not supported on this filesystem")

    def test_file_signature_validation(self):
        png_data = b"\x89PNG\r\n\x1a\n" + b"data"
        assert validate_file_signature(png_data) == "image/png"

        jpeg_data = b"\xff\xd8" + b"data" + b"\xff\xd9"
        assert validate_file_signature(jpeg_data) == "image/jpeg"

        with pytest.raises(InvalidFileTypeError):
            validate_file_signature(b"invalid_data")

    def test_magic_bytes_bypass_attempt(self, tmp_path):
        fake_png = b"\x89PNG\r\n\x1a\n" + b"fake image content"

        success, result = secure_file_save(str(tmp_path), "fake.png", fake_png)

        assert success is True

    def test_upload_directory_validation(self, tmp_path):
        assert validate_upload_directory(str(tmp_path)) is True

        assert validate_upload_directory(str(tmp_path / "nonexistent")) is False

        test_file = tmp_path / "test.txt"
        test_file.write_text("test")
        assert validate_upload_directory(str(test_file)) is False

    def test_uuid_filename_generation(self, tmp_path):
        png_data = b"\x89PNG\r\n\x1a\nvalid_png"

        success, result1 = secure_file_save(str(tmp_path), "test1.png", png_data)
        success, result2 = secure_file_save(str(tmp_path), "test2.png", png_data)

        filename1 = Path(result1).name
        filename2 = Path(result2).name

        assert filename1 != filename2
        assert len(filename1) == 36 + 4
        assert len(filename2) == 36 + 4

    def test_extension_based_on_content(self, tmp_path):
        png_data = b"\x89PNG\r\n\x1a\nvalid_png"

        success, result = secure_file_save(
            str(tmp_path), "wrong_extension.jpg", png_data
        )

        assert success is True
        assert result.endswith(".png")


class TestEdgeCases:
    def test_empty_file(self, tmp_path):
        success, result = secure_file_save(str(tmp_path), "empty.png", b"")

        assert success is False
        assert "File type not allowed" in result

    def test_exactly_max_size(self, tmp_path):
        max_size_data = b"\x89PNG\r\n\x1a\n" + b"x" * (MAX_FILE_SIZE - 8)

        success, result = secure_file_save(str(tmp_path), "max.png", max_size_data)

        assert success is True

    def test_special_characters_in_filename(self, tmp_path):
        png_data = b"\x89PNG\r\n\x1a\nvalid_png"

        dangerous_names = [
            "file with spaces.png",
            "file(with)parentheses.png",
        ]

        for name in dangerous_names:
            success, result = secure_file_save(str(tmp_path), name, png_data)
            assert success is True


@pytest.mark.parametrize(
    "test_content,description",
    [
        (b"test script content", "script-like content"),
        (b"path/traversal/attempt", "path traversal pattern"),
        (b"normal_file_content", "normal content"),
    ],
)
def test_various_content_handling(test_content, description, tmp_path):
    wrapped_content = b"\x89PNG\r\n\x1a\n" + test_content

    success, result = secure_file_save(
        str(tmp_path), f"test_{description}.png", wrapped_content
    )

    assert success is True
    assert Path(result).exists()


def test_concurrent_upload_safety(tmp_path):
    import threading

    png_data = b"\x89PNG\r\n\x1a\nvalid_png"
    results = []

    def upload_file():
        success, result = secure_file_save(str(tmp_path), "concurrent.png", png_data)
        results.append((success, result))

    threads = []
    for i in range(3):
        thread = threading.Thread(target=upload_file)
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    success_count = sum(1 for success, _ in results if success)
    assert success_count == 3

    file_paths = [result for _, result in results]
    assert len(set(file_paths)) == 3
