from app.services.color_match_service import compute_color_score
from app.services.seasonal_classifier import classify


def test_summer_navy_color():
    seasonal = classify(2.0, 0.0)
    # Navy Blue per PRD: ct=0.747, cb=0.420
    result = compute_color_score(0.747, 0.420, seasonal["seasonal_membership"])
    # Per PRD test case: Y2 around 0.65
    assert 0.55 < result["y2"] < 0.75
    assert result["label"] in {"SUITABLE", "VERY_SUITABLE"}


def test_spring_warm_light_color():
    seasonal = classify(2.0, 2.0)  # Spring
    # Warm light color: ct=1.7, cb=0.85
    result = compute_color_score(1.7, 0.85, seasonal["seasonal_membership"])
    assert result["y2"] > 0.7
