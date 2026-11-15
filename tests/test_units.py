"""Unit conversions used by the web form (mg/dL <-> mmol/L, C <-> F)."""
import pytest

from units import c_to_f, f_to_c, mgdl_to_mmol, mmol_to_mgdl


def test_glucose_known_values():
    assert mgdl_to_mmol(180.16) == pytest.approx(10.0)
    assert mgdl_to_mmol(200) == pytest.approx(11.1, abs=0.01)  # B1 "high" cutoff
    assert mmol_to_mgdl(7.0) == pytest.approx(126.1, abs=0.05)


def test_temperature_known_values():
    assert c_to_f(37) == pytest.approx(98.6)
    assert c_to_f(38) == pytest.approx(100.4)  # fever cutoff
    assert f_to_c(98.6) == pytest.approx(37)


def test_round_trips():
    assert mmol_to_mgdl(mgdl_to_mmol(126)) == pytest.approx(126)
    assert f_to_c(c_to_f(36.5)) == pytest.approx(36.5)
