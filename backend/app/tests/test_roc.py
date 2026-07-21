from app.services.product_ranker import roc_weights, aggregate_product_score, resolve_weights


def test_roc_single():
    assert roc_weights(1) == [1.0]


def test_roc_two():
    weights = roc_weights(2)
    assert abs(weights[0] - 0.75) < 0.001
    assert abs(weights[1] - 0.25) < 0.001


def test_roc_three():
    weights = roc_weights(3)
    assert abs(weights[0] - 0.611) < 0.005
    assert abs(weights[1] - 0.278) < 0.005
    assert abs(weights[2] - 0.111) < 0.005


def test_aggregate_three_colors():
    result = aggregate_product_score([0.603, 0.820, 0.700])
    assert abs(result["total_roc_score"] - 0.674) < 0.01
    assert result["weight_mode"] == "ROC"


def test_aggregate_uses_percentage_mode_when_available():
    # Mode 2 (Persentase Langsung, Persamaan 11): dipakai bila seluruh warna
    # punya persentase pasti, mengesampingkan bobot ROC.
    result = aggregate_product_score([0.514, 0.600], percentages=[75.0, 25.0])
    assert result["weight_mode"] == "PERCENTAGE"
    assert abs(result["weights"][0] - 0.75) < 0.001
    assert abs(result["weights"][1] - 0.25) < 0.001
    expected = 0.75 * 0.514 + 0.25 * 0.600
    assert abs(result["total_roc_score"] - expected) < 0.001


def test_resolve_weights_falls_back_to_roc_when_percentage_missing():
    weights, mode = resolve_weights(3, percentages=[60.0, None, 40.0])
    assert mode == "ROC"
    assert abs(weights[0] - 0.611) < 0.005
