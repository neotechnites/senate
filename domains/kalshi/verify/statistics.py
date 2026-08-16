"""Statistical verification and multiple-testing penalization for Kalshi Domain Pod.

Implements Bailey & López de Prado (2014) Deflated Sharpe Ratio and Bonferroni hurdles
for local domain strategy research.
"""

import math
from dataclasses import dataclass
from typing import Optional


@dataclass
class HurdleResult:
    n_trials: int
    alpha: float
    bonferroni_t_hurdle: float
    expected_max_noise_sharpe: float
    description: str


def standard_normal_cdf(x: float) -> float:
    """Compute CDF of standard normal distribution using error function."""
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def standard_normal_quantile(p: float) -> float:
    """Compute quantile function (inverse CDF) for standard normal distribution.
    
    Uses rational approximation algorithm (Acklam).
    """
    if p <= 0.0 or p >= 1.0:
        raise ValueError("Quantile probability must be strictly between 0 and 1.")

    a = [-3.969683028665376e01, 2.209460984245205e02, -2.759285104469687e02, 1.383577518672690e02, -3.066479806614716e01, 2.506628277459239e00]
    b = [-5.447609879822406e01, 1.615858368580409e02, -1.556989798598866e02, 6.680131188771972e01, -1.328068155288572e01]
    c = [-7.784894002430293e-03, -3.223964580411365e-01, -2.400758277161838e00, -2.549732539343734e00, 4.374664141464968e00, 2.938163982698783e00]
    d = [7.784695709041462e-03, 3.224671290700398e-01, 2.445134137142996e00, 3.754408661907416e00]

    q_low = 0.02425
    q_high = 1.0 - q_low

    if p < q_low:
        q = math.sqrt(-2.0 * math.log(p))
        return (((((c[0]*q + c[1])*q + c[2])*q + c[3])*q + c[4])*q + c[5]) / ((((d[0]*q + d[1])*q + d[2])*q + d[3])*q + 1.0)
    elif p <= q_high:
        q = p - 0.5
        r = q * q
        return (((((a[0]*r + a[1])*r + a[2])*r + a[3])*r + a[4])*r + a[5])*q / (((((b[0]*r + b[1])*r + b[2])*r + b[3])*r + b[4])*r + 1.0)
    else:
        q = math.sqrt(-2.0 * math.log(1.0 - p))
        return -(((((c[0]*q + c[1])*q + c[2])*q + c[3])*q + c[4])*q + c[5]) / ((((d[0]*q + d[1])*q + d[2])*q + d[3])*q + 1.0)


def expected_maximum_sr(n: int, var_sr: float = 1.0) -> float:
    """Expected maximum Sharpe Ratio from N independent false trials with mean 0 and variance var_sr.
    
    Formula: sqrt(var_sr) * ((1 - gamma) * Z^(-1)(1 - 1/N) + gamma * Z^(-1)(1 - 1/(N * e)))
    """
    if n <= 1:
        return 0.0

    euler_gamma = 0.577215664901532860606512090082402431042
    e = math.e

    p1 = 1.0 - 1.0 / n
    p2 = 1.0 - 1.0 / (n * e)

    z1 = standard_normal_quantile(p1)
    z2 = standard_normal_quantile(p2)

    em_sr = math.sqrt(var_sr) * ((1.0 - euler_gamma) * z1 + euler_gamma * z2)
    return em_sr


def price_n_hurdle(n: int, alpha: float = 0.05, obs_count: Optional[int] = None) -> HurdleResult:
    """Calculate required statistical hurdle given N multiple-testing trials."""
    if n < 1:
        n = 1

    adj_alpha = alpha / n
    bonferroni_t = standard_normal_quantile(1.0 - adj_alpha / 2.0)
    noise_sr = expected_maximum_sr(n, var_sr=1.0)

    desc = f"N={n} trials: Bonferroni t-hurdle |t| >= {bonferroni_t:.2f} (E[Max noise Sharpe]={noise_sr:.2f})"
    return HurdleResult(
        n_trials=n,
        alpha=alpha,
        bonferroni_t_hurdle=round(bonferroni_t, 3),
        expected_max_noise_sharpe=round(noise_sr, 3),
        description=desc,
    )
