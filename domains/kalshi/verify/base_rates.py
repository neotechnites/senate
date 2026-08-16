"""Fundamental Base-Rate and Asymmetric Risk Engine for Kalshi Domain Pod.

INVARIANT: NEVER QUOTE BOOK GEOMETRY AGAINST AN ASYMMETRIC FUNDAMENTAL BASE RATE.
A wide spread or high LIP subsidy is worthless if quoting the wrong side of an 80/20 distribution.
"""

from typing import Any, Dict, Optional, Tuple


# Empirical historical base rates across Kalshi market families
# Sourced from historical election data, Ballotpedia, NOAA, BLS, FOMC archives
HISTORICAL_BASE_RATES: Dict[str, Dict[str, Any]] = {
    # State constitutional amendments and bond measures pass at ~72-78% rate nationally
    "BALLOT_BOND_AND_TAX_CAP": {
        "family": "KXSTATEBALLOTMEASURE",
        "keywords": ["bond", "amendment", "fund", "tax rate", "cultural", "infrastructure", "fire", "emergency", "911"],
        "historical_yes_prob": 0.76,
        "prohibited_sides": ["no"],
        "max_contra_price": 0.35,  # Selling NO at <= 35c on 76% pass rate is strictly toxic
        "rationale": "State ballot bonds and constitutional infrastructure/emergency funds pass at 76% base rate.",
    },
    "BALLOT_GENERAL_AMENDMENT": {
        "family": "KXSTATEBALLOTMEASURE",
        "keywords": ["amendment", "measure", "proposition"],
        "historical_yes_prob": 0.68,
        "prohibited_sides": ["no"],
        "max_contra_price": 0.30,
        "rationale": "General state ballot measures pass at 68% historical base rate.",
    },
    "FED_FUNDS_STABLE_HOLD": {
        "family": "KXFEDFUNDSYEAR",
        "keywords": ["hold", "no change", "neutral"],
        "historical_yes_prob": 0.82,
        "prohibited_sides": ["no"],
        "max_contra_price": 0.25,
        "rationale": "Fed rate inertia base rate favors modal path; tail deviations require explicit macro trigger.",
    },
}


def evaluate_fundamental_base_rate(
    ticker: str,
    side: str,
    price: float,
    market_title: str = "",
    market_subtitle: str = "",
) -> Tuple[bool, Optional[str], Optional[Dict[str, Any]]]:
    """Evaluate if an order proposal conflicts with empirical fundamental base rates.
    
    Returns:
        (is_safe, violation_reason_or_none, matched_base_rate_rule)
    """
    ticker_upper = ticker.upper()
    side_lower = side.lower()
    text_corpus = f"{ticker_upper} {market_title} {market_subtitle}".lower()

    for rule_key, rule in HISTORICAL_BASE_RATES.items():
        family_match = rule["family"] in ticker_upper
        keyword_match = any(kw in text_corpus for kw in rule["keywords"])

        if family_match and keyword_match:
            # Check if side is prohibited under base rate
            if side_lower in rule["prohibited_sides"]:
                # If price is at or below the max contra price (e.g. selling NO cheap against high YES probability)
                if price <= rule["max_contra_price"]:
                    violation = (
                        f"Fundamental Base-Rate Breach ({rule_key}): Quoting '{side_upper}' @ ${price:.2f} "
                        f"in '{ticker}' violates historical base rate (True YES P={rule['historical_yes_prob']:.0%}). "
                        f"Rationale: {rule['rationale']}"
                    ) if (side_upper := side.upper()) else ""
                    return False, violation, rule

    return True, None, None
