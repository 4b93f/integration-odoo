"""Tests for OdooClient."""
import pytest
from unittest.mock import patch, MagicMock
from src.sync.odoo_client import OdooClient


class TestOdooClient:
    
    @patch('src.sync.odoo_client.xmlrpc.client.ServerProxy')
    def test_connect_success(self, mock_proxy):
        mock_common = MagicMock()
        mock_common.version.return_value = {'server_version': '16.0'}
        mock_proxy.return_value = mock_common
        
        client = OdooClient()
        result = client.connect()
        
        assert client._connected is True
        assert result == {'server_version': '16.0'}
    
    @patch('src.sync.odoo_client.xmlrpc.client.ServerProxy')
    def test_authenticate_success(self, mock_proxy=MagicMock()):
        mock_common = MagicMock()
        mock_common.authenticate.return_value = 42
        
        client = OdooClient()
        client.common = mock_common
        client._connected = True
        
        uid = client.authenticate()
        
        assert uid == 42
        assert client.uid == 42
    
    @patch('src.sync.odoo_client.xmlrpc.client.ServerProxy')
    def test_get_partners_with_active_filter(self, 	mock_proxy=MagicMock()):
        mock_models = MagicMock()
        mock_models.execute_kw.return_value = [
            {'id': 1, 'name': 'Active Partner', 'active': True}
        ]
        
        client = OdooClient()
        client.models = mock_models
        client.uid = 1
        client._connected = True
        
        partners = client.get_partners()
        
        assert mock_models.execute_kw.called
        call_args = mock_models.execute_kw.call_args[0]
        
        assert call_args[3] == 'res.partner'
        assert call_args[4] == 'search_read'
        assert len(partners) == 1
