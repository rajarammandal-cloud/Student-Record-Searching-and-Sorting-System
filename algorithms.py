"""
algorithms.py
-------------
Manual implementations of exactly four core DAA algorithms:
1. Linear Search
2. Binary Search
3. Bubble Sort
4. Quick Sort

None of these algorithms use external libraries or Python's built-in sorting.
All timing is captured via time.perf_counter() with microsecond precision.
"""

import time
from typing import List, Dict, Any, Tuple, Optional


# =====================================================================
# THEORETICAL COMPLEXITY METADATA
# =====================================================================

COMPLEXITY_INFO = {
    "linear_search": {
        "name": "Linear Search",
        "type": "Searching",
        "best": "O(1)",
        "average": "O(n)",
        "worst": "O(n)",
        "space": "O(1)",
        "description": "Sequentially compares each record's roll number until a match is found or the end is reached."
    },
    "binary_search": {
        "name": "Binary Search",
        "type": "Searching",
        "best": "O(1)",
        "average": "O(log n)",
        "worst": "O(log n)",
        "space": "O(1)",
        "description": "Repeatedly halves the search space using low, high, and mid pointers. Requires records to be pre-sorted by key."
    },
    "bubble_sort": {
        "name": "Bubble Sort",
        "type": "Sorting",
        "best": "O(n²)",  # Unoptimized baseline as specified in syllabus
        "best_optimized": "O(n)",
        "average": "O(n²)",
        "worst": "O(n²)",
        "space": "O(1)",
        "description": "Repeatedly steps through the list, compares adjacent elements, and swaps them if in the wrong order."
    },
    "quick_sort": {
        "name": "Quick Sort",
        "type": "Sorting",
        "best": "O(n log n)",
        "average": "O(n log n)",
        "worst": "O(n²)",
        "space": "O(log n)",
        "description": "Divide-and-conquer algorithm that selects a pivot, partitions elements around the pivot, and recursively sorts subarrays."
    }
}


# =====================================================================
# 1. LINEAR SEARCH
# =====================================================================

def linear_search(records: List[Dict[str, Any]], target_roll: int) -> Tuple[int, Optional[Dict[str, Any]], int, float]:
    """
    Manually perform Linear Search on student records by roll number.

    Parameters:
        records: List of student dictionaries
        target_roll: The roll number to find

    Returns:
        (index, found_record, comparisons_count, execution_time_seconds)
    """
    comparisons = 0
    start_time = time.perf_counter()

    found_idx = -1
    found_record = None

    # Step through records one by one
    for idx in range(len(records)):
        comparisons += 1
        if records[idx]["roll_no"] == target_roll:
            found_idx = idx
            found_record = records[idx]
            break

    exec_time = time.perf_counter() - start_time
    return found_idx, found_record, comparisons, exec_time


# =====================================================================
# 2. BINARY SEARCH
# =====================================================================

def binary_search(records: List[Dict[str, Any]], target_roll: int) -> Tuple[int, Optional[Dict[str, Any]], int, float]:
    """
    Manually perform Binary Search on student records by roll number.
    Assumes `records` is already sorted by 'roll_no'.

    Parameters:
        records: List of student dictionaries (PRE-SORTED by roll_no)
        target_roll: The roll number to find

    Returns:
        (index, found_record, comparisons_count, execution_time_seconds)
    """
    comparisons = 0
    start_time = time.perf_counter()

    low = 0
    high = len(records) - 1
    found_idx = -1
    found_record = None

    while low <= high:
        comparisons += 1
        mid = (low + high) // 2
        mid_val = records[mid]["roll_no"]

        if mid_val == target_roll:
            found_idx = mid
            found_record = records[mid]
            break
        elif mid_val < target_roll:
            low = mid + 1
        else:
            high = mid - 1

    exec_time = time.perf_counter() - start_time
    return found_idx, found_record, comparisons, exec_time


def binary_search_with_prep(records: List[Dict[str, Any]], target_roll: int) -> Tuple[int, Optional[Dict[str, Any]], int, float, float, List[Dict[str, Any]]]:
    """
    Prepares records for Binary Search if not already sorted, measures
    the sorting preparation time separately from the pure binary search time.

    Returns:
        (index, found_record, comparisons, search_time, prep_sort_time, sorted_records)
    """
    # Check if already sorted by roll_no
    is_sorted = True
    for i in range(len(records) - 1):
        if records[i]["roll_no"] > records[i + 1]["roll_no"]:
            is_sorted = False
            break

    prep_sort_time = 0.0
    if not is_sorted:
        # Sort a copy using Quick Sort
        sorted_records, prep_sort_time, _, _ = quick_sort(records, key="roll_no", ascending=True)
    else:
        sorted_records = [dict(r) for r in records]

    # Perform pure binary search on sorted dataset
    idx, student, comparisons, search_time = binary_search(sorted_records, target_roll)

    return idx, student, comparisons, search_time, prep_sort_time, sorted_records


# =====================================================================
# 3. BUBBLE SORT
# =====================================================================

def bubble_sort(records: List[Dict[str, Any]], key: str = "roll_no", ascending: bool = True) -> Tuple[List[Dict[str, Any]], float, int, int]:
    """
    Manually perform Bubble Sort on student records.
    Compares adjacent elements and swaps them when out of order.
    
    Standard syllabus implementation:
    Operates in O(n²) time across best, average, and worst cases (without early break),
    while accurately counting comparisons and swaps.

    Parameters:
        records: List of student records to sort
        key: Dictionary key to sort by ('roll_no' or 'marks')
        ascending: True for ascending order, False for descending

    Returns:
        (sorted_records, execution_time_seconds, comparisons_count, swaps_count)
    """
    arr = [dict(r) for r in records]
    n = len(arr)
    comparisons = 0
    swaps = 0

    start_time = time.perf_counter()

    for i in range(n - 1):
        for j in range(0, n - i - 1):
            comparisons += 1
            val_a = arr[j][key]
            val_b = arr[j + 1][key]

            should_swap = (val_a > val_b) if ascending else (val_a < val_b)
            if should_swap:
                # Manual swap
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
                swaps += 1

    exec_time = time.perf_counter() - start_time
    return arr, exec_time, comparisons, swaps


# =====================================================================
# 4. QUICK SORT
# =====================================================================

def quick_sort(records: List[Dict[str, Any]], key: str = "roll_no", ascending: bool = True) -> Tuple[List[Dict[str, Any]], float, int, int]:
    """
    Manually perform Quick Sort on student records using pivot partitioning.

    Parameters:
        records: List of student records to sort
        key: Dictionary key to sort by ('roll_no' or 'marks')
        ascending: True for ascending order, False for descending

    Returns:
        (sorted_records, execution_time_seconds, comparisons_count, swaps_count)
    """
    arr = [dict(r) for r in records]
    comparisons = [0]
    swaps = [0]

    start_time = time.perf_counter()

    def partition(low: int, high: int) -> int:
        # Choose middle element as pivot to prevent worst-case O(n²) on already sorted data
        mid = (low + high) // 2
        # Move pivot to high
        arr[mid], arr[high] = arr[high], arr[mid]
        swaps[0] += 1

        pivot_val = arr[high][key]
        i = low - 1  # Index of smaller/greater element

        for j in range(low, high):
            comparisons[0] += 1
            current_val = arr[j][key]
            condition = (current_val <= pivot_val) if ascending else (current_val >= pivot_val)
            if condition:
                i += 1
                arr[i], arr[j] = arr[j], arr[i]
                swaps[0] += 1

        # Place pivot in correct position
        arr[i + 1], arr[high] = arr[high], arr[i + 1]
        swaps[0] += 1
        return i + 1

    def _quick_sort_recursive(low: int, high: int) -> None:
        if low < high:
            pi = partition(low, high)
            _quick_sort_recursive(low, pi - 1)
            _quick_sort_recursive(pi + 1, high)

    if len(arr) > 1:
        _quick_sort_recursive(0, len(arr) - 1)

    exec_time = time.perf_counter() - start_time
    return arr, exec_time, comparisons[0], swaps[0]
