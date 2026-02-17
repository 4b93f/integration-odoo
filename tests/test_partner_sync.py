"""Tests for partner sync functionality."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime
from src.sync.sync_partners import sync_partners


@pytest.mark.asyncio
class TestPartnerSync:
    
    @patch('src.sync.sync_partners.PartnerService')
    async def test_sync_partners_calls_service(self, mock_service_class):
        # Mock service
        mock_service = AsyncMock()
        mock_service.sync_from_odoo = AsyncMock(return_value={
            'upserted': 1,
            'deleted': 0,
            'total_fetched': 1
        })
        mock_service_class.return_value = mock_service
        
        session = MagicMock()
        await sync_partners(session)
        
        # Verify service was instantiated with session
        mock_service_class.assert_called_once_with(session)
        
        # Verify sync was called
        mock_service.sync_from_odoo.assert_called_once()
    
    @patch('src.sync.sync_partners.PartnerService')
    async def test_sync_partners_handles_service_error(self, mock_service_class):
        # Mock service to raise exception
        mock_service = AsyncMock()
        mock_service.sync_from_odoo = AsyncMock(side_effect=Exception("Odoo connection failed"))
        mock_service_class.return_value = mock_service
        
        session = MagicMock()
        
        # Verify exception is raised
        with pytest.raises(Exception, match="Odoo connection failed"):
            await sync_partners(session)
