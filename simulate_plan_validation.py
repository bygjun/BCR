#!/usr/bin/env python3
"""Virtual simulation to validate EXPERIMENT_PLAN primary hypotheses."""

from __future__ import annotations

from dataclasses import dataclass
import numpy as np


@dataclass
class DatasetSpec:
    name: str
    delta_f1: float
    delta_loc: float
    min_target: float
    rerun_delta: float
    sigma_run: float


def paired_permutation_pvalue(diff: np.ndarray, rng: np.random.Generator, n_perm: int) -> float:
    if diff.size == 0:
        return 1.0
    observed = float(np.mean(diff))
    signs = rng.choice(np.array([-1.0, 1.0]), size=(n_perm, diff.size))
    perm_means = np.mean(signs * diff, axis=1)
    return float(np.mean(np.abs(perm_means) >= abs(observed)))


def bootstrap_ci(diff: np.ndarray, rng: np.random.Generator, n_boot: int) -> tuple[float, float]:
    if diff.size == 0:
        return (0.0, 0.0)
    idx = rng.integers(0, diff.size, size=(n_boot, diff.size))
    means = np.mean(diff[idx], axis=1)
    low = float(np.percentile(means, 2.5))
    high = float(np.percentile(means, 97.5))
    return (low, high)


def simulate_trial(
    specs: list[DatasetSpec],
    seeds: int,
    cost_sd: float,
    rng: np.random.Generator,
    n_perm: int,
    n_boot: int,
    null_mode: bool,
) -> dict[str, float] | None:
    run_diffs = []
    run_loc_diffs = []
    dataset_means = {}
    kept = 0
    total = len(specs) * seeds
    h2_win = 0
    h2_total = 0

    for spec in specs:
        ds = []
        ds_loc = []
        for _ in range(seeds):
            cost_ratio = rng.normal(1.0, cost_sd)
            if cost_ratio < 0.95 or cost_ratio > 1.05:
                continue
            base_delta = 0.0 if null_mode else spec.delta_f1
            base_loc = 0.0 if null_mode else spec.delta_loc
            diff = rng.normal(base_delta, spec.sigma_run)
            loc_diff = rng.normal(base_loc, spec.sigma_run)
            ds.append(diff)
            ds_loc.append(loc_diff)
            run_diffs.append(diff)
            run_loc_diffs.append(loc_diff)
            kept += 1

            if not null_mode:
                bcr_gain = max(rng.normal(base_delta, spec.sigma_run), 1e-4)
                rerun_gain = max(rng.normal(spec.rerun_delta, spec.sigma_run), 1e-4)
                bcr_cost = max(rng.normal(1.20, 0.02), 1.0)
                rerun_cost = max(rng.normal(1.42, 0.04), 1.0)
                if (bcr_cost - 1.0) / bcr_gain < (rerun_cost - 1.0) / rerun_gain:
                    h2_win += 1
                h2_total += 1
        dataset_means[spec.name] = float(np.mean(ds)) if ds else np.nan

    if np.isnan(list(dataset_means.values())).any() or len(run_diffs) < 8:
        return None

    diff_arr = np.array(run_diffs)
    loc_arr = np.array(run_loc_diffs)
    p_h1 = paired_permutation_pvalue(diff_arr, rng, n_perm)
    p_h3 = paired_permutation_pvalue(loc_arr, rng, n_perm)
    ci_h1 = bootstrap_ci(diff_arr, rng, n_boot)
    ci_h3 = bootstrap_ci(loc_arr, rng, n_boot)
    macro_f1 = float(np.mean(list(dataset_means.values())))
    target_pass = all(dataset_means[s.name] >= s.min_target for s in specs)

    return {
        "kept_ratio": kept / total,
        "macro_f1": macro_f1,
        "h1_sig": float(p_h1 < 0.05 and ci_h1[0] > 0.0),
        "h1_target": float(target_pass),
        "h3_sig": float(p_h3 < 0.05 and ci_h3[0] > 0.0),
        "h2_win": (h2_win / h2_total) if h2_total else np.nan,
    }


def aggregate(results: list[dict[str, float]], total_trials: int) -> dict[str, float]:
    if not results:
        return {
            "valid_rate": 0.0,
            "kept_ratio": 0.0,
            "macro_f1": 0.0,
            "h1_power": 0.0,
            "h1_target": 0.0,
            "h3_power": 0.0,
            "h2_win": 0.0,
        }
    h2_values = [r["h2_win"] for r in results if not np.isnan(r["h2_win"])]
    h2_mean = float(np.mean(h2_values)) if h2_values else np.nan
    return {
        "valid_rate": len(results) / total_trials,
        "kept_ratio": float(np.mean([r["kept_ratio"] for r in results])),
        "macro_f1": float(np.mean([r["macro_f1"] for r in results])),
        "h1_power": float(np.mean([r["h1_sig"] for r in results])),
        "h1_target": float(np.mean([r["h1_target"] for r in results])),
        "h3_power": float(np.mean([r["h3_sig"] for r in results])),
        "h2_win": h2_mean,
    }


def run_scenario(
    label: str,
    specs: list[DatasetSpec],
    seeds: int,
    trials: int,
    cost_sd: float,
    n_perm: int,
    n_boot: int,
    null_mode: bool,
) -> tuple[str, dict[str, float]]:
    rng = np.random.default_rng(20260220 + int(cost_sd * 1000) + (100 if null_mode else 0))
    valid = []
    for _ in range(trials):
        out = simulate_trial(specs, seeds, cost_sd, rng, n_perm, n_boot, null_mode)
        if out is not None:
            valid.append(out)
    return label, aggregate(valid, trials)


def format_pct(x: float) -> str:
    if np.isnan(x):
        return "N/A"
    return f"{100.0 * x:5.1f}%"


def print_report(summaries: list[tuple[str, dict[str, float]]]) -> None:
    print("# Virtual Simulation Validation")
    print()
    print("| Scenario | Valid Trials | Cost-Matched Kept | Mean Macro ΔF1 | H1 Sig Rate | H1 Target Pass | H3 Sig Rate | H2 CPG Win Rate |")
    print("|---|---:|---:|---:|---:|---:|---:|---:|")
    for label, s in summaries:
        print(
            f"| {label} | {format_pct(s['valid_rate'])} | {format_pct(s['kept_ratio'])} "
            f"| {s['macro_f1']:.4f} | {format_pct(s['h1_power'])} | {format_pct(s['h1_target'])} "
            f"| {format_pct(s['h3_power'])} | {format_pct(s['h2_win'])} |"
        )


def main() -> None:
    specs = [
        DatasetSpec("HotpotQA", 0.018, 0.035, 0.015, 0.024, 0.007),
        DatasetSpec("2WikiMultiHopQA", 0.017, 0.032, 0.015, 0.023, 0.007),
        DatasetSpec("MuSiQue", 0.012, 0.028, 0.010, 0.017, 0.008),
        DatasetSpec("MultiHop-RAG", 0.016, 0.030, 0.015, 0.022, 0.007),
    ]
    seeds = 5
    trials = 1200
    n_perm = 4000
    n_boot = 4000

    summaries = [
        run_scenario("A. Expected Effect / Stable Cost(sd=0.02)", specs, seeds, trials, 0.02, n_perm, n_boot, False),
        run_scenario("B. Expected Effect / Volatile Cost(sd=0.04)", specs, seeds, trials, 0.04, n_perm, n_boot, False),
        run_scenario("C. Null Effect / Stable Cost(sd=0.02)", specs, seeds, trials, 0.02, n_perm, n_boot, True),
    ]
    print_report(summaries)


if __name__ == "__main__":
    main()
