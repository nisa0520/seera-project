from sqlalchemy.orm import Session as DBSession

from .color_utils import compute_color_features
from .models import Category, Product, Color, ProductColor


SAMPLE_CATEGORIES = [
    {"name": "Gamis"},
    {"name": "Koko"},
    {"name": "Hijab"},
    {"name": "Abaya"},
    {"name": "Outer"},
]

SAMPLE_PRODUCTS = [
    {
        "name": "Gamis Dusty Rose",
        "description": "Gamis daily look feminine dengan warna soft pink.",
        "price": 329000,
        "rating": 4.7,
        "popularity": 284,
        "stock": 150,
        "image_url": "/gamis-pink.png",
        "category": "Gamis",
        "colors": [
            ("#B76E79", "Dusty Rose"),
            ("#F3D9DC", "Soft Pink"),
        ],
    },
    {
        "name": "Koko Navy Elegance",
        "description": "Koko premium warna navy elegan.",
        "price": 289000,
        "rating": 4.8,
        "popularity": 312,
        "stock": 200,
        "image_url": "/koko-abu.png",
        "category": "Koko",
        "colors": [
            ("#1B3A6B", "Navy Blue"),
            ("#E8E8E8", "Silver Grey"),
        ],
    },
    {
        "name": "Abaya Charcoal Modern",
        "description": "Abaya modern warna netral gelap.",
        "price": 359000,
        "rating": 4.9,
        "popularity": 430,
        "stock": 50,
        "image_url": "/abaya-hitam.png",
        "category": "Abaya",
        "colors": [
            ("#2E2E2E", "Charcoal"),
            ("#8A8A8A", "Medium Grey"),
        ],
    },
    {
        "name": "Koko Olive Heritage",
        "description": "Koko nuansa earthy warm yang hangat.",
        "price": 269000,
        "rating": 4.6,
        "popularity": 226,
        "stock": 100,
        "image_url": "/koko-hijau.png",
        "category": "Koko",
        "colors": [
            ("#6B8E23", "Olive Green"),
            ("#C2B280", "Warm Beige"),
            ("#3B2F2F", "Dark Brown"),
        ],
    },
    {
        "name": "Hijab Lilac Glow",
        "description": "Hijab ringan warna cool light lavender.",
        "price": 149000,
        "rating": 4.5,
        "popularity": 198,
        "stock": 300,
        "image_url": "/hijab.png",
        "category": "Hijab",
        "colors": [
            ("#C8A2C8", "Lilac"),
        ],
    },
]

def seed_products(db: DBSession):
    if db.query(Product).first():
        return

    cat_map = {}
    for cat_data in SAMPLE_CATEGORIES:
        category = Category(name=cat_data["name"])
        db.add(category)
        db.flush()
        cat_map[cat_data["name"]] = category.id

    for p_data in SAMPLE_PRODUCTS:
        product = Product(
            name=p_data["name"],
            description=p_data["description"],
            price=p_data["price"],
            rating=p_data["rating"],
            popularity=p_data["popularity"],
            stock=p_data["stock"],
            image_url=p_data["image_url"],
            thumbnail_url=p_data["image_url"],
            category_id=cat_map[p_data["category"]],
        )
        db.add(product)
        db.flush()

        for idx, (hex_code, color_name) in enumerate(p_data["colors"]):
            color = db.query(Color).filter(Color.hex_code == hex_code).first()
            if not color:
                features = compute_color_features(hex_code)
                # Map old features dict keys to match Color model
                r, g, b = features.pop("r_value", 0), features.pop("g_value", 0), features.pop("b_value", 0)
                if r == 0 and g == 0 and b == 0:
                    # quick calculation if compute_color_features doesn't return r_value
                    hex_clean = hex_code.lstrip('#')
                    r, g, b = tuple(int(hex_clean[i:i+2], 16) for i in (0, 2, 4))
                
                h = features.get("h_value", 0.0)
                s = features.get("s_value", 0.0)
                v = features.get("v_value", 0.0)
                ct = features.get("ct_value", 1.0)
                cb = features.get("cb_value", v)

                color = Color(
                    hex_code=hex_code,
                    color_name=color_name,
                    r=r, g=g, b=b,
                    h=h, s=s, v=v,
                    ct=ct, cb=cb
                )
                db.add(color)
                db.flush()
            
            pc = ProductColor(
                product_id=product.id,
                color_id=color.id,
                dominance_rank=idx + 1
            )
            db.add(pc)

    db.commit()
