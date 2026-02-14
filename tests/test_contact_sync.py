"""Tests for contact sync functionality."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime
from src.contact_sync import sync_contacts, upsert_contacts


@pytest.mark.asyncio
class TestContactSync:
    
    @patch('src.contact_sync.OdooClient')
    @patch('src.contact_sync.upsert_contacts')
    @patch('src.contact_sync.delete_removed_contacts') # DO NOT REMOVE THIS, OR DISASTER
    async def test_sync_contacts_maps_fields_correctly(self, mock_delete, mock_upsert, mock_client_class):
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
        
        await sync_contacts()
        
        assert mock_upsert.called
        records = mock_upsert.call_args[0][0]
        
        assert len(records) == 1
        assert records[0]['odoo_id'] == 1
        assert records[0]['name'] == 'Test Partner'
        assert records[0]['email'] == 'test@example.com'
    
    @patch('src.contact_sync.OdooClient')
    @patch('src.contact_sync.upsert_contacts')
    @patch('src.contact_sync.delete_removed_contacts')
    async def test_sync_contacts_handles_missing_fields(self, mock_delete, mock_upsert, mock_client_class):
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
        
        await sync_contacts()
        
        records = mock_upsert.call_args[0][0]
        assert records[0]['email'] is None
        assert records[0]['phone'] is None
        assert records[0]['function'] is None