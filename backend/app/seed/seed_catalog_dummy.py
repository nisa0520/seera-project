"""Seed catalog products and colors using local public clothing assets."""
from sqlalchemy.orm import Session as DBSession
from app.models.category import Category
from app.models.color import Color
from app.models.product import Product
from app.models.product_color import ProductColor
from app.services.color_feature_service import compute_color_features


CATEGORIES = ["Atasan", "Bawahan", "Outerwear", "Dress", "Aksesoris"]


COLORS_SEED = [
    {"name": "Black", "hex": "#111111"},
    {"name": "Ash Gray", "hex": "#9A9A9A"},
    {"name": "Chocolate Brown", "hex": "#6B3F2A"},
    {"name": "Forest Green", "hex": "#2F5D50"},
    {"name": "Taupe", "hex": "#B7A18B"},
    {"name": "Dusty Pink", "hex": "#E8A7B7"},
    {"name": "Off White", "hex": "#F8F3E8"},
    {"name": "Deep Teal", "hex": "#1F5A5C"},
    {"name": "Mocha Brown", "hex": "#8B5E3C"},
    {"name": "Slate Blue", "hex": "#4F6F8F"},
    {"name": "Navy Blue", "hex": "#1B3A6B"},
    {"name": "Canary Yellow", "hex": "#F2CB6A"},
    {"name": "Ivory White", "hex": "#F2E8E0"},
    {"name": "Sage Green", "hex": "#8FA68A"},
    {"name": "Warm Yellow", "hex": "#FFD447"},
    {"name": "Powder Blue", "hex": "#A8C0D6"},
    {"name": "Burgundy", "hex": "#7A1B3A"},
    {"name": "Peach", "hex": "#F4A77F"},
    {"name": "Lavender", "hex": "#D5C7E0"},
    {"name": "Charcoal", "hex": "#1F1B16"},
    {"name": "Rust Brown", "hex": "#A85E40"},
    {"name": "Mustard", "hex": "#C4863F"},
    {"name": "Sky Blue", "hex": "#7FA4C2"},
    {"name": "Soft Pink", "hex": "#F2C9B4"},
    {"name": "Olive Deep", "hex": "#7B6B47"},
    {"name": "Cream", "hex": "#F4D7C0"},
    {"name": "Royal Plum", "hex": "#5C2B7A"},
    {"name": "Camel", "hex": "#E8C896"},
    {"name": "Terracotta", "hex": "#C47A5C"},
    {"name": "Mint", "hex": "#7BC4C9"},
]


PRODUCTS_SEED = [
    {
        "external_catalog_id": "SK-001",
        "name": "Koko Putih Classic",
        "price": 250000,
        "rating": 4.8,
        "stock": 24,
        "popularity": 180,
        "category": "Atasan",
        "is_active": True,
        "colors": [("Off White", "DOMINANT", 100.0)],
        "image_url": "/koko-putih.png",
        "description": "Koko putih clean look dari asset public/koko-putih.png.",
    },
    {
        "external_catalog_id": "SK-002",
        "name": "Koko Abu Minimalis",
        "price": 290000,
        "rating": 4.6,
        "stock": 18,
        "popularity": 135,
        "category": "Atasan",
        "is_active": True,
        "colors": [("Ash Gray", "DOMINANT", 100.0)],
        "image_url": "/koko-abu.png",
        "description": "Koko abu netral yang sinkron dengan public/koko-abu.png.",
    },
    {
        "external_catalog_id": "SK-003",
        "name": "Koko Biru Modern",
        "price": 280000,
        "rating": 4.5,
        "stock": 20,
        "popularity": 150,
        "category": "Atasan",
        "is_active": True,
        "colors": [("Slate Blue", "DOMINANT", 100.0)],
        "image_url": "/koko-biru.png",
        "description": "Koko biru modern dari asset public/koko-biru.png.",
    },
    {
        "external_catalog_id": "SK-004",
        "name": "Koko Hijau Sage",
        "price": 220000,
        "rating": 4.7,
        "stock": 16,
        "popularity": 170,
        "category": "Atasan",
        "is_active": True,
        "colors": [("Sage Green", "DOMINANT", 100.0)],
        "image_url": "/koko-hijau.png",
        "description": "Koko hijau bernuansa sage dari asset public/koko-hijau.png.",
    },
    {
        "external_catalog_id": "SK-005",
        "name": "Koko Coklat Earth Tone",
        "price": 240000,
        "rating": 4.4,
        "stock": 12,
        "popularity": 115,
        "category": "Atasan",
        "is_active": True,
        "colors": [("Chocolate Brown", "DOMINANT", 100.0)],
        "image_url": "/koko-coklat.png",
        "description": "Koko coklat warm dari asset public/koko-coklat.png.",
    },
    {
        "external_catalog_id": "SK-006",
        "name": "Koko Batik Taupe",
        "price": 300000,
        "rating": 4.6,
        "stock": 10,
        "popularity": 105,
        "category": "Atasan",
        "is_active": True,
        "colors": [
            ("Taupe", "DOMINANT", 60.0),
            ("Chocolate Brown", "SECONDARY", 25.0),
            ("Camel", "ACCENT", 15.0),
        ],
        "image_url": "/koko-bt.png",
        "description": "Koko batik taupe dengan aksen coklat dari asset public/koko-bt.png.",
    },
    {
        "external_catalog_id": "SK-007",
        "name": "Koko Teal Premium",
        "price": 350000,
        "rating": 4.7,
        "stock": 9,
        "popularity": 95,
        "category": "Atasan",
        "is_active": True,
        "colors": [
            ("Deep Teal", "DOMINANT", 80.0),
            ("Charcoal", "SECONDARY", 20.0),
        ],
        "image_url": "/koko-t.png",
        "description": "Koko premium bernuansa teal dari asset public/koko-t.png.",
    },
    {
        "external_catalog_id": "SK-008",
        "name": "Abaya Hitam Premium (Out of Stock)",
        "price": 300000,
        "rating": 4.9,
        "stock": 0,
        "popularity": 200,
        "category": "Dress",
        "is_active": True,
        "colors": [("Black", "DOMINANT", 100.0)],
        "image_url": "/abaya-hitam.png",
        "description": "Abaya hitam premium dari asset public/abaya-hitam.png.",
    },
    {
        "external_catalog_id": "SK-009",
        "name": "Koko Putih Waffle",
        "price": 275000,
        "rating": 4.9,
        "stock": 14,
        "popularity": 125,
        "category": "Atasan",
        "is_active": True,
        "colors": [
            ("Off White", "DOMINANT", 85.0),
            ("Charcoal", "SECONDARY", 15.0),
        ],
        "image_url": "/koko-w.png",
        "description": "Koko putih dengan detail gelap dari asset public/koko-w.png.",
    },
    {
        "external_catalog_id": "SK-010",
        "name": "Koko Navy Seera",
        "price": 260000,
        "rating": 4.3,
        "stock": 17,
        "popularity": 128,
        "category": "Atasan",
        "is_active": True,
        "colors": [("Navy Blue", "DOMINANT", 100.0)],
        "image_url": "/koko.png",
        "description": "Koko navy basic dari asset public/koko.png.",
    },
    {
        "external_catalog_id": "SK-011",
        "name": "Gamis Pink Elegan",
        "price": 280000,
        "rating": 4.5,
        "stock": 13,
        "popularity": 145,
        "category": "Dress",
        "is_active": True,
        "colors": [
            ("Dusty Pink", "DOMINANT", 75.0),
            ("Cream", "SECONDARY", 25.0),
        ],
        "image_url": "/gamis-pink.png",
        "description": "Gamis pink elegan dari asset public/gamis-pink.png.",
    },
    {
        "external_catalog_id": "SK-012",
        "name": "Gamis Coklat Daily",
        "price": 200000,
        "rating": 4.6,
        "stock": 21,
        "popularity": 132,
        "category": "Dress",
        "is_active": True,
        "colors": [
            ("Mocha Brown", "DOMINANT", 70.0),
            ("Camel", "SECONDARY", 30.0),
        ],
        "image_url": "/gamis-coklat.png",
        "description": "Gamis coklat daily dari asset public/gamis-coklat.png.",
    },
    {
        "external_catalog_id": "SK-013",
        "name": "Gamis Peach Executive",
        "price": 350000,
        "rating": 4.7,
        "stock": 8,
        "popularity": 118,
        "category": "Dress",
        "is_active": True,
        "colors": [
            ("Peach", "DOMINANT", 70.0),
            ("Cream", "SECONDARY", 30.0),
        ],
        "image_url": "/gamis-p.png",
        "description": "Gamis executive bernuansa peach dari asset public/gamis-p.png.",
    },
    {
        "external_catalog_id": "SK-014",
        "name": "Gamis Cream Flow",
        "price": 320000,
        "rating": 4.5,
        "stock": 15,
        "popularity": 108,
        "category": "Dress",
        "is_active": True,
        "colors": [
            ("Cream", "DOMINANT", 70.0),
            ("Dusty Pink", "SECONDARY", 30.0),
        ],
        "image_url": "/gamis.png",
        "description": "Gamis cream flow dari asset public/gamis.png.",
    },
    {
        "external_catalog_id": "SK-015",
        "name": "Abaya Neutral Seera",
        "price": 330000,
        "rating": 4.2,
        "stock": 11,
        "popularity": 112,
        "category": "Dress",
        "is_active": True,
        "colors": [
            ("Charcoal", "DOMINANT", 65.0),
            ("Off White", "SECONDARY", 35.0),
        ],
        "image_url": "/abaya.png",
        "description": "Abaya neutral dari asset public/abaya.png.",
    },
    {
        "external_catalog_id": "SK-016",
        "name": "Hijab Lavender Soft",
        "price": 240000,
        "rating": 4.4,
        "stock": 25,
        "popularity": 122,
        "category": "Aksesoris",
        "is_active": True,
        "colors": [
            ("Lavender", "DOMINANT", 65.0),
            ("Soft Pink", "SECONDARY", 35.0),
        ],
        "image_url": "/hijab.png",
        "description": "Hijab soft tone dari asset public/hijab.png.",
    },
]


def seed_colors(db: DBSession) -> dict[str, int]:
    name_to_id: dict[str, int] = {}
    for entry in COLORS_SEED:
        color = db.query(Color).filter(Color.hex_code == entry["hex"]).first()
        features = compute_color_features(entry["hex"])
        if not color:
            color = Color(
                color_name=entry["name"],
                hex_code=entry["hex"],
                r=features["r"],
                g=features["g"],
                b=features["b"],
                h=features["h"],
                s=features["s"],
                v=features["v"],
                ct=features["ct"],
                cb=features["cb"],
            )
            db.add(color)
            db.flush()
        else:
            color.color_name = entry["name"]
            color.r = features["r"]
            color.g = features["g"]
            color.b = features["b"]
            color.h = features["h"]
            color.s = features["s"]
            color.v = features["v"]
            color.ct = features["ct"]
            color.cb = features["cb"]
        name_to_id[entry["name"]] = color.id
    db.commit()
    return name_to_id


def seed_categories(db: DBSession) -> dict[str, int]:
    out: dict[str, int] = {}
    for name in CATEGORIES:
        cat = db.query(Category).filter(Category.name == name).first()
        if not cat:
            cat = Category(name=name)
            db.add(cat)
            db.flush()
        out[name] = cat.id
    db.commit()
    return out


def seed_products(db: DBSession) -> None:
    color_ids = seed_colors(db)
    category_ids = seed_categories(db)

    for entry in PRODUCTS_SEED:
        product = (
            db.query(Product)
            .filter(Product.external_catalog_id == entry["external_catalog_id"])
            .first()
        )
        if not product:
            product = Product(
                external_catalog_id=entry["external_catalog_id"],
                name=entry["name"],
                price=entry["price"],
                rating=entry["rating"],
                stock=entry["stock"],
                popularity=entry["popularity"],
                category_id=category_ids.get(entry["category"]),
                is_active=entry["is_active"],
                image_url=entry.get("image_url"),
                description=entry.get("description"),
            )
            db.add(product)
            db.flush()
        else:
            product.name = entry["name"]
            product.price = entry["price"]
            product.rating = entry["rating"]
            product.stock = entry["stock"]
            product.popularity = entry["popularity"]
            product.category_id = category_ids.get(entry["category"])
            product.is_active = entry["is_active"]
            product.image_url = entry.get("image_url")
            product.description = entry.get("description")
            # purge existing product_colors to re-seed
            for pc in list(product.product_colors):
                db.delete(pc)
            db.flush()

        for idx, (color_name, role, pct) in enumerate(entry["colors"], start=1):
            db.add(
                ProductColor(
                    product_id=product.id,
                    color_id=color_ids[color_name],
                    color_role=role,
                    color_rank=idx,
                    color_percentage=pct,
                )
            )
    db.commit()


def seed_catalog(db: DBSession) -> None:
    seed_products(db)
