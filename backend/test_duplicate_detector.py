"""Test suite for duplicate complaint detection module.

Verifies:
1. Nearly identical complaints are detected as potential duplicates.
2. Complaints about different civic problems are not marked as duplicates.
3. Empty inputs (strings, lists, None) are handled safely without crashing.
4. Similarity scores strictly stay within the valid mathematical range [0.0, 1.0].
"""

import sys
from pathlib import Path

# Ensure backend directory is in path
sys.path.insert(0, str(Path(__file__).parent))

from duplicate_detector import find_duplicate_complaint, DEFAULT_DUPLICATE_THRESHOLD


def run_tests():
    print("=" * 80)
    print("RUNNING DUPLICATE DETECTOR TEST SUITE")
    print(f"Default Duplicate Threshold: {DEFAULT_DUPLICATE_THRESHOLD}")
    print("=" * 80)

    total_tests = 0
    passed_tests = 0

    def assert_test(condition: bool, description: str):
        nonlocal total_tests, passed_tests
        total_tests += 1
        if condition:
            passed_tests += 1
            print(f"[PASS] {description}")
        else:
            print(f"[FAIL] {description}")

    # -------------------------------------------------------------
    # 1. Nearly Identical Complaints (Should be flagged as duplicates)
    # -------------------------------------------------------------
    print("\n--- Test Group 1: Nearly Identical Complaints ---")
    existing_pool_1 = [
        "A deep pothole on the main road is causing severe traffic delays",
        "Frequent power cuts throughout the night in our locality",
        "Garbage is overflowing from the municipal bin onto the road",
    ]

    new_pothole = "There is a deep pothole on the main road causing heavy traffic delays"
    res1 = find_duplicate_complaint(new_pothole, existing_pool_1)
    assert_test(res1["is_duplicate"] is True, "Near-identical pothole complaint detected as duplicate")
    assert_test(res1["most_similar_complaint"] == existing_pool_1[0], "Correct matching pothole complaint returned")
    assert_test(res1["similarity_score"] >= DEFAULT_DUPLICATE_THRESHOLD, f"Similarity score ({res1['similarity_score']}) meets threshold")

    existing_pool_water = [
        "Water pipe is leaking continuously on the pedestrian path",
        "Streetlight is not working and dark at night",
    ]
    new_water = "Water pipe leaking continuously on pedestrian walkway"
    res_water = find_duplicate_complaint(new_water, existing_pool_water)
    assert_test(res_water["is_duplicate"] is True, "Near-identical water leak complaint detected as duplicate")
    assert_test(res_water["most_similar_complaint"] == existing_pool_water[0], "Correct matching water complaint returned")

    # Exact duplicate test
    exact_match = "Water pipe is leaking continuously on the pedestrian path"
    res_exact = find_duplicate_complaint(exact_match, existing_pool_water)
    assert_test(res_exact["is_duplicate"] is True, "Exact duplicate complaint detected")
    assert_test(res_exact["similarity_score"] == 1.0, f"Exact match similarity score is 1.0 (got {res_exact['similarity_score']})")

    # -------------------------------------------------------------
    # 2. Different Civic Problems (Should NOT be marked as duplicates)
    # -------------------------------------------------------------
    print("\n--- Test Group 2: Distinct Civic Problems ---")
    distinct_complaints = [
        "Frequent power cuts throughout the night in our locality",
        "Garbage is overflowing from the municipal bin onto the street",
        "The streetlight is broken and the whole street is pitch dark",
    ]
    new_distinct_road = "Multiple large potholes along the main avenue causing severe vehicular jams"
    res_distinct = find_duplicate_complaint(new_distinct_road, distinct_complaints)
    assert_test(res_distinct["is_duplicate"] is False, "Distinct road problem not marked as duplicate of power/garbage/lighting")
    assert_test(res_distinct["most_similar_complaint"] is None, "most_similar_complaint is None when duplicate not found")
    assert_test(res_distinct["similarity_score"] < DEFAULT_DUPLICATE_THRESHOLD, f"Distinct similarity score ({res_distinct['similarity_score']}) is below threshold")

    # Same domain, but completely different issue (Low pressure vs Burst pipeline)
    water_pool = [
        "Low water pressure since yesterday morning unable to fill storage tanks",
        "Sewage wastewater backing up into kitchen sink",
    ]
    new_burst_pipe = "Main municipal water supply pipeline has burst and flooding the lane"
    res_diff_water = find_duplicate_complaint(new_burst_pipe, water_pool)
    assert_test(res_diff_water["is_duplicate"] is False, "Different water issue (burst vs pressure) not marked as duplicate")

    # -------------------------------------------------------------
    # 3. Empty & Invalid Inputs (Safety Checks)
    # -------------------------------------------------------------
    print("\n--- Test Group 3: Empty and Invalid Inputs ---")
    res_empty_new = find_duplicate_complaint("", existing_pool_1)
    assert_test(res_empty_new["is_duplicate"] is False and res_empty_new["similarity_score"] == 0.0, "Empty new complaint handled safely")

    res_whitespace_new = find_duplicate_complaint("   \t\n   ", existing_pool_1)
    assert_test(res_whitespace_new["is_duplicate"] is False and res_whitespace_new["similarity_score"] == 0.0, "Whitespace-only new complaint handled safely")

    res_empty_list = find_duplicate_complaint("There is a pothole on the road", [])
    assert_test(res_empty_list["is_duplicate"] is False and res_empty_list["similarity_score"] == 0.0, "Empty existing list handled safely")

    res_whitespace_list = find_duplicate_complaint("There is a pothole on the road", ["", "   ", " \t "])
    assert_test(res_whitespace_list["is_duplicate"] is False and res_whitespace_list["similarity_score"] == 0.0, "Existing list with only blank strings handled safely")

    res_none_new = find_duplicate_complaint(None, existing_pool_1)
    assert_test(res_none_new["is_duplicate"] is False and res_none_new["similarity_score"] == 0.0, "None new complaint handled safely")

    res_none_list = find_duplicate_complaint("There is a pothole on the road", None)
    assert_test(res_none_list["is_duplicate"] is False and res_none_list["similarity_score"] == 0.0, "None existing complaints handled safely")

    # -------------------------------------------------------------
    # 4. Score Range Validation [0.0, 1.0]
    # -------------------------------------------------------------
    print("\n--- Test Group 4: Similarity Score Range Validation ---")
    all_results = [res1, res_water, res_exact, res_distinct, res_diff_water, res_empty_new, res_whitespace_new, res_empty_list]
    scores_in_range = all(0.0 <= r["similarity_score"] <= 1.0 for r in all_results)
    assert_test(scores_in_range, "All similarity scores strictly fall within [0.0, 1.0]")

    # Verify configurable threshold works
    custom_threshold = 0.90
    res_custom = find_duplicate_complaint(new_pothole, existing_pool_1, threshold=custom_threshold)
    assert_test(res_custom["is_duplicate"] is False, f"Score {res_custom['similarity_score']} does not trigger duplicate under stricter threshold {custom_threshold}")

    print("=" * 80)
    print(f"TEST SUMMARY: {passed_tests}/{total_tests} Passed")
    print("=" * 80)

    if passed_tests != total_tests:
        sys.exit(1)


if __name__ == "__main__":
    run_tests()
