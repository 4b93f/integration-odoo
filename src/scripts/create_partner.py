from src.odoo_client import OdooClient


def create_partner():
    client = OdooClient()
    client.connect()
    client.authenticate()
    
    print("\n📝 Create New Partner in Odoo\n")
    
    name = input("Name (required): ").strip()
    if not name:
        print("❌ Name is required")
        return
    
    email = input("Email: ").strip() or False
    phone = input("Phone: ").strip() or False
    function = input("Function/Job Position: ").strip() or False
    
    partner_data = {
        'name': name,
        'email': email,
        'phone': phone,
        'function': function,
        'active': True
    }
    
    print("\n📋 Partner to create:")
    for key, value in partner_data.items():
        print(f"  {key}: {value}")
    
    confirm = input("\nCreate this partner? (y/n): ").strip().lower()
    if confirm != 'y':
        print("Cancelled")
        return
    
    partner_id = client.models.execute_kw(
        client.db, client.uid, client.password,
        'res.partner', 'create',
        [partner_data]
    )
    
    print(f"\n✅ Partner created successfully with ID: {partner_id}")
    print(f"   Name: {name}")
    print(f"   Email: {email}")
    print(f"   Phone: {phone}")
    print(f"   Function/Job Position: {function}")

if __name__ == "__main__":
    create_partner()
