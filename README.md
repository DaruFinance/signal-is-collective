# signal-is-collective

**Reproducible synthetic demos behind the article _"The signal is collective"_.**

> Reproducible demos for [The signal is collective](https://daru.finance/projects/signal-is-collective), an article by Daniel Gatto on [daru.finance](https://daru.finance).

The article (live at the portfolio site) defends the claim that signal at the
individual-strategy level and signal at the portfolio level are mathematically
distinct objects: across ≈360 000 strategy configurations on nine instruments,
every per-strategy multiple-testing procedure returns noise, while a fixed
portfolio-construction pipeline run on the same population produces stable
positive aggregate outcomes regime after regime.

This repository ships the **synthetic demonstrations** of the same effect — no
proprietary strategy data is included. The demos reproduce the qualitative
shape of the article's headline figure (individual Sharpe density vs. portfolio
Sharpe density on the same pool) on a deterministic synthetic universe, which
anyone can run with a single command.

## Reproduce

```bash
git clone https://github.com/DaruFinance/signal-is-collective
cd signal-is-collective
pip install -e .
python scripts/portfolio_demo.py
```

That writes `figures/individual_vs_portfolio.{png,pdf}` and
`individual_vs_portfolio.json` next to it. The script is reproducible
(seed = 2026 by default) and takes <30 s on a laptop.

## What the demo shows

* `synthetic_universe` builds a pool of 30 000 noisy strategies with a small
  cross-strategy common factor and a mild per-strategy drift. Each individual
  Sharpe is statistically indistinguishable from zero — a per-strategy
  selection rule is hopeless.
* `random_portfolio_sharpes` draws 10 000 equal-weighted portfolios of `k`
  strategies from the same pool and computes the portfolio-level Sharpe.
* The headline plot overlays the two densities. The individual density is
  centred near zero; the portfolio density is shifted to the right and
  visibly narrower — the variance-reduction effect of aggregation.

The synthetic universe deliberately has very weak per-strategy drift (the
"noise dominates" regime), so the gap between the two distributions is
attributable purely to aggregation, not to a hand-tuned signal.

## Why a separate repo

The article on the live site uses real strategy data that lives in private
research directories. This repository captures the **public, redistributable
half** of the article — the deterministic synthetic counter-demo that lets
any reader audit the form of the claim without access to the original
backtests. It complements the project repositories
(`strategy-rmt`, `strategy-tda`, `tail-evt`, `hc-knockoffs`, `strategy-stats`,
`strategy-corrcube`), which each ship a synthetic demo of one estimator;
this repo's demo composes the result *across* estimators by aggregating into
portfolios.

## Citation

> Gatto, D. V. (2026). _The signal is collective: an aggregation hypothesis
> on a 360 000-strategy universe._ Online article and synthetic demonstration
> repository. https://github.com/DaruFinance/signal-is-collective

## License

MIT — see [`LICENSE`](LICENSE).
