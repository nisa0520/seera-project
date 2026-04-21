from sqlalchemy.orm import Session

from .color_utils import compute_color_features
from .models import Product, ProductColor


SAMPLE_PRODUCTS = [
    {
        "name": "Koko Navy Elegance",
        "description": "Koko premium warna navy.",
        "price": 289000,
        "rating": 4.8,
        "sold_count": 312,
        "image_url": "/koko-abu.png",
        "colors": ["#1B3A6B", "#E8E8E8"],
    },
    {
        "name": "Gamis Dusty Rose",
        "description": "Gamis daily look feminine.",
        "price": 329000,
        "rating": 4.7,
        "sold_count": 284,
        "image_url": "/gamis-pink.png",
        "colors": ["#B76E79", "#F3D9DC"],
    },
    {
        "name": "Abaya Charcoal",
        "description": "Abaya modern warna netral gelap.",
        "price": 359000,
        "rating": 4.9,
        "sold_count": 430,
        "image_url": "/abaya-hitam.png",
        "colors": ["#2E2E2E", "#8A8A8A"],
    },
    {
        "name": "Koko Olive Heritage",
        "description": "Koko nuansa earthy warm.",
        "price": 269000,
        "rating": 4.6,
        "sold_count": 226,
        "image_url": "/koko-hijau.png",
        "colors": ["#6B8E23", "#C2B280", "#3B2F2F"],
    },
    {
        "name": "Hijab Lilac Glow",
        "description": "Hijab ringan warna cool light.",
        "price": 149000,
        "rating": 4.5,
        "sold_count": 198,
        "image_url": "/hijab.png",
        "colors": ["#C8A2C8"],
    },
]


def seed_products(db: Session):
    has_data = db.query(Product).first()
    if has_data:
        return

    for item in SAMPLE_PRODUCTS:
        product = Product(
            name=item["name"],
            description=item["description"],
            price=item["price"],
            rating=item["rating"],
            sold_count=item["sold_count"],
            image_url=item["image_url"],
        )
        db.add(product)
        db.flush()

        for index, hex_code in enumerate(item["colors"], start=1):
            features = compute_color_features(hex_code)
            color = ProductColor(
                product_id=product.id,
                hex_code=hex_code,
                color_order=index,
                **features,
            )
            db.add(color)

    db.commit()
