from app.services.seasonal_classifier import classify


def test_fair_cool_summer():
    result = classify(2.0, 0.0)
    assert result["seasonal_code"] == "SUMMER"
    assert abs(result["y1_continuous"] - 1.5) < 0.001


def test_fair_warm_spring():
    result = classify(2.0, 2.0)
    assert result["seasonal_code"] == "SPRING"
    assert abs(result["y1_continuous"] - 0.5) < 0.001


def test_brown_warm_autumn():
    result = classify(5.0, 2.0)
    assert result["seasonal_code"] == "AUTUMN"
    assert abs(result["y1_continuous"] - 2.0) < 0.001


def test_brown_cool_winter():
    result = classify(5.0, 0.0)
    assert result["seasonal_code"] == "WINTER"
    assert abs(result["y1_continuous"] - 2.5) < 0.001
