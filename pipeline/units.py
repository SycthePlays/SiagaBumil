"""Unit conversions between what a bidan types (Indonesian units) and what the
dataset uses. The web app (web/app.js) does the same math in JavaScript."""

MGDL_PER_MMOL = 18.016  # glucose: 1 mmol/L = 18.016 mg/dL


def mgdl_to_mmol(mgdl: float) -> float:
    return mgdl / MGDL_PER_MMOL


def mmol_to_mgdl(mmol: float) -> float:
    return mmol * MGDL_PER_MMOL


def c_to_f(celsius: float) -> float:
    return celsius * 9 / 5 + 32


def f_to_c(fahrenheit: float) -> float:
    return (fahrenheit - 32) * 5 / 9
