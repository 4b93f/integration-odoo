"""Tests for partner sync functionality."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime
from src.sync.sync_partners import sync_partners, upsert_partners


@pytest.mark.asyncio
class TestPartnerSync:
    
    @patch('src.sync.sync_partners.OdooClient')
    @patch('src.sync.sync_partners.upsert_partners')
    @patch('src.sync.sync_partners.delete_removed_partners') # DO NOT REMOVE THIS, OR DISASTER
    async def test_sync_partners_maps_fields_correctly(self, mock_delete, mock_upsert, mock_client_class):
        mock_client = MagicMock()
        mock_client.get_partners.return_value = [
            {
                'id': 1,
                'name': 'Test Partner',
                'email': 'test@example.com',
                'phone': '+123456',
                'function': 'Developer',
                'active': True
            }
        ]
        mock_client_class.return_value = mock_client
        mock_upsert.return_value = None
        mock_delete.return_value = None
        session = MagicMock()
        await sync_partners(session)
        
        assert mock_upsert.called
        records = mock_upsert.call_args[0][0]
        
        assert len(records) == 1
        assert records[0]['odoo_id'] == 1
        assert records[0]['name'] == 'Test Partner'
        assert records[0]['email'] == 'test@example.com'
    
    @patch('src.sync.sync_partners.OdooClient')
    @patch('src.sync.sync_partners.upsert_partners')
    @patch('src.sync.sync_partners.delete_removed_partners')
    async def test_sync_partners_handles_missing_fields(self, mock_delete, mock_upsert, mock_client_class):
        mock_client = MagicMock()
        mock_client.get_partners.return_value = [
            {
                'id': 2,
                'name': 'Minimal Partner',
                'email': None,
                'phone': None,
                'function': None,
                'active': True
            }
        ]
        mock_client_class.return_value = mock_client
        mock_upsert.return_value = None
        mock_delete.return_value = None
        session = MagicMock()
        await sync_partners(session)
        
        records = mock_upsert.call_args[0][0]
        assert records[0]['email'] is None
        assert records[0]['phone'] is None
        assert records[0]['function'] is None
