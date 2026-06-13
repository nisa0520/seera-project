from app.services.product_ranker import roc_weights, aggregate_product_score


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
    # Per PRD: ~0.674
    assert abs(result["total_roc_score"] - 0.674) < 0.01
