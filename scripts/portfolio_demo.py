#!/usr/bin/env python3
"""Reproducible synthetic demo of the individual-vs-portfolio aggregation effect.

This is the headline demonstration behind the article "The signal is
collective". It builds a synthetic universe of N noisy strategies — each one
indistinguishable from a coin flip on its own — then constructs random
portfolios of size k from that pool and shows the resulting Sharpe-ratio
distribution at both levels of aggregation.

Output:
  figures/individual_vs_portfolio.png
  figures/individual_vs_portfolio.pdf
  individual_vs_portfolio.json   compact summary consumed by tests / external sites

The article on the live site walks through the same effect on the real
strategy universe; this demo shows the form of the result with no proprietary
data attached.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


def synthetic_universe(
    n_strategies: int = 30_000,
    n_windows: int = 60,
    sigma_strategy: float = 0.04,   # per-strategy mean Sharpe spread
    rho: float = 0.05,              # cross-strategy correlation
    seed: int = 2026,
) -> np.ndarray:
    """Per-window per-strategy returns matrix R ∈ ℝ^{T × N}.

    Each strategy's per-window return is drawn from a mean-zero Gaussian with
    a small positive expected mean Sharpe (σ_strategy) and a mild common-factor
    component (rho). The marginal mean Sharpe is therefore noise-like — most
    strategies look indistinguishable from random under a per-strategy test.
    """
    rng = np.random.default_rng(seed)
    common = rng.standard_normal((n_windows, 1))
    idio   = rng.standard_normal((n_windows, n_strategies))
    R = np.sqrt(rho) * common + np.sqrt(1 - rho) * idio
    drift = rng.standard_normal((1, n_strategies)) * sigma_strategy
    return R + drift


def per_strategy_sharpe(R: np.ndarray) -> np.ndarray:
    """Mean / std of each column — the classical Sharpe estimator on returns."""
    mu  = R.mean(axis=0)
    sig = R.std(axis=0, ddof=1).clip(1e-12)
    return mu / sig


def random_portfolio_sharpes(
    R: np.ndarray, n_portfolios: int, k: int, rng: np.random.Generator
) -> np.ndarray:
    """For each portfolio, pick k strategies uniformly at random and compute
    the equal-weighted portfolio Sharpe over the same window grid."""
    T, N = R.shape
    out = np.empty(n_portfolios)
    for p in range(n_portfolios):
        idx = rng.choice(N, size=k, replace=False)
        w = R[:, idx].mean(axis=1)
        out[p] = w.mean() / max(w.std(ddof=1), 1e-12)
    return out


def plot_two_densities(individual: np.ndarray, portfolio: np.ndarray,
                       k: int, n_portfolios: int, out: Path) -> None:
    """Two overlaid KDE-ish histograms — the headline figure."""
    fig, ax = plt.subplots(figsize=(8.5, 4.6))
    bins = np.linspace(min(individual.min(), portfolio.min()) - 0.05,
                       max(individual.max(), portfolio.max()) + 0.05, 80)
    ax.hist(individual, bins=bins, density=True, alpha=0.45,
            color="#e0625d", edgecolor="white", linewidth=0.4,
            label=f"individual strategies (n = {len(individual):,})")
    ax.hist(portfolio, bins=bins, density=True, alpha=0.65,
            color="#b6ff4a", edgecolor="white", linewidth=0.4,
            label=f"random portfolios of k = {k}  (n = {n_portfolios:,})")
    ax.axvline(0, color="#333", linewidth=0.5, linestyle="-")
    ax.axvline(individual.mean(), color="#a23c38", linewidth=1.4, linestyle="--",
               label=f"individual mean = {individual.mean():+.3f}")
    ax.axvline(portfolio.mean(), color="#5a8530", linewidth=1.4, linestyle="--",
               label=f"portfolio mean = {portfolio.mean():+.3f}")
    ax.set_xlabel("Sharpe ratio")
    ax.set_ylabel("density")
    ax.set_title("Individual vs. portfolio Sharpe — synthetic strategy universe")
    ax.legend(loc="upper left", frameon=False, fontsize=10)
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    fig.savefig(out, dpi=160)
    fig.savefig(out.with_suffix(".pdf"))
    print(f"  wrote {out}")
    print(f"  wrote {out.with_suffix('.pdf')}")


def main() -> None:
    ap = argparse.ArgumentParser(
        description="Synthetic demo of the individual-vs-portfolio aggregation effect."
    )
    ap.add_argument("--n-strategies", type=int, default=30_000,
                    help="number of synthetic strategies in the pool (default 30 000).")
    ap.add_argument("--n-windows", type=int, default=60,
                    help="window-level return observations per strategy (default 60).")
    ap.add_argument("--n-portfolios", type=int, default=10_000,
                    help="number of random portfolios to draw (default 10 000).")
    ap.add_argument("--k", type=int, default=50,
                    help="portfolio size, in strategies (default 50).")
    ap.add_argument("--seed", type=int, default=2026)
    ap.add_argument("--out", type=Path,
                    default=Path(__file__).resolve().parent.parent / "figures",
                    help="output directory for figures.")
    args = ap.parse_args()

    args.out.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(args.seed)

    R = synthetic_universe(
        n_strategies=args.n_strategies,
        n_windows=args.n_windows,
        seed=args.seed,
    )
    individual = per_strategy_sharpe(R)
    portfolio  = random_portfolio_sharpes(R, args.n_portfolios, args.k, rng)

    plot_two_densities(individual, portfolio, args.k, args.n_portfolios,
                       args.out / "individual_vs_portfolio.png")

    summary = {
        "n_strategies":   int(args.n_strategies),
        "n_windows":      int(args.n_windows),
        "n_portfolios":   int(args.n_portfolios),
        "k":              int(args.k),
        "seed":           int(args.seed),
        "individual_mean": round(float(individual.mean()), 6),
        "individual_std":  round(float(individual.std(ddof=1)), 6),
        "individual_q05":  round(float(np.quantile(individual, 0.05)), 6),
        "individual_q95":  round(float(np.quantile(individual, 0.95)), 6),
        "portfolio_mean":  round(float(portfolio.mean()), 6),
        "portfolio_std":   round(float(portfolio.std(ddof=1)), 6),
        "portfolio_q05":   round(float(np.quantile(portfolio, 0.05)), 6),
        "portfolio_q95":   round(float(np.quantile(portfolio, 0.95)), 6),
    }
    out_json = args.out.parent / "individual_vs_portfolio.json"
    out_json.write_text(json.dumps(summary, indent=2))
    print(f"  wrote {out_json}")
    print(f"  individual mean Sharpe ≈ {summary['individual_mean']:+.3f}  "
          f"portfolio mean Sharpe ≈ {summary['portfolio_mean']:+.3f}")


if __name__ == "__main__":
    main()
