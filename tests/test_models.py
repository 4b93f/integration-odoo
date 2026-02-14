"""Tests for Partner model."""
from datetime import datetime
from src.models.partner import Partner, FIELD_MAP


class TestPartnerModel:
    
    def test_field_map_has_required_fields(self):
        assert 'id' in FIELD_MAP
        assert 'name' in FIELD_MAP
        assert 'email' in FIELD_MAP
        assert FIELD_MAP['id'] == 'odoo_id'
    
    def test_partner_creation_with_all_fields(self):
        partner = Partner(
            id=1,
            odoo_id=100,
            name="Test Partner",
            email="test@example.com",
            phone="+123456",
            function="Developer",
            synced_at=datetime.now()
        )
        
        assert partner.id == 1
        assert partner.odoo_id == 100
        assert partner.name == "Test Partner"
        assert partner.email == "test@example.com"
    
    def test_partner_creation_with_optional_fields_none(self):
        partner = Partner(
            odoo_id=200,
            name="Minimal Partner",
            email=None,
            phone=None,
            function=None
        )
        
        assert partner.odoo_id == 200
        assert partner.email is None
        assert partner.phone is None
