"""Statistical verification, multiple-testing penalization, and regime clustering for The Senate.

Grounding:
- Bailey & Lopez de Prado (Notices of the AMS, 2014) — The Deflated Sharpe Ratio.
- Cameron, Gelbach & Miller (JBES, 2011) — Robust Inference with Multiway Clustering.
- Constitutional Statement 14: Statistical Power Requires Regime Clustering (K >= 10).
"""

import math
from statistics import NormalDist
from typing import Any, Dict, List, Optional, Tuple

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


def compute_clustered_statistics(cluster_samples: List[List[float]], min_clusters: int = 10) -> Dict[str, Any]:
    """Compute cluster-robust variance and t-statistic across K regime/date clusters (Statement 14).
    
    Statement 14 Invariant: All t-stats and win-rates must be clustered at the regime level.
    Single-regime sample mining is treated as K=1 and strictly rejected.
    """
    k = len(cluster_samples)
    if k == 0:
        return {
            "status": "REJECTED_EMPTY",
            "k_clusters": 0,
            "total_observations": 0,
            "mean": 0.0,
            "clustered_t_stat": 0.0,
            "is_valid_power": False,
            "reason": "Zero clusters provided.",
        }

    # Total observations and cluster means
    total_n = sum(len(c) for c in cluster_samples)
    if total_n == 0:
        return {
            "status": "REJECTED_EMPTY",
            "k_clusters": k,
            "total_observations": 0,
            "mean": 0.0,
            "clustered_t_stat": 0.0,
            "is_valid_power": False,
            "reason": "Clusters contain zero data points.",
        }

    all_values = [x for c in cluster_samples for x in c]
    overall_mean = sum(all_values) / total_n

    # Cluster-level means
    cluster_means = [sum(c) / len(c) if len(c) > 0 else 0.0 for c in cluster_samples]

    if k < min_clusters:
        return {
            "status": "REJECTED_UNDERPOWERED",
            "k_clusters": k,
            "min_required_clusters": min_clusters,
            "total_observations": total_n,
            "mean": round(overall_mean, 4),
            "clustered_t_stat": 0.0,
            "is_valid_power": False,
            "reason": f"INVARIANT_BREACH (Statement 14): Regime cluster count K={k} < {min_clusters}. Intra-day sample mining without distinct regime partitions is strictly forbidden.",
        }

    # Clustered variance: Var(mean) = 1 / (K * (K - 1)) * sum((mean_k - mean_overall)^2)
    mean_of_means = sum(cluster_means) / k
    sum_sq_diff = sum((mk - mean_of_means) ** 2 for mk in cluster_means)
    clustered_variance = sum_sq_diff / (k * (k - 1))
    clustered_se = math.sqrt(clustered_variance) if clustered_variance > 0 else 1e-9

    t_stat = mean_of_means / clustered_se

    return {
        "status": "VERIFIED_POWER",
        "k_clusters": k,
        "total_observations": total_n,
        "mean": round(overall_mean, 4),
        "cluster_mean": round(mean_of_means, 4),
        "clustered_se": round(clustered_se, 4),
        "clustered_t_stat": round(t_stat, 3),
        "is_valid_power": True,
    }


def deflated_sharpe_ratio(
    observed_sr: float,
    n_trials: int,
    var_sr: float = 1.0,
    skewness: float = 0.0,
    kurtosis: float = 3.0,
    obs_count: int = 252,
) -> Dict[str, Any]:
    """Compute the Deflated Sharpe Ratio (DSR) adjusting for multiple testing and non-normality."""
    ems = expected_max_sharpe(n_trials)
    
    # Asymptotic variance of Sharpe ratio under non-normality (Mertens 2002)
    # V(SR) = (1 / T) * (1 + 0.5 * SR^2 - skew * SR + ((kurt - 3) / 4) * SR^2)
    t = max(obs_count, 2)
    sr2 = observed_sr ** 2
    se_sr = math.sqrt(max((1.0 / t) * (1.0 + 0.5 * sr2 - skewness * observed_sr + ((kurtosis - 3.0) / 4.0) * sr2), 1e-9))

    # Standardized test stat vs expected noise Sharpe
    z = (observed_sr - ems) / se_sr
    dsr_pvalue = 1.0 - NormalDist().cdf(z)

    return {
        "observed_sr": round(observed_sr, 3),
        "n_trials": n_trials,
        "expected_noise_sharpe": round(ems, 3),
        "z_score": round(z, 3),
        "dsr_pvalue": round(dsr_pvalue, 4),
        "is_significant_5pct": dsr_pvalue < 0.05,
    }
