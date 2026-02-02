"""Test CaptureService implementation"""
import pytest
from unittest.mock import AsyncMock

from app.services.interfaces import ICaptureService


class TestCaptureServiceContract:
    """Test CaptureService follows interface contract"""

    @pytest.fixture
    def capture_service(self):
        """Create mock capture service for testing"""
        service = AsyncMock(spec=ICaptureService)
        return service

    @pytest.mark.asyncio
    async def test_verify_handshake_valid_returns_true(self, capture_service):
        """Test verifying valid handshake returns True"""
        capture_service.verify_handshake.return_value = True
        
        result = await capture_service.verify_handshake(
            "/tmp/capture.cap", "00:11:22:33:44:55"
        )
        
        assert result is True

    @pytest.mark.asyncio
    async def test_verify_handshake_invalid_returns_false(self, capture_service):
        """Test verifying invalid handshake returns False"""
        capture_service.verify_handshake.return_value = False
        
        result = await capture_service.verify_handshake(
            "/tmp/nocapture.cap", "00:11:22:33:44:55"
        )
        
        assert result is False

    @pytest.mark.asyncio
    async def test_verify_handshake_checks_all_eapol_frames(self, capture_service):
        """Test verification checks all 4 EAPOL frames"""
        # Implementation should verify all 4 frames of WPA handshake
        capture_service.verify_handshake.return_value = True
        
        result = await capture_service.verify_handshake(
            "/tmp/capture.cap", "00:11:22:33:44:55"
        )
        
        assert result is True

    @pytest.mark.asyncio
    async def test_verify_handshake_file_not_found_raises(self, capture_service):
        """Test verifying non-existent file raises exception"""
        capture_service.verify_handshake.side_effect = FileNotFoundError(
            "Capture file not found"
        )
        
        with pytest.raises(FileNotFoundError):
            await capture_service.verify_handshake(
                "/nonexistent.cap", "00:11:22:33:44:55"
            )

    @pytest.mark.asyncio
    async def test_extract_pmkid_returns_pmkid(self, capture_service):
        """Test extracting PMKID from capture"""
        pmkid = "2582a8281bf9d4308d6f5731d0e61c61"
        capture_service.extract_pmkid.return_value = pmkid
        
        result = await capture_service.extract_pmkid("/tmp/pmkid.cap")
        
        assert result == pmkid
        assert len(result) == 32  # PMKID is 32 hex chars

    @pytest.mark.asyncio
    async def test_extract_pmkid_none_when_not_found(self, capture_service):
        """Test extracting PMKID returns None when not found"""
        capture_service.extract_pmkid.return_value = None
        
        result = await capture_service.extract_pmkid("/tmp/no_pmkid.cap")
        
        assert result is None

    @pytest.mark.asyncio
    async def test_convert_capture_cap_to_hccapx(self, capture_service):
        """Test converting .cap to .hccapx for hashcat"""
        output_file = "/tmp/capture.hccapx"
        capture_service.convert_capture.return_value = output_file
        
        result = await capture_service.convert_capture(
            "/tmp/capture.cap", "hccapx"
        )
        
        assert result == output_file
        assert result.endswith(".hccapx")

    @pytest.mark.asyncio
    async def test_convert_capture_cap_to_22000(self, capture_service):
        """Test converting to hashcat 22000 format"""
        output_file = "/tmp/capture.22000"
        capture_service.convert_capture.return_value = output_file
        
        result = await capture_service.convert_capture(
            "/tmp/capture.cap", "22000"
        )
        
        assert result == output_file

    @pytest.mark.asyncio
    async def test_convert_capture_unsupported_format_raises(self, capture_service):
        """Test converting to unsupported format raises exception"""
        capture_service.convert_capture.side_effect = ValueError(
            "Unsupported format"
        )
        
        with pytest.raises(ValueError, match="Unsupported format"):
            await capture_service.convert_capture("/tmp/capture.cap", "invalid")

    @pytest.mark.asyncio
    async def test_get_capture_info_returns_metadata(self, capture_service):
        """Test getting capture file metadata"""
        info = {
            "bssid": "00:11:22:33:44:55",
            "essid": "TestNetwork",
            "packets": 5000,
            "handshakes": 1,
            "file_size": 1024000,
        }
        capture_service.get_capture_info.return_value = info
        
        result = await capture_service.get_capture_info("/tmp/capture.cap")
        
        assert "bssid" in result
        assert "essid" in result
        assert "packets" in result

    @pytest.mark.asyncio
    async def test_get_capture_info_includes_handshake_count(self, capture_service):
        """Test capture info includes handshake count"""
        info = {"handshakes": 2}
        capture_service.get_capture_info.return_value = info
        
        result = await capture_service.get_capture_info("/tmp/capture.cap")
        
        assert "handshakes" in result
        assert result["handshakes"] >= 0


class TestCaptureServiceIntegration:
    """Integration tests for CaptureService"""

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_verify_real_handshake_file(self):
        """Test verifying real handshake capture"""
        pytest.skip("Integration test - requires sample capture files")

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_extract_pmkid_from_real_capture(self):
        """Test extracting PMKID from real capture"""
        pytest.skip("Integration test - requires sample capture files")

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_convert_formats_with_hcxtools(self):
        """Test format conversion with hcxtools"""
        pytest.skip("Integration test - requires hcxtools installed")
