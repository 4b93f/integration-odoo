from src.odoo_client import OdooClient


def show_partners():
    client = OdooClient()
    client.connect()
    client.authenticate()
    
    # Get all partners
    partners = client.get_partners()
    
    print(f"\n📋 Found {len(partners)} partners\n")
    
    for idx, partner in enumerate(partners, 1):
        print(f"Partner #{idx}:")
        print(f"  Active: {partner.get('active')}, Name: {partner.get('name')}, Email: {partner.get('email')}, Phone: {partner.get('phone')}")

def show_invoices():
    client = OdooClient()
    client.connect()
    client.authenticate()
    
    # Get all invoices
    invoices = client.get_invoices()
    
    print(f"\n📋 Found {len(invoices)} invoices\n")
    
    for idx, invoice in enumerate(invoices, 1):
        print(f"Invoice #{idx}:")
        print(f"Customer: {invoice.get('partner_id')}")
        print(f"Name: {invoice.get('name')}, Date: {invoice.get('date')}, Untaxed Amount: {invoice.get('amount_untaxed')}, Amount: {invoice.get('amount_total')}")


if __name__ == "__main__":
    show_partners()
    show_invoices()
