from django.db import migrations


def seed_categories(apps, schema_editor):
    Category = apps.get_model("products", "Category")

    categories = {
        "Ropa": {
            "slug": "ropa",
            "children": [
                {"name": "Camisetas", "slug": "camisetas"},
                {"name": "Camisas", "slug": "camisas"},
                {"name": "Pantalones", "slug": "pantalones"},
                {"name": "Chaquetas", "slug": "chaquetas"},
                {"name": "Vestidos", "slug": "vestidos"},
                {"name": "Sudaderas", "slug": "sudaderas"},
            ],
        },
        "Calzado": {
            "slug": "calzado",
            "children": [
                {"name": "Zapatos", "slug": "zapatos"},
                {"name": "Tenis", "slug": "tenis"},
                {"name": "Sandalias", "slug": "sandalias"},
            ],
        },
        "Accesorios": {
            "slug": "accesorios",
            "children": [
                {"name": "Bolsos", "slug": "bolsos"},
                {"name": "Relojes", "slug": "relojes"},
                {"name": "Gorras", "slug": "gorras"},
                {"name": "Joyería", "slug": "joyeria"},
            ],
        },
    }

    for parent_name, data in categories.items():
        parent = Category.objects.create(
            name=parent_name,
            slug=data["slug"],
            is_active=True,
        )
        for child_data in data["children"]:
            Category.objects.create(
                name=child_data["name"],
                slug=child_data["slug"],
                parent=parent,
                is_active=True,
            )


class Migration(migrations.Migration):

    dependencies = [
        ("products", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(seed_categories, migrations.RunPython.noop),
    ]
