from app.services.seasonal_classifier import classify
from app.services.fuzzy_membership import (
    non_singleton_fire,
    SKIN_TONE_SETS,
    SKIN_TONE_ORDER,
    UNDERTONE_SETS,
    UNDERTONE_ORDER,
)


def test_fair_cool_summer():
    result = classify(2.0, 0.0)
    assert result["seasonal_code"] == "SUMMER"
    assert result["seasonal_membership"]["SUMMER"] == 1.0


def test_fair_warm_spring():
    result = classify(2.0, 2.0)
    assert result["seasonal_code"] == "SPRING"
    assert result["seasonal_membership"]["SPRING"] == 1.0


def test_brown_warm_autumn_matches_worked_example():
    # Contoh perhitungan Bab IV.2.7.3 Poin 5: Skin Tone Tipe V (Brown) + Undertone Warm
    # -> vektor (Spring, Summer, Autumn, Winter) = (0, 0, 1.000, 0.286).
    result = classify(5.0, 2.0)
    membership = result["seasonal_membership"]
    assert result["seasonal_code"] == "AUTUMN"
    assert membership["SPRING"] == 0.0
    assert membership["SUMMER"] == 0.0
    assert membership["AUTUMN"] == 1.0
    assert abs(membership["WINTER"] - 0.286) < 0.001


def test_brown_cool_winter():
    result = classify(5.0, 0.0)
    assert result["seasonal_code"] == "WINTER"
    assert result["seasonal_membership"]["WINTER"] == 1.0


def test_output_has_no_scalar_y1_artifact():
    result = classify(3.0, 1.0)
    assert "y1_continuous" not in result
    assert set(result["seasonal_membership"].keys()) == {"SPRING", "SUMMER", "AUTUMN", "WINTER"}


def test_non_singleton_fire_skin_tone_brown_matches_table_iv15():
    # Tabel IV.15: fuzzifikasi non-singleton input Brown (Tipe V).
    fires = non_singleton_fire("BROWN", SKIN_TONE_SETS, SKIN_TONE_ORDER)
    assert fires["VERY_FAIR"] == 0.0
    assert fires["FAIR"] == 0.0
    assert fires["MEDIUM_FAIR"] == 0.0
    assert abs(fires["MODERATE_BROWN"] - 0.286) < 0.001
    assert fires["BROWN"] == 1.0
    assert abs(fires["DARK_BROWN"] - 0.364) < 0.001


def test_non_singleton_fire_undertone_warm_matches_table_iv16():
    # Tabel IV.16: fuzzifikasi non-singleton input Warm.
    fires = non_singleton_fire("WARM", UNDERTONE_SETS, UNDERTONE_ORDER)
    assert fires["COOL"] == 0.0
    assert abs(fires["NEUTRAL"] - 0.286) < 0.001
    assert fires["WARM"] == 1.0
