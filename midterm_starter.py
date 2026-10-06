import gc
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

SIZES = [250, 500, 1000, 1500, 2000, 3000, 4000, 5000]
TRIALS = 7
SEED = 202


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


def benchmark(sizes=SIZES, trials=TRIALS, seed=SEED):
    """
    Time both algorithms on the same worst-case inputs across several sizes.
    Returns {algorithm name: [median seconds for each n in sizes]}.
    """
    random.seed(seed)
    algorithms = {
        "find_duplicates_slow (O(n^2))": find_duplicates_slow,
        "find_duplicates_fast (O(n))": find_duplicates_fast,
    }
    results = {name: [] for name in algorithms}

    # Warm-up run so first-call overhead does not land in the smallest size.
    warmup = make_input(100)
    for func in algorithms.values():
        func(warmup)

    gc_was_enabled = gc.isenabled()
    gc.disable()
    try:
        for n in sizes:
            per_algo = {name: [] for name in algorithms}
            for trial in range(trials):
                data = make_input(n)
                # Alternate the order each trial so neither algorithm always
                # benefits from a warmer cache.
                order = list(algorithms.items())
                if trial % 2:
                    order.reverse()
                for name, func in order:
                    per_algo[name].append(time_once(func, data))
            for name in algorithms:
                results[name].append(statistics.median(per_algo[name]))
            print(f"n={n:>6}  " + "  ".join(
                f"{name.split()[0]}={results[name][-1]:.6f}s" for name in algorithms))
    finally:
        if gc_was_enabled:
            gc.enable()

    return results


def plot_results(sizes, results, path="results.png"):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import matplotlib.ticker

    fig, (ax_lin, ax_log) = plt.subplots(1, 2, figsize=(12, 5))
    markers = ["o", "s"]

    for (name, times), marker in zip(results.items(), markers):
        ax_lin.plot(sizes, times, marker=marker, label=name)
        ax_log.loglog(sizes, times, marker=marker, label=name)

    # Reference slopes anchored at the largest n make the growth rate easy to read.
    n0 = sizes[-1]
    slow_t0, fast_t0 = (times[-1] for times in results.values())
    ax_log.loglog(sizes, [slow_t0 * (n / n0) ** 2 for n in sizes],
                  "k--", alpha=0.5, label="reference slope 2 (n^2)")
    ax_log.loglog(sizes, [fast_t0 * (n / n0) for n in sizes],
                  "k:", alpha=0.5, label="reference slope 1 (n)")

    ax_lin.set_title("Runtime vs. input size (linear scale)")
    ax_log.set_title("Runtime vs. input size (log-log scale)")
    for ax in (ax_lin, ax_log):
        ax.set_xlabel("Input size n (number of elements)")
        ax.set_ylabel(f"Median runtime over {TRIALS} trials (seconds)")
        ax.grid(True, which="both", alpha=0.3)
        ax.legend()
    ax_log.set_xticks([250, 500, 1000, 2000, 5000])
    ax_log.xaxis.set_major_formatter(matplotlib.ticker.ScalarFormatter())
    ax_log.xaxis.set_minor_formatter(matplotlib.ticker.NullFormatter())

    fig.suptitle("Duplicate detection: worst-case input (no duplicates)")
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    print(f"Saved plot to {path}")


if __name__ == "__main__":
    results = benchmark()
    plot_results(SIZES, results)