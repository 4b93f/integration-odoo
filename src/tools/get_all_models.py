from src.sync.odoo_client import OdooClient


def main():
    client = OdooClient()
    client.connect()
    client.authenticate()

    models = client.execute(
        "ir.model",
        "search_read",
        [],
        {"fields": ["name", "model"]},
    )

    for m in models:
        print(f"{m['model']}: {m['name']}")


if __name__ == "__main__":
    main()
