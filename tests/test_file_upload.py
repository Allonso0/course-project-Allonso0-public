from pathlib import Path

from app.core.file_upload import secure_file_save


class TestFileUpload:

    def test_valid_png_upload(self, tmp_path):
        png_data = b"\x89PNG\r\n\x1a\nvalid_png_data"
        success, result = secure_file_save(str(tmp_path), "test.png", png_data)
        assert success is True
        assert Path(result).exists()
        assert result.endswith(".png")

    def test_file_too_large(self, tmp_path):
        large_data = b"\x89PNG\r\n\x1a\n" + b"x" * (5_242_880 + 1)
        success, result = secure_file_save(str(tmp_path), "large.png", large_data)
        assert success is False
        assert "exceeds maximum size" in result

    def test_invalid_file_type(self, tmp_path):
        invalid_data = b"not_an_image_file"
        success, result = secure_file_save(str(tmp_path), "test.txt", invalid_data)
        assert success is False
        assert "File type not allowed" in result
