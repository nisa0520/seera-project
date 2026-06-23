"""Visual matching: virtual try-on produk rekomendasi + background (FR-IMG-11/12)."""
from typing import Optional

from sqlalchemy.orm import Session as DBSession

from app.models.session import Session
from app.models.product import Product
from app.models.recommendation import Recommendation
from app.models.recommendation_item import RecommendationItem
from app.models.visual_match_session import VisualMatchSession
from app.models.image_analysis_session import ImageAnalysisSession
from app.services.background_service import BackgroundService
from app.core.exceptions import InvalidConversationStateError


# Hex representatif skala Fitzpatrick — fallback bila sesi tidak punya analisis image.
FITZPATRICK_HEX = {
    1.0: "#F5DBC4",
    2.0: "#EAC2A0",
    3.0: "#D4A382",
    4.0: "#A87858",
    5.0: "#7A4F36",
    6.0: "#4A2E20",
}
DEFAULT_SKIN_HEX = "#D4A382"

GARMENT_GAMIS = "GAMIS"
GARMENT_ABAYA = "ABAYA"
GARMENT_KOKO = "KOKO"
GARMENT_HIJAB = "HIJAB"

# Fallback posisi kepala bila aset belum punya anotasi anchor (fraksi dimensi foto).
DEFAULT_FACE_ANCHORS = {
    GARMENT_KOKO: {"cx": 0.50, "cy": -0.12, "w": 0.26},
    GARMENT_GAMIS: {"cx": 0.50, "cy": 0.06, "w": 0.16},
    GARMENT_ABAYA: {"cx": 0.50, "cy": 0.04, "w": 0.20},
    GARMENT_HIJAB: {"cx": 0.50, "cy": 0.30, "w": 0.34},
}


class VisualMatchService:
    def __init__(self, db: DBSession):
        self.db = db
        self.backgrounds = BackgroundService(db)

    def _recommended_product(self, recommendation: Recommendation, product_id: int) -> Product:
        """Produk hanya boleh berasal dari item rekomendasi sesi (BR-IMG-06)."""
        item = (
            self.db.query(RecommendationItem)
            .filter(
                RecommendationItem.recommendation_id == recommendation.id,
                RecommendationItem.product_id == product_id,
            )
            .first()
        )
        if not item:
            raise InvalidConversationStateError(
                "Produk tidak termasuk dalam rekomendasi sesi ini."
            )
        return item.product

    def create_preview(
        self,
        session: Session,
        recommendation: Recommendation,
        product_id: int,
        background_id: Optional[int],
    ) -> dict:
        product = self._recommended_product(recommendation, product_id)

        background = None
        if background_id is not None:
            background = self.backgrounds.get_active(background_id)
            if not background:
                raise InvalidConversationStateError("Background preset tidak tersedia.")

        preview_config = self._build_preview_config(session, product, background)

        match = VisualMatchSession(
            session_id=session.id,
            recommendation_id=recommendation.id,
            selected_product_id=product.id,
            selected_background_id=background.id if background else None,
            preview_config=preview_config,
        )
        self.db.add(match)
        self.db.flush()

        return {
            "visual_match_id": match.id,
            "selected_product": self._serialize_product(product),
            "selected_background": (
                BackgroundService.serialize(background) if background else None
            ),
            "preview_config": preview_config,
        }

    def _build_preview_config(self, session: Session, product: Product, background) -> dict:
        asset = next(
            (a for a in product.visual_assets if a.is_active),
            None,
        )
        colors_sorted = sorted(product.product_colors, key=lambda pc: pc.color_rank)
        dominant_hex = None
        if asset and asset.dominant_color_hex:
            dominant_hex = asset.dominant_color_hex
        elif colors_sorted:
            dominant_hex = colors_sorted[0].color.hex_code

        color_roles: dict = {}
        for pc in colors_sorted:
            role = (pc.color_role or "").lower()
            if role and role not in color_roles:
                color_roles[role] = pc.color.hex_code

        garment_type = self._garment_type(product)
        face_anchor = None
        if asset and asset.anchor_config:
            face_anchor = asset.anchor_config
        if face_anchor is None:
            face_anchor = DEFAULT_FACE_ANCHORS.get(garment_type, DEFAULT_FACE_ANCHORS[GARMENT_GAMIS])

        return {
            "mode": "VIRTUAL_TRY_ON",
            "garment_type": garment_type,
            "skin_hex": self._skin_hex(session),
            "product_photo_url": asset.asset_url if asset else product.image_url,
            "face_anchor": face_anchor,
            "product_asset_url": asset.asset_url if asset else product.image_url,
            "product_asset_type": asset.asset_type if asset else "IMAGE",
            "dominant_color_hex": dominant_hex,
            "color_roles": color_roles,
            "palette": [pc.color.hex_code for pc in colors_sorted],
            "background_url": background.image_url if background else None,
        }

    @staticmethod
    def _garment_type(product: Product) -> str:
        """Siluet figur try-on mengikuti jenis produk pada katalog Seera."""
        haystack = product.name.lower()
        if product.category and product.category.name:
            haystack += " " + product.category.name.lower()
        if "hijab" in haystack or "khimar" in haystack or "aksesoris" in haystack:
            return GARMENT_HIJAB
        if "koko" in haystack:
            return GARMENT_KOKO
        if "abaya" in haystack:
            return GARMENT_ABAYA
        if "gamis" in haystack or "dress" in haystack:
            return GARMENT_GAMIS
        return GARMENT_KOKO if product.target_gender == "MALE" else GARMENT_GAMIS

    def _skin_hex(self, session: Session) -> str:
        """Warna kulit figur (leher/tangan) mengikuti hasil analisis foto pengguna."""
        analysis = (
            self.db.query(ImageAnalysisSession)
            .filter(
                ImageAnalysisSession.session_id == session.id,
                ImageAnalysisSession.sample_rgb.isnot(None),
            )
            .order_by(ImageAnalysisSession.id.desc())
            .first()
        )
        if analysis and analysis.sample_rgb:
            try:
                r, g, b = (int(v) for v in analysis.sample_rgb.split(","))
                return "#{:02X}{:02X}{:02X}".format(r, g, b)
            except ValueError:
                pass
        if session.skintone_snapshot is not None:
            return FITZPATRICK_HEX.get(float(session.skintone_snapshot), DEFAULT_SKIN_HEX)
        return DEFAULT_SKIN_HEX

    @staticmethod
    def _serialize_product(product: Product) -> dict:
        colors_sorted = sorted(product.product_colors, key=lambda pc: pc.color_rank)
        return {
            "product_id": product.id,
            "product_name": product.name,
            "price": float(product.price),
            "rating": float(product.rating) if product.rating is not None else None,
            "image_url": product.image_url,
            "colors": [
                {
                    "color_name": pc.color.color_name,
                    "hex_code": pc.color.hex_code,
                    "color_role": pc.color_role,
                }
                for pc in colors_sorted
            ],
        }
