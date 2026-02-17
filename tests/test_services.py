"""Tests for service layer."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime
from src.services.partner_service import PartnerService
from src.services.invoice_service import InvoiceService


@pytest.mark.asyncio
class TestPartnerService:
    
    @patch('src.services.partner_service.PartnerRepository')
    async def test_get_all_partners(self, mock_repo_class):
        # Setup
        mock_repo = AsyncMock()
        mock_repo.get_all = AsyncMock(return_value=[MagicMock(), MagicMock()])
        mock_repo_class.return_value = mock_repo
        
        session = MagicMock()
        service = PartnerService(session)
        
        # Execute
        result = await service.get_all_partners()
        
        # Verify
        assert len(result) == 2
        mock_repo.get_all.assert_called_once()
    
    @patch('src.services.partner_service.PartnerRepository')
    async def test_get_partner_by_odoo_id(self, mock_repo_class):
        # Setup
        mock_partner = MagicMock(odoo_id=123)
        mock_repo = AsyncMock()
        mock_repo.get_by_odoo_id = AsyncMock(return_value=mock_partner)
        mock_repo_class.return_value = mock_repo
        
        session = MagicMock()
        service = PartnerService(session)
        
        # Execute
        result = await service.get_partner_by_odoo_id(123)
        
        # Verify
        assert result == mock_partner
        mock_repo.get_by_odoo_id.assert_called_once_with(123)
    
    @patch('src.services.partner_service.OdooClient')
    @patch('src.services.partner_service.PartnerRepository')
    async def test_sync_from_odoo_success(self, mock_repo_class, mock_client_class):
        # Setup Odoo client
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
        
        # Setup repository
        mock_repo = AsyncMock()
        mock_repo.upsert_batch = AsyncMock(return_value=1)
        mock_repo.delete_by_odoo_ids_not_in = AsyncMock(return_value=0)
        mock_repo_class.return_value = mock_repo
        
        session = MagicMock()
        service = PartnerService(session)
        
        # Execute
        stats = await service.sync_from_odoo()
        
        # Verify
        assert stats['upserted'] == 1
        assert stats['deleted'] == 0
        assert stats['total_fetched'] == 1
        mock_client.authenticate.assert_called_once()
        mock_client.get_partners.assert_called_once()
        mock_repo.upsert_batch.assert_called_once()
        mock_repo.delete_by_odoo_ids_not_in.assert_called_once()
    
    @patch('src.services.partner_service.OdooClient')
    @patch('src.services.partner_service.PartnerRepository')
    async def test_sync_from_odoo_handles_auth_failure(self, mock_repo_class, mock_client_class):
        # Setup
        mock_client = MagicMock()
        mock_client.authenticate.side_effect = Exception("Auth failed")
        mock_client_class.return_value = mock_client
        
        mock_repo = AsyncMock()
        mock_repo_class.return_value = mock_repo
        
        session = MagicMock()
        service = PartnerService(session)
        
        # Execute & Verify
        with pytest.raises(Exception, match="Auth failed"):
            await service.sync_from_odoo()


@pytest.mark.asyncio
class TestInvoiceService:
    
    @patch('src.services.invoice_service.InvoiceRepository')
    async def test_get_all_invoices(self, mock_repo_class):
        # Setup
        mock_repo = AsyncMock()
        mock_repo.get_all = AsyncMock(return_value=[MagicMock(), MagicMock(), MagicMock()])
        mock_repo_class.return_value = mock_repo
        
        session = MagicMock()
        service = InvoiceService(session)
        
        # Execute
        result = await service.get_all_invoices()
        
        # Verify
        assert len(result) == 3
        mock_repo.get_all.assert_called_once()
    
    @patch('src.services.invoice_service.InvoiceRepository')
    async def test_get_invoices_by_partner(self, mock_repo_class):
        # Setup
        mock_repo = AsyncMock()
        mock_repo.get_by_partner_id = AsyncMock(return_value=[MagicMock(), MagicMock()])
        mock_repo_class.return_value = mock_repo
        
        session = MagicMock()
        service = InvoiceService(session)
        
        # Execute
        result = await service.get_invoices_by_partner(42)
        
        # Verify
        assert len(result) == 2
        mock_repo.get_by_partner_id.assert_called_once_with(42)
    
    @patch('src.services.invoice_service.OdooClient')
    @patch('src.services.invoice_service.InvoiceRepository')
    async def test_sync_from_odoo_success(self, mock_repo_class, mock_client_class):
        # Setup Odoo client
        mock_client = MagicMock()
        mock_client.get_invoices.return_value = [
            {
                'id': 1,
                'name': 'INV/2024/001',
                'partner_id': [10, 'Test Partner'],
                'amount_total': 1000.50,
                'state': 'posted'
            },
            {
                'id': 2,
                'name': 'INV/2024/002',
                'partner_id': [20, 'Another Partner'],
                'amount_total': 2500.00,
                'state': 'draft'
            }
        ]
        mock_client_class.return_value = mock_client
        
        # Setup repository
        mock_repo = AsyncMock()
        mock_repo.upsert_batch = AsyncMock(return_value=2)
        mock_repo_class.return_value = mock_repo
        
        session = MagicMock()
        service = InvoiceService(session)
        
        # Execute
        stats = await service.sync_from_odoo()
        
        # Verify
        assert stats['upserted'] == 2
        assert stats['total_fetched'] == 2
        mock_client.authenticate.assert_called_once()
        mock_client.get_invoices.assert_called_once()
        mock_repo.upsert_batch.assert_called_once()
