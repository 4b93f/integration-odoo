from src.odoo_client import OdooClient

client = OdooClient()
client.connect()
client.authenticate()

# List all available models
models = client.search_read(
    model="ir.model",
    fields=["name", "model"],
)

for m in models:
    print(f"{m['model']}: {m['name']}")