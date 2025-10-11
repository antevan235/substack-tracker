"""Simple test to verify clustering module works correctly."""

import pandas as pd
from src.analytics.clustering import StudentClusteringAnalyzer, generate_analysis_report


def test_clustering_basic():
    """Test basic clustering functionality."""
    print("Testing k-Means Clustering Module...")
    print("=" * 70)
    
    # Create simple test data
    data = {
        'StudentID': [1, 2, 3, 4, 5, 6, 7, 8, 938],
        'Gender': [0, 1, 0, 1, 1, 0, 1, 0, 1],
        'Grade': [10, 10, 11, 9, 12, 9, 10, 11, 10],
        'Arrests': [0, 0, 0, 3, 0, 4, 1, 0, 1],
        'Suspended': [0, 0, 0, 1, 0, 1, 1, 0, 1],
        'Expelled': [0, 0, 0, 1, 0, 1, 0, 0, 0]
    }
    df = pd.DataFrame(data)
    
    # Initialize analyzer
    analyzer = StudentClusteringAnalyzer(n_clusters=3, random_state=42)
    
    # Load data
    print("\n1. Loading data...")
    analyzer.load_data(df)
    print(f"   ✓ Loaded {len(df)} students")
    
    # Fit model
    print("\n2. Fitting k-Means model...")
    analyzer.fit_kmeans()
    print("   ✓ Model fitted successfully")
    
    # Test cluster sizes
    print("\n3. Testing cluster sizes...")
    sizes = analyzer.get_cluster_sizes()
    print(f"   ✓ Cluster sizes: {sizes}")
    assert sum(sizes.values()) == len(df), "Sum of cluster sizes should equal total students"
    
    # Test largest cluster
    print("\n4. Testing largest cluster...")
    largest = analyzer.get_largest_cluster_size()
    print(f"   ✓ Largest cluster size: {largest}")
    assert largest == max(sizes.values()), "Largest cluster size mismatch"
    
    # Test student lookup
    print("\n5. Testing student ID 938 lookup...")
    cluster_938 = analyzer.get_student_cluster(938)
    print(f"   ✓ Student 938 in cluster: {cluster_938}")
    assert cluster_938 is not None, "Student 938 should be found"
    assert 0 <= cluster_938 < 3, "Cluster number should be valid"
    
    # Test arrest rates
    print("\n6. Testing arrest rate calculation...")
    arrest_rates = analyzer.get_cluster_arrest_rates()
    print(f"   ✓ Arrest rates: {arrest_rates}")
    assert len(arrest_rates) == 3, "Should have 3 cluster arrest rates"
    
    # Test critical risk cluster
    print("\n7. Testing critical risk identification...")
    critical_cluster, critical_rate = analyzer.identify_critical_risk_cluster()
    print(f"   ✓ Critical risk cluster: {critical_cluster} (rate: {critical_rate:.2f})")
    assert critical_rate == max(arrest_rates.values()), "Should identify highest arrest rate"
    
    # Test gender distribution
    print("\n8. Testing gender distribution...")
    for cluster_num in range(3):
        gender_dist = analyzer.get_gender_distribution(cluster_num)
        print(f"   ✓ Cluster {cluster_num}: {gender_dist}")
        assert 'Female' in gender_dist and 'Male' in gender_dist, "Should have both genders"
    
    # Test suspension proportion
    print("\n9. Testing suspension proportion...")
    for cluster_num in range(3):
        susp_prop = analyzer.get_suspension_proportion(cluster_num)
        print(f"   ✓ Cluster {cluster_num} suspension rate: {susp_prop:.2%}")
        assert 0 <= susp_prop <= 1, "Proportion should be between 0 and 1"
    
    # Test expulsion check
    print("\n10. Testing expulsion check...")
    for cluster_num in range(3):
        expulsion_info = analyzer.check_expulsions_in_cluster(cluster_num)
        print(f"   ✓ Cluster {cluster_num} expulsions: {expulsion_info['count']}")
        assert 'has_expulsions' in expulsion_info, "Should have expulsions flag"
        assert 'count' in expulsion_info, "Should have count"
        assert 'student_ids' in expulsion_info, "Should have student IDs"
    
    # Test average arrests
    print("\n11. Testing average arrests...")
    for cluster_num in range(3):
        avg_arrests = analyzer.get_average_arrests(cluster_num)
        print(f"   ✓ Cluster {cluster_num} avg arrests: {avg_arrests:.2f}")
        assert avg_arrests >= 0, "Average arrests should be non-negative"
    
    # Test middle-risk classification
    print("\n12. Testing middle-risk classification...")
    middle_risk = analyzer.classify_middle_risk_clusters()
    middle_risk_count = analyzer.count_middle_risk_students(middle_risk)
    print(f"   ✓ Middle-risk clusters: {middle_risk}")
    print(f"   ✓ Middle-risk student count: {middle_risk_count}")
    
    # Test cluster summary
    print("\n13. Testing cluster summary...")
    summary = analyzer.get_cluster_summary()
    print(f"   ✓ Summary shape: {summary.shape}")
    assert len(summary) == 3, "Should have 3 rows in summary"
    
    # Test centroids
    print("\n14. Testing centroids...")
    centroids = analyzer.get_centroids_dataframe()
    print(f"   ✓ Centroids shape: {centroids.shape}")
    assert len(centroids) == 3, "Should have 3 centroids"
    
    # Test grade interpretation
    print("\n15. Testing grade interpretation...")
    interpretation = analyzer.interpret_grade_risk()
    print(f"   ✓ Interpretation generated ({len(interpretation)} chars)")
    assert len(interpretation) > 0, "Interpretation should not be empty"
    
    # Test report generation
    print("\n16. Testing report generation...")
    report = generate_analysis_report(analyzer)
    print(f"   ✓ Report generated ({len(report)} chars)")
    assert "K-MEANS CLUSTERING ANALYSIS REPORT" in report, "Report should have title"
    assert "Student ID 938" in report, "Report should mention student 938"
    
    print("\n" + "=" * 70)
    print("✓ ALL TESTS PASSED!")
    print("=" * 70)
    
    return True


if __name__ == "__main__":
    try:
        test_clustering_basic()
        print("\n✓ Clustering module is working correctly!")
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
