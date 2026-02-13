import xmlrpc
from src.odoo_client import OdooClient

client = OdooClient()
fields = client.get_fields("res.partner")
for field_name, field_info in fields.items():
    print(f"{field_name}: {field_info['type']}")
