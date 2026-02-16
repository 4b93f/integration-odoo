from src.sync.odoo_client import OdooClient
import sys


def archive_partner():
    client = OdooClient()
    client.connect()
    client.authenticate()
    
    if len(sys.argv) > 1:
        search_term = ' '.join(sys.argv[1:])
    else:
        search_term = input("Enter partner name or ID to archive: ").strip()
    
    try:
        partner_id = int(search_term)
        domain = [('id', '=', partner_id)]
    except ValueError:
        domain = [('name', 'ilike', search_term)]
    
    partners = client.models.execute_kw(
        client.db, client.uid, client.password,
        'res.partner', 'search_read',
        [domain],
        {'fields': ['id', 'name', 'email', 'active']}
    )
    
    if not partners:
        print(f"\n⚠️  No partner found matching: {search_term}")
        return
    
    if len(partners) > 1:
        print(f"\n⚠️  Found {len(partners)} partners:")
        for p in partners:
            print(f"  ID {p['id']}: {p['name']} ({p['email']}) - Active: {p['active']}")
        print("\nPlease be more specific or use the exact ID")
        return
    
    partner = partners[0]
    print(f"\nFound: ID {partner['id']}: {partner['name']} - Active: {partner['active']}")
    
    if not partner['active']:
        print("✓ Partner is already archived")
        return
    
    confirm = input("Archive this partner? (y/n): ").strip().lower()
    if confirm != 'y':
        print("Cancelled")
        return
    
    client.models.execute_kw(
        client.db, client.uid, client.password,
        'res.partner', 'write',
        [[partner['id']], {'active': False}]
    )
    
    print(f"\n✅ Partner '{partner['name']}' has been archived")


if __name__ == "__main__":
    archive_partner()
