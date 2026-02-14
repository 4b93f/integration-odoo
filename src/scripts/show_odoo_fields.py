from src.odoo_client import OdooClient


def show_partners():
    client = OdooClient()
    client.connect()
    client.authenticate()
    
    # Get all partners
    partners = client.models.execute_kw(
        client.db, client.uid, client.password,
        'res.partner', 'search_read',
        [[]],
        {}
    )
    
    print(f"\n📋 Found {len(partners)} partners\n")
    
    for idx, partner in enumerate(partners, 1):
        print(f"Partner #{idx}:")
        print(f"  Active: {partner.get('active')}, Name: {partner.get('name')}, Email: {partner.get('email')}, Phone: {partner.get('phone')}")


if __name__ == "__main__":
    show_partners()
