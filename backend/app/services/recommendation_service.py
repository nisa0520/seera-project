"""Recommendation generation: ties FIS Layer 1, Layer 2, ROC, ranking, and persistence."""
from typing import Optional
from sqlalchemy.orm import Session as DBSession
from sqlalchemy import select

from app.models.session import Session
from app.models.product import Product
from app.models.product_color import ProductColor
from app.models.color import Color
from app.models.seasonal_result import SeasonalResult
from app.models.recommendation import Recommendation
from app.models.recommendation_item import RecommendationItem
from app.models.color_match_score import ColorMatchScore
from app.models.product_match_filter import ProductMatchFilter

from app.services.seasonal_classifier import classify
from app.services.color_match_service import compute_color_score, LABEL_INDONESIAN, label_for_score
from app.services.product_ranker import aggregate_product_score, sort_items
from app.core.exceptions import RecommendationNotFoundError


ROLE_ORDER = {"DOMINANT": 0, "SECONDARY": 1, "MOTIF": 2, "ACCENT": 3}


class RecommendationService:
    def __init__(self, db: DBSession):
        self.db = db

    def classify_seasonal(self, session: Session, skin_tone_value: float, undertone_value: float) -> SeasonalResult:
        result = classify(skin_tone_value, undertone_value)
        sc = session.skin_characteristic
        sr = SeasonalResult(
            skin_characteristic_id=sc.id,
            user_id=session.user_id,
            seasonal_code=result["seasonal_code"],
            seasonal_name=result["seasonal_name"],
            y1_continuous=result["y1_continuous"],
            score_seasonal=result["score_seasonal"],
            seasonal_membership=result["seasonal_membership"],
            fired_rules=result["fired_rules"],
        )
        self.db.add(sr)
        self.db.flush()

        session.y1_continuous = result["y1_continuous"]
        session.seasonal_type_name = result["seasonal_name"]
        self.db.flush()

        return sr

    def _available_products(self) -> list[Product]:
        stmt = select(Product).where(Product.is_active.is_(True), Product.stock > 0)
        return list(self.db.execute(stmt).scalars().all())

    def generate_recommendation(self, session: Session, seasonal_result: SeasonalResult, top_n: int = 5) -> dict:
        recommendation = Recommendation(
            session_id=session.id,
            user_id=session.user_id,
            top_n=top_n,
        )
        self.db.add(recommendation)
        self.db.flush()

        products = self._available_products()
        all_match_filters = []
        ranking_rows: list[dict] = []

        for product in products:
            colors_sorted = sorted(product.product_colors, key=lambda pc: pc.color_rank)
            if not colors_sorted:
                continue

            color_scores_payload = []
            y2_values = []
            for pc in colors_sorted:
                color = pc.color
                ct = float(color.ct)
                cb = float(color.cb)
                result = compute_color_score(ct, cb, seasonal_result.seasonal_membership)

                cms = ColorMatchScore(
                    seasonal_result_id=seasonal_result.id,
                    product_color_id=pc.id,
                    user_id=session.user_id,
                    color_id=color.id,
                    match_color_name=color.color_name,
                    hex_code=color.hex_code,
                    ct=ct,
                    cb=cb,
                    suitable_score_color=result["y2"],
                    suitability_label=result["label"],
                    ct_membership=result["ct_membership"],
                    cb_membership=result["cb_membership"],
                    fired_rules=result["fired_rules"],
                )
                self.db.add(cms)
                color_scores_payload.append({
                    "product_color_id": pc.id,
                    "color_name": color.color_name,
                    "hex_code": color.hex_code,
                    "ct": ct,
                    "cb": cb,
                    "y2": result["y2"],
                    "label": result["label"],
                    "label_indonesian": result["label_indonesian"],
                    "color_role": pc.color_role,
                    "color_rank": pc.color_rank,
                })
                y2_values.append(result["y2"])

            aggregated = aggregate_product_score(y2_values)
            weights = aggregated["weights"]

            # map per role
            role_to_roc = {"DOMINANT": None, "SECONDARY": None, "MOTIF": None, "ACCENT": None}
            for pc, w in zip(colors_sorted, weights):
                if pc.color_role in role_to_roc:
                    role_to_roc[pc.color_role] = float(w)

            pmf = ProductMatchFilter(
                product_id=product.id,
                seasonal_result_id=seasonal_result.id,
                recommendation_id=recommendation.id,
                match_product_name=product.name,
                amount_color=aggregated["amount_color"],
                dominant_roc=role_to_roc["DOMINANT"],
                secondary_roc=role_to_roc["SECONDARY"],
                motif_roc=role_to_roc["MOTIF"],
                accent_roc=role_to_roc["ACCENT"],
                total_roc_score=aggregated["total_roc_score"],
                suitability_label=aggregated["label"],
            )
            self.db.add(pmf)
            self.db.flush()
            all_match_filters.append(pmf)

            # add roc weights into color payload (aligned with sorted ranks)
            for idx, pc_payload in enumerate(color_scores_payload):
                pc_payload["roc_weight"] = float(weights[idx]) if idx < len(weights) else 0.0

            ranking_rows.append({
                "product_id": product.id,
                "product_name": product.name,
                "price_snapshot": float(product.price),
                "rating_snapshot": float(product.rating) if product.rating is not None else None,
                "stock_snapshot": product.stock,
                "popularity": product.popularity,
                "product_score": float(aggregated["total_roc_score"]),
                "label": aggregated["label"],
                "label_indonesian": aggregated["label_indonesian"],
                "product_match_filter_id": pmf.id,
                "image_url": product.image_url,
                "colors": color_scores_payload,
            })

        # Tie-break: score desc, rating desc, price asc, name asc
        sorted_rows = sort_items(ranking_rows, "SCORE_DESC")

        items = []
        top_rows = sorted_rows[:top_n]
        for rank, row in enumerate(top_rows, start=1):
            item = RecommendationItem(
                recommendation_id=recommendation.id,
                product_id=row["product_id"],
                product_match_filter_id=row["product_match_filter_id"],
                rank_number=rank,
                product_score=row["product_score"],
                product_rank_label=row["label"],
                price_snapshot=row["price_snapshot"],
                rating_snapshot=row["rating_snapshot"],
                stock_snapshot=row["stock_snapshot"],
            )
            self.db.add(item)
            items.append({**row, "rank": rank})

        session.recommendation_id = recommendation.id
        self.db.flush()

        return {
            "recommendation": recommendation,
            "items": items,
            "all_ranked": sorted_rows,
        }

    def get_latest_recommendation(self, session: Session) -> Recommendation:
        rec = (
            self.db.query(Recommendation)
            .filter(Recommendation.session_id == session.id)
            .order_by(Recommendation.id.desc())
            .first()
        )
        if not rec:
            raise RecommendationNotFoundError()
        return rec

    def serialize_recommendation_items(self, recommendation: Recommendation) -> list[dict]:
        items_out = []
        for item in sorted(recommendation.items, key=lambda x: x.rank_number):
            product = item.product
            colors = []
            for pc in sorted(product.product_colors, key=lambda x: x.color_rank):
                cms = (
                    self.db.query(ColorMatchScore)
                    .filter(
                        ColorMatchScore.product_color_id == pc.id,
                        ColorMatchScore.seasonal_result_id
                        == item.product_match_filter.seasonal_result_id,
                    )
                    .first()
                )
                if cms:
                    colors.append({
                        "color_name": cms.match_color_name,
                        "hex_code": cms.hex_code,
                        "ct": float(cms.ct),
                        "cb": float(cms.cb),
                        "y2": float(cms.suitable_score_color),
                        "label": cms.suitability_label,
                        "label_indonesian": LABEL_INDONESIAN.get(cms.suitability_label, ""),
                        "color_role": pc.color_role,
                        "color_rank": pc.color_rank,
                    })
            items_out.append({
                "rank": item.rank_number,
                "product_id": product.id,
                "product_name": product.name,
                "price": float(item.price_snapshot),
                "rating": float(item.rating_snapshot) if item.rating_snapshot is not None else None,
                "stock": item.stock_snapshot,
                "popularity": product.popularity,
                "image_url": product.image_url,
                "product_score": float(item.product_score),
                "label": item.product_rank_label,
                "label_indonesian": LABEL_INDONESIAN.get(item.product_rank_label or "", ""),
                "product_match_filter_id": item.product_match_filter_id,
                "colors": colors,
            })
        return items_out

    def reorder_items(self, recommendation: Recommendation, criteria: str) -> list[dict]:
        items_serialized = self.serialize_recommendation_items(recommendation)
        # Normalize keys to be compatible with sort_items
        for item in items_serialized:
            item["product_score"] = float(item["product_score"])
            item["price_snapshot"] = float(item["price"])
            item["rating_snapshot"] = item["rating"]
        sorted_items = sort_items(items_serialized, criteria)
        new_items = []
        for idx, item in enumerate(sorted_items, start=1):
            item["rank"] = idx
            new_items.append(item)
        return new_items

    def colors_to_avoid(self, recommendation: Recommendation) -> list[dict]:
        seasonal_result_id = None
        if recommendation.product_match_filters:
            seasonal_result_id = recommendation.product_match_filters[0].seasonal_result_id
        else:
            raise RecommendationNotFoundError()

        cms_rows = (
            self.db.query(ColorMatchScore)
            .filter(
                ColorMatchScore.seasonal_result_id == seasonal_result_id,
                ColorMatchScore.suitability_label.in_(["LESS_SUITABLE", "NOT_SUITABLE"]),
            )
            .all()
        )

        # Deduplicate by hex_code, pick worst score per color
        unique = {}
        for cms in cms_rows:
            existing = unique.get(cms.hex_code)
            if not existing or float(cms.suitable_score_color) < float(existing.suitable_score_color):
                unique[cms.hex_code] = cms

        result = []
        for cms in unique.values():
            label_idn = LABEL_INDONESIAN.get(cms.suitability_label, "")
            reason = self._reason_for_color(cms)
            result.append({
                "color_name": cms.match_color_name,
                "hex_code": cms.hex_code,
                "ct": float(cms.ct),
                "cb": float(cms.cb),
                "y2": float(cms.suitable_score_color),
                "label": cms.suitability_label,
                "label_indonesian": label_idn,
                "reason": reason,
            })
        # sort by y2 ascending so worst first
        result.sort(key=lambda x: x["y2"])
        return result

    @staticmethod
    def _reason_for_color(cms: ColorMatchScore) -> str:
        ct = float(cms.ct)
        cb = float(cms.cb)
        ct_label = "warm" if ct > 1.2 else ("cool" if ct < 0.8 else "neutral")
        cb_label = "light" if cb > 0.6 else ("dark" if cb < 0.3 else "medium")
        return (
            f"Warna ini cenderung {ct_label} dan {cb_label}, "
            f"kurang cocok dengan profil personal color Anda."
        )
