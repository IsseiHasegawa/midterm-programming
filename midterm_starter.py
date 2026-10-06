import gc
import math
import statistics
import time
import random

# =======================================================
# DO NOT MODIFY THE ALGORITHM IMPLEMENTATIONS
# =======================================================

def find_duplicates_slow(data):
    """An O(n^2) algorithm to find duplicates."""
    n = len(data)
    for i in range(n):
        for j in range(i + 1, n):
            if data[i] == data[j]:
                return True
    return False

def find_duplicates_fast(data):
    """An O(n) algorithm to find duplicates."""
    seen = set()
    for item in data:
        if item in seen:
            return True
        seen.add(item)
    return False


# =======================================================
# YOUR TASK: FIX THE BENCHMARKING SCRIPT BELOW
# =======================================================

# Doubling sizes so each step should multiply the time by about 4 for O(n^2)
# and about 2 for O(n). The slow algorithm stops at MAX_SLOW_SIZE because
# n^2 growth makes larger sizes take too long; the fast one keeps going so its
# linear growth is shown over a much wider range.
SIZES = [250, 500, 1000, 2000, 4000, 8000, 16000, 32000, 64000, 128000]
MAX_SLOW_SIZE = 8000
TRIALS = 7
SEED = 202

SLOW = "find_duplicates_slow"
FAST = "find_duplicates_fast"
ALGORITHMS = {SLOW: find_duplicates_slow, FAST: find_duplicates_fast}
MAX_SIZE = {SLOW: MAX_SLOW_SIZE, FAST: max(SIZES)}
EXPECTED = {SLOW: "O(n^2)", FAST: "O(n)"}
EXPECTED_SLOPE = {SLOW: 2, FAST: 1}


def make_input(n):
    # No duplicates is the worst case for both algorithms: neither can return
    # early, so the timing reflects the full O(n^2) / O(n) work.
    data = random.sample(range(10 * n), n)
    assert len(set(data)) == n
    return data


def time_once(func, data):
    # Copy outside the timed region so both algorithms see identical input
    # and the copy cost is not measured.
    data = list(data)
    start = time.perf_counter()
    func(data)
    return time.perf_counter() - start


def fit_slope(sizes, times):
    """Least-squares slope of log(time) vs. log(n), i.e. the k in time ~ n^k."""
    xs = [math.log(n) for n in sizes]
    ys = [math.log(t) for t in times]
    x_mean = statistics.fmean(xs)
    y_mean = statistics.fmean(ys)
    num = sum((x - x_mean) * (y - y_mean) for x, y in zip(xs, ys))
    den = sum((x - x_mean) ** 2 for x in xs)
    return num / den


def flawed_benchmark(sizes=SIZES, trials=TRIALS, seed=SEED):
    """
    Time both algorithms on the same worst-case inputs across several sizes.
    Returns {algorithm name: {"sizes": [...], "times": [median seconds], "slope": k}}.
    """
    random.seed(seed)
    results = {name: {"sizes": [], "times": []} for name in ALGORITHMS}

    # Warm-up run so first-call overhead does not land in the smallest size.
    warmup = make_input(100)
    for func in ALGORITHMS.values():
        func(warmup)

    gc_was_enabled = gc.isenabled()
    gc.disable()
    try:
        for n in sizes:
            active = [name for name in ALGORITHMS if n <= MAX_SIZE[name]]
            per_algo = {name: [] for name in active}
            for trial in range(trials):
                data = make_input(n)
                # Alternate the order each trial so neither algorithm always
                # benefits from a warmer cache.
                order = active if trial % 2 == 0 else active[::-1]
                for name in order:
                    per_algo[name].append(time_once(ALGORITHMS[name], data))
            for name in active:
                results[name]["sizes"].append(n)
                results[name]["times"].append(statistics.median(per_algo[name]))
            print(f"n={n:>7}  " + "  ".join(
                f"{name}={results[name]['times'][-1]:.6f}s" for name in active))
    finally:
        if gc_was_enabled:
            gc.enable()

    print()
    for name, r in results.items():
        r["slope"] = fit_slope(r["sizes"], r["times"])
        print(f"{name}: log-log slope = {r['slope']:.2f} "
              f"(expected about {EXPECTED_SLOPE[name]} for {EXPECTED[name]})")

    return results


def plot_results(results, path="results.png"):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import matplotlib.ticker

    fig, (ax_lin, ax_log) = plt.subplots(1, 2, figsize=(13, 5.5))
    markers = {SLOW: "o", FAST: "s"}
    colors = {SLOW: "tab:blue", FAST: "tab:orange"}

    # On a linear axis the fast algorithm's extra sizes would squash the slow
    # curve into the corner, so the linear plot only covers the shared sizes.
    for name, r in results.items():
        shared = [(n, t) for n, t in zip(r["sizes"], r["times"]) if n <= MAX_SLOW_SIZE]
        ax_lin.plot(*zip(*shared), marker=markers[name], color=colors[name],
                    label=f"{name} ({EXPECTED[name]})")
        ax_log.loglog(r["sizes"], r["times"], marker=markers[name], color=colors[name],
                      label=f"{name} ({EXPECTED[name]}), fitted slope = {r['slope']:.2f}")

    # Reference lines anchored at each algorithm's largest n.
    for name, style in ((SLOW, "k--"), (FAST, "k:")):
        power = EXPECTED_SLOPE[name]
        label = f"reference slope {power} ({'n^2' if power == 2 else 'n'})"
        sizes, times = results[name]["sizes"], results[name]["times"]
        n0, t0 = sizes[-1], times[-1]
        ax_log.loglog(sizes, [t0 * (n / n0) ** power for n in sizes], style,
                      alpha=0.5, label=label)

    ax_lin.set_title(f"Runtime vs. input size, n <= {MAX_SLOW_SIZE} (linear scale)")
    ax_log.set_title("Runtime vs. input size (log-log scale)")
    for ax in (ax_lin, ax_log):
        ax.set_xlabel("Input size n (number of elements)")
        ax.set_ylabel(f"Median runtime over {TRIALS} trials (seconds)")
        ax.grid(True, which="both", alpha=0.3)
        ax.legend(fontsize=9)
    ax_log.xaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda x, _: f"{x:,.0f}"))
    ax_log.xaxis.set_minor_formatter(matplotlib.ticker.NullFormatter())

    fig.suptitle("Duplicate detection: worst-case input (no duplicates)")
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    print(f"Saved plot to {path}")


if __name__ == "__main__":
    results = flawed_benchmark()
    plot_results(results)
