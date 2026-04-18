"""Traducere mărimi tehnice → indicatori economici (EUR / RON)."""

# Tarif industrial mediu pentru energie activă (ipoteză — Europa 2024)
EUR_PER_KWH = 0.15

# Curs RON/EUR aproximativ
RON_PER_EUR = 4.98

# Taxa pe carbon (schema ETS + ipoteză locală pentru industria grea)
RON_PER_TCO2 = 80.0


def kwh_to_eur(kwh):
    """Cost monetar al consumului activ (EUR)."""
    return kwh * EUR_PER_KWH


def kwh_to_ron(kwh):
    return kwh_to_eur(kwh) * RON_PER_EUR


def co2_to_ron(tco2):
    """Cost ecologic (RON) în funcție de emisiile de CO2."""
    return tco2 * RON_PER_TCO2


def reactive_penalty_eur(reactive_kvarh, usage_kwh, pf_threshold=0.92):
    """Estimare grosieră a penalizării pentru factor de putere scăzut.

    Distribuitorii percep o suprataxă de ~5% asupra consumului activ când
    factorul de putere (cosφ) este sub pragul contractual. Aici aproximăm
    cosφ = Usage_kWh / sqrt(Usage_kWh^2 + reactive_kVarh^2).
    """
    import numpy as np
    denom = np.sqrt(usage_kwh ** 2 + reactive_kvarh ** 2)
    pf = np.where(denom > 0, usage_kwh / denom, 1.0)
    under_threshold = pf < pf_threshold
    return kwh_to_eur(usage_kwh) * 0.05 * under_threshold
