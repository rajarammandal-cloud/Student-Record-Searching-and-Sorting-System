"""
performance.py
--------------
Empirical performance benchmarking module for DAA algorithms.
Measures real execution times for Linear Search, Binary Search,
Bubble Sort, and Quick Sort across multiple dataset sizes (10, 100, 1000, 5000).
Generates side-by-side Matplotlib visualization charts.
"""

import time
import random
import sys
import os
from typing import List, Dict, Any, Callable, Optional

# Ensure local imports resolve whether executed directly or as a package
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.figure import Figure

from algorithms import linear_search, binary_search, bubble_sort, quick_sort


FIRST_NAMES = [
    "Rahul", "Priya", "Aman", "Neha", "Rohit", "Anjali", "Karan", "Simran",
    "Arjun", "Pooja", "Vikram", "Sneha", "Aditya", "Riya", "Varun", "Divya",
    "Manish", "Kavita", "Suresh", "Tanvi", "Deepak", "Meera", "Gaurav", "Swati"
]

LAST_NAMES = [
    "Sharma", "Verma", "Gupta", "Singh", "Patel", "Kumar", "Mishra", "Joshi",
    "Reddy", "Mehta", "Nair", "Bose", "Chawla", "Yadav", "Malhotra", "Saxena"
]

COURSES = ["MCA", "B.Tech", "M.Tech", "BCA", "M.Sc CS"]


def generate_synthetic_dataset(size: int, seed: Optional[int] = 42) -> List[Dict[str, Any]]:
    """
    Generate a realistic list of synthetic student records.
    Uses distinct roll numbers from 1001 to 1001 + size - 1.
    """
    rng = random.Random(seed + size if seed is not None else None)
    records = []
    rolls = list(range(1001, 1001 + size))
    rng.shuffle(rolls)

    for i in range(size):
        fname = rng.choice(FIRST_NAMES)
        lname = rng.choice(LAST_NAMES)
        records.append({
            "roll_no": rolls[i],
            "name": f"{fname} {lname}",
            "course": rng.choice(COURSES),
            "marks": round(rng.uniform(40.0, 99.5), 1)
        })

    return records


def run_single_size_benchmark(size: int) -> Dict[str, Any]:
    """
    Run benchmarks on an identical dataset for size N.
    Measures:
    - Linear Search time
    - Binary Search time (pure execution time on sorted array)
    - Sorting preparation time for Binary Search
    - Bubble Sort time
    - Quick Sort time
    """
    raw_dataset = generate_synthetic_dataset(size, seed=100)

    # 1. Quick Sort Benchmark
    # Use fresh copy
    qs_data = [dict(r) for r in raw_dataset]
    sorted_by_qs, qs_time, qs_comps, qs_swaps = quick_sort(qs_data, key="roll_no", ascending=True)

    # 2. Bubble Sort Benchmark
    # Use identical fresh copy
    bs_data = [dict(r) for r in raw_dataset]
    sorted_by_bs, bs_time, bs_comps, bs_swaps = bubble_sort(bs_data, key="roll_no", ascending=True)

    # 3. Choose a consistent target for searches (middle element of sorted array for average case)
    target_idx = size // 2
    target_roll = sorted_by_qs[target_idx]["roll_no"]

    # 4. Linear Search Benchmark (on original unsorted dataset)
    # Average across multiple iterations to reduce system noise on small sizes
    search_iterations = 20 if size <= 100 else (5 if size <= 1000 else 2)
    
    lin_times = []
    for _ in range(search_iterations):
        _, _, lin_comps, t_lin = linear_search(raw_dataset, target_roll)
        lin_times.append(t_lin)
    avg_lin_time = sum(lin_times) / len(lin_times)

    # 5. Binary Search Benchmark (pure search on pre-sorted dataset)
    bin_times = []
    # Binary search is extremely fast (sub-microsecond), repeat multiple times for precision
    bin_iterations = 100 if size <= 100 else 20
    for _ in range(bin_iterations):
        _, _, bin_comps, t_bin = binary_search(sorted_by_qs, target_roll)
        bin_times.append(t_bin)
    avg_bin_time = sum(bin_times) / len(bin_times)

    # Sorting prep time for Binary Search (time taken to quicksort the unsorted array)
    binary_prep_time = qs_time

    return {
        "size": size,
        "linear_search_time_sec": avg_lin_time,
        "linear_search_time_us": avg_lin_time * 1e6,  # microseconds
        "linear_search_comps": lin_comps,
        "binary_search_time_sec": avg_bin_time,
        "binary_search_time_us": avg_bin_time * 1e6,  # microseconds
        "binary_search_comps": bin_comps,
        "binary_prep_time_sec": binary_prep_time,
        "binary_prep_time_ms": binary_prep_time * 1e3,
        "bubble_sort_time_sec": bs_time,
        "bubble_sort_time_ms": bs_time * 1e3,
        "bubble_sort_comps": bs_comps,
        "bubble_sort_swaps": bs_swaps,
        "quick_sort_time_sec": qs_time,
        "quick_sort_time_ms": qs_time * 1e3,
        "quick_sort_comps": qs_comps,
        "quick_sort_swaps": qs_swaps,
    }


def run_full_benchmark(sizes: Optional[List[int]] = None,
                       progress_callback: Optional[Callable[[int, int, str], None]] = None) -> List[Dict[str, Any]]:
    """
    Run empirical benchmarks across standard sizes: [10, 100, 1000, 5000].
    Notifies progress_callback with (current_index, total_steps, message).
    """
    if sizes is None:
        sizes = [10, 100, 1000, 5000]

    results = []
    total_sizes = len(sizes)

    for idx, size in enumerate(sizes):
        if progress_callback:
            progress_callback(idx, total_sizes, f"Benchmarking algorithms with N = {size:,} records...")
        res = run_single_size_benchmark(size)
        results.append(res)

    if progress_callback:
        progress_callback(total_sizes, total_sizes, "Benchmark execution completed successfully!")

    return results


def create_performance_figure(results: List[Dict[str, Any]]) -> Figure:
    """
    Generate professional, publication-quality performance graphs
    comparing Searching and Sorting algorithms side-by-side.
    """
    sizes = [r["size"] for r in results]
    sizes_str = [str(s) for s in sizes]

    # Searching metrics (in microseconds for readability)
    lin_times_us = [r["linear_search_time_us"] for r in results]
    bin_times_us = [r["binary_search_time_us"] for r in results]

    # Sorting metrics (in milliseconds)
    bubble_times_ms = [r["bubble_sort_time_ms"] for r in results]
    quick_times_ms = [r["quick_sort_time_ms"] for r in results]

    # Create figure with 2 subplots
    fig = Figure(figsize=(10.5, 4.4), dpi=100)
    fig.patch.set_facecolor("#f8fafc")

    # ---------------- Subplot 1: Searching Comparison ----------------
    ax1 = fig.add_subplot(1, 2, 1)
    ax1.set_facecolor("#ffffff")

    ax1.plot(sizes, lin_times_us, marker='o', linewidth=2.2, markersize=6,
             color='#ef4444', label='Linear Search - O(n)')
    ax1.plot(sizes, bin_times_us, marker='s', linewidth=2.2, markersize=6,
             color='#10b981', label='Binary Search - O(log n)')

    ax1.set_title("Searching Algorithms (Time in µs)", fontsize=11, fontweight='bold', color='#1e293b', pad=10)
    ax1.set_xlabel("Dataset Size (N)", fontsize=9, fontweight='bold', color='#475569')
    ax1.set_ylabel("Execution Time (µs)", fontsize=9, fontweight='bold', color='#475569')
    ax1.grid(True, linestyle='--', alpha=0.6, color='#cbd5e1')
    ax1.legend(loc='upper left', fontsize=8.5, framealpha=0.9)
    ax1.tick_params(colors='#475569', labelsize=8.5)

    # ---------------- Subplot 2: Sorting Comparison ----------------
    ax2 = fig.add_subplot(1, 2, 2)
    ax2.set_facecolor("#ffffff")

    ax2.plot(sizes, bubble_times_ms, marker='^', linewidth=2.2, markersize=6,
             color='#8b5cf6', label='Bubble Sort - O(n²)')
    ax2.plot(sizes, quick_times_ms, marker='D', linewidth=2.2, markersize=6,
             color='#3b82f6', label='Quick Sort - O(n log n)')

    ax2.set_title("Sorting Algorithms (Time in ms)", fontsize=11, fontweight='bold', color='#1e293b', pad=10)
    ax2.set_xlabel("Dataset Size (N)", fontsize=9, fontweight='bold', color='#475569')
    ax2.set_ylabel("Execution Time (ms)", fontsize=9, fontweight='bold', color='#475569')
    ax2.grid(True, linestyle='--', alpha=0.6, color='#cbd5e1')
    ax2.legend(loc='upper left', fontsize=8.5, framealpha=0.9)
    ax2.tick_params(colors='#475569', labelsize=8.5)

    fig.tight_layout(pad=2.5)
    return fig
