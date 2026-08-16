"""Statistical verification and multiple-testing penalization for The Senate.

Grounding:
Bailey & Lopez de Prado (Notices of the AMS, 2014) — The Deflated Sharpe Ratio.
"""

import math
from statistics import NormalDist
from typing import Dict, Any

EULER_MASCHERONI = 0.5772156649015329


def expected_max_sharpe(n: int) -> float:
    """Expected maximum Sharpe ratio over N pure-noise trials (Bailey & Lopez de Prado 2014)."""
    if n < 2:
        return 0.0
    nd = NormalDist()
    g = EULER_MASCHERONI
    return (1.0 - g) * nd.inv_cdf(1.0 - 1.0 / n) + g * nd.inv_cdf(1.0 - 1.0 / (n * math.e))


def required_t_stat(n: int, alpha: float = 0.05) -> float:
    """Two-sided Bonferroni |t| hurdle holding FWER at alpha across N trials."""
    n = max(int(n), 1)
    return NormalDist().inv_cdf(1.0 - (alpha / 2.0) / n)


def price_n_hurdle(n: int, alpha: float = 0.05, obs_count: int = 0) -> Dict[str, Any]:
    """Compute exact statistical hurdle for a given trial count N."""
    ems = expected_max_sharpe(n)
    t_req = required_t_stat(n, alpha)
    result = {
        "n_trials": n,
        "alpha": alpha,
        "expected_noise_sharpe": round(ems, 3),
        "required_t_stat": round(t_req, 3),
        "required_sharpe_per_obs": None,
        "annualized_sharpe_252": None,
    }
    if obs_count > 0:
        sr_obs = t_req / math.sqrt(obs_count)
        result["required_sharpe_per_obs"] = round(sr_obs, 4)
        result["annualized_sharpe_252"] = round(sr_obs * math.sqrt(252), 3)

    return result
