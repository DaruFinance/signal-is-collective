"""Smoke test: the synthetic demo runs end-to-end and produces a non-empty figure."""
from __future__ import annotations
import json
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPT = REPO_ROOT / "scripts" / "portfolio_demo.py"


def test_synthetic_demo(tmp_path: Path) -> None:
    out = tmp_path / "figures"
    # Smaller-than-default sample for a fast CI smoke test.
    result = subprocess.run(
        [sys.executable, str(SCRIPT),
         "--out", str(out),
         "--n-strategies", "2000",
         "--n-portfolios", "500",
         "--k", "20"],
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
    )
    assert result.returncode == 0, result.stderr

    fig = out / "individual_vs_portfolio.png"
    assert fig.exists(), "demo figure not written"
    assert fig.stat().st_size > 5_000, "demo figure suspiciously small"

    payload = json.loads((out.parent / "individual_vs_portfolio.json").read_text())
    assert payload["n_strategies"] == 2000
    assert payload["k"] == 20
    # Individual Sharpe should be tightly clustered around zero; the portfolio
    # of 20 should have a noticeably tighter spread (variance reduction). We
    # only sanity-check that both summaries are real numbers.
    assert -1.0 < payload["individual_mean"] < 1.0
    assert -1.0 < payload["portfolio_mean"]  < 1.0
    assert payload["portfolio_std"] > 0


if __name__ == "__main__":
    import tempfile
    with tempfile.TemporaryDirectory() as d:
        test_synthetic_demo(Path(d))
        print("ok")
