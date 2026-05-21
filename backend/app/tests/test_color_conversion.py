from app.services.color_feature_service import (
    hex_to_rgb,
    rgb_to_hsv,
    hue_to_color_temperature,
    hsv_to_color_brightness,
    compute_color_features,
)


def test_hex_to_rgb_navy():
    assert hex_to_rgb("#1B3A6B") == (27, 58, 107)


def test_rgb_to_hsv_navy():
    h, s, v = rgb_to_hsv(27, 58, 107)
    # H around 215-217 (Python colorsys: 216.75 deg)
    assert 213 <= h <= 219
    assert abs(s - 0.748) < 0.02
    assert abs(v - 0.420) < 0.005


def test_hue_to_ct_blue_range_is_cool():
    # Any hue in 150-270 yields CT in [0, 0.8] (cool side)
    ct = hue_to_color_temperature(216.75, 0.748)
    assert 0 <= ct <= 0.8


def test_hue_to_ct_yellow_range_is_warm():
    ct = hue_to_color_temperature(45.0, 1.0)
    assert ct >= 1.2


def test_v_to_cb_navy():
    assert hsv_to_color_brightness(0.420) == 0.420


def test_compute_features_navy():
    features = compute_color_features("#1B3A6B")
    assert (features["r"], features["g"], features["b"]) == (27, 58, 107)
    # CT for navy lies in the cool band (< 0.8)
    assert 0 <= features["ct"] <= 0.8
    assert abs(features["cb"] - 0.420) < 0.005
