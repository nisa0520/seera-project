from app.services.fuzzy_membership import triangular, trapezoidal, memberships, CT_SETS, CB_SETS


def test_triangular_peak():
    assert triangular(2.0, 1.3, 2.0, 2.7) == 1.0


def test_triangular_below():
    assert triangular(1.0, 1.3, 2.0, 2.7) == 0.0


def test_trapezoidal_shoulder_low():
    assert trapezoidal(0.0, 0.0, 0.0, 0.5, 0.8) == 1.0


def test_trapezoidal_shoulder_high():
    assert trapezoidal(2.0, 1.2, 1.5, 2.0, 2.0) == 1.0


def test_ct_navy_blue_cool():
    # Per PRD: CT 0.747 Cool ~ 0.177
    mu = memberships(0.747, CT_SETS)
    assert mu["COOL"] > 0
    assert abs(mu["COOL"] - 0.177) < 0.01


def test_ct_navy_blue_neutral():
    mu = memberships(0.747, CT_SETS)
    assert abs(mu["NEUTRAL"] - 0.368) < 0.01


def test_cb_navy_blue_medium():
    # CB 0.420 Medium = 0.600
    mu = memberships(0.420, CB_SETS)
    assert abs(mu["MEDIUM"] - 0.600) < 0.001
