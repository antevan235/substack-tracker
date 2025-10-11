"""Run k-Means clustering analysis on student data.

This script demonstrates the complete workflow for analyzing student data
using k-Means clustering with 4 clusters, and optionally with 3 clusters.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from analytics.clustering import StudentClusteringAnalyzer, generate_analysis_report


def create_sample_student_data(n_students: int = 1000, include_student_938: bool = True) -> pd.DataFrame:
    """Create sample student data for clustering analysis.
    
    Args:
        n_students: Number of students to generate
        include_student_938: Whether to include student ID 938 specifically
        
    Returns:
        DataFrame with student data
    """
    np.random.seed(42)
    
    # Generate diverse student profiles
    data = []
    
    # Profile 1: Low-risk students (40%)
    n_low_risk = int(n_students * 0.4)
    for i in range(n_low_risk):
        data.append({
            'StudentID': i + 1,
            'Gender': np.random.choice([0, 1]),  # 0=Female, 1=Male
            'Grade': np.random.choice([10, 11, 12], p=[0.3, 0.35, 0.35]),
            'Arrests': 0,
            'Suspended': 0,
            'Expelled': 0
        })
    
    # Profile 2: Moderate-risk students (30%)
    n_moderate = int(n_students * 0.3)
    for i in range(n_moderate):
        data.append({
            'StudentID': n_low_risk + i + 1,
            'Gender': np.random.choice([0, 1]),
            'Grade': np.random.choice([9, 10, 11], p=[0.4, 0.4, 0.2]),
            'Arrests': np.random.choice([0, 1, 2], p=[0.5, 0.3, 0.2]),
            'Suspended': np.random.choice([0, 1], p=[0.6, 0.4]),
            'Expelled': 0
        })
    
    # Profile 3: Higher-risk students (20%)
    n_high = int(n_students * 0.2)
    for i in range(n_high):
        data.append({
            'StudentID': n_low_risk + n_moderate + i + 1,
            'Gender': np.random.choice([0, 1], p=[0.3, 0.7]),  # More males
            'Grade': np.random.choice([9, 10], p=[0.6, 0.4]),
            'Arrests': np.random.choice([1, 2, 3, 4], p=[0.3, 0.3, 0.2, 0.2]),
            'Suspended': 1,
            'Expelled': np.random.choice([0, 1], p=[0.8, 0.2])
        })
    
    # Profile 4: Critical-risk students (10%)
    n_critical = n_students - n_low_risk - n_moderate - n_high
    for i in range(n_critical):
        data.append({
            'StudentID': n_low_risk + n_moderate + n_high + i + 1,
            'Gender': np.random.choice([0, 1], p=[0.2, 0.8]),  # Mostly males
            'Grade': 9,
            'Arrests': np.random.choice([3, 4, 5, 6], p=[0.3, 0.3, 0.2, 0.2]),
            'Suspended': 1,
            'Expelled': np.random.choice([0, 1], p=[0.5, 0.5])
        })
    
    df = pd.DataFrame(data)
    
    # Include student 938 if requested
    if include_student_938 and 938 not in df['StudentID'].values:
        # Add student 938 as a moderate-risk student
        df = pd.concat([df, pd.DataFrame([{
            'StudentID': 938,
            'Gender': 1,
            'Grade': 10,
            'Arrests': 1,
            'Suspended': 1,
            'Expelled': 0
        }])], ignore_index=True)
    
    return df.sort_values('StudentID').reset_index(drop=True)


def load_student_data_from_csv(filepath: str) -> pd.DataFrame:
    """Load student data from CSV file.
    
    Args:
        filepath: Path to CSV file with student data
        
    Returns:
        DataFrame with student data
    """
    df = pd.read_csv(filepath)
    required_cols = ['StudentID', 'Gender', 'Grade', 'Arrests', 'Suspended', 'Expelled']
    
    # Validate columns
    missing = [col for col in required_cols if col not in df.columns]
    if missing:
        raise ValueError(f"CSV missing required columns: {missing}")
    
    return df


def run_four_cluster_analysis(df: pd.DataFrame, output_dir: Path) -> StudentClusteringAnalyzer:
    """Run k-Means clustering with 4 clusters.
    
    Args:
        df: Student data DataFrame
        output_dir: Directory to save output files
        
    Returns:
        Fitted analyzer instance
    """
    print("\n" + "=" * 70)
    print("RUNNING K-MEANS CLUSTERING WITH 4 CLUSTERS")
    print("=" * 70 + "\n")
    
    # Initialize analyzer
    analyzer = StudentClusteringAnalyzer(n_clusters=4, random_state=42)
    
    # Load and process data
    print("Loading student data...")
    analyzer.load_data(df)
    print(f"Loaded {len(df)} students")
    
    # Fit clustering model
    print("\nFitting k-Means clustering model...")
    analyzer.fit_kmeans()
    print("Clustering complete!")
    
    # Generate report
    print("\nGenerating analysis report...")
    report = generate_analysis_report(analyzer)
    print(report)
    
    # Save report to file
    output_dir.mkdir(parents=True, exist_ok=True)
    report_path = output_dir / "clustering_analysis_4clusters.txt"
    with open(report_path, 'w') as f:
        f.write(report)
    print(f"\nReport saved to: {report_path}")
    
    # Save clustered data to CSV
    clustered_data_path = output_dir / "student_data_with_clusters_4.csv"
    analyzer.df.to_csv(clustered_data_path, index=False)
    print(f"Clustered data saved to: {clustered_data_path}")
    
    # Save cluster summary
    summary_path = output_dir / "cluster_summary_4clusters.csv"
    analyzer.get_cluster_summary().to_csv(summary_path, index=False)
    print(f"Cluster summary saved to: {summary_path}")
    
    # Save centroids
    centroids_path = output_dir / "cluster_centroids_4clusters.csv"
    analyzer.get_centroids_dataframe().to_csv(centroids_path, index=False)
    print(f"Cluster centroids saved to: {centroids_path}")
    
    return analyzer


def run_three_cluster_analysis(df: pd.DataFrame, output_dir: Path) -> StudentClusteringAnalyzer:
    """Run k-Means clustering with 3 clusters.
    
    Args:
        df: Student data DataFrame
        output_dir: Directory to save output files
        
    Returns:
        Fitted analyzer instance
    """
    print("\n" + "=" * 70)
    print("RUNNING K-MEANS CLUSTERING WITH 3 CLUSTERS")
    print("=" * 70 + "\n")
    
    # Initialize analyzer with 3 clusters
    analyzer = StudentClusteringAnalyzer(n_clusters=3, random_state=42)
    
    # Load and process data
    print("Loading student data...")
    analyzer.load_data(df)
    print(f"Loaded {len(df)} students")
    
    # Fit clustering model
    print("\nFitting k-Means clustering model...")
    analyzer.fit_kmeans()
    print("Clustering complete!")
    
    # Identify highest-risk cluster
    critical_cluster, critical_rate = analyzer.identify_critical_risk_cluster()
    cluster_sizes = analyzer.get_cluster_sizes()
    highest_risk_count = cluster_sizes[critical_cluster]
    
    print(f"\nHighest-Risk Cluster (Cluster {critical_cluster}):")
    print(f"  - Student Count: {highest_risk_count}")
    print(f"  - Average Arrests: {critical_rate:.2f}")
    
    # Save results
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Save clustered data
    clustered_data_path = output_dir / "student_data_with_clusters_3.csv"
    analyzer.df.to_csv(clustered_data_path, index=False)
    print(f"\nClustered data saved to: {clustered_data_path}")
    
    # Save cluster summary
    summary_path = output_dir / "cluster_summary_3clusters.csv"
    analyzer.get_cluster_summary().to_csv(summary_path, index=False)
    print(f"Cluster summary saved to: {summary_path}")
    
    # Save centroids
    centroids_path = output_dir / "cluster_centroids_3clusters.csv"
    analyzer.get_centroids_dataframe().to_csv(centroids_path, index=False)
    print(f"Cluster centroids saved to: {centroids_path}")
    
    return analyzer


def main():
    """Main execution function."""
    print("Student Data K-Means Clustering Analysis")
    print("=" * 70)
    
    # Set up directories
    base_dir = Path(__file__).parent.parent
    output_dir = base_dir / "output" / "clustering"
    data_dir = base_dir / "data"
    
    # Check if student data CSV exists
    student_csv_path = data_dir / "student_data.csv"
    
    if student_csv_path.exists():
        print(f"\nLoading student data from: {student_csv_path}")
        df = load_student_data_from_csv(str(student_csv_path))
    else:
        print("\nNo student data CSV found. Generating sample data...")
        df = create_sample_student_data(n_students=1000, include_student_938=True)
        
        # Save sample data
        data_dir.mkdir(parents=True, exist_ok=True)
        df.to_csv(student_csv_path, index=False)
        print(f"Sample data saved to: {student_csv_path}")
    
    print(f"\nDataset Info:")
    print(f"  - Total Students: {len(df)}")
    print(f"  - Columns: {', '.join(df.columns)}")
    print(f"\nFirst few rows:")
    print(df.head(10))
    
    # Run 4-cluster analysis
    analyzer_4 = run_four_cluster_analysis(df, output_dir)
    
    # Run 3-cluster analysis
    print("\n")
    analyzer_3 = run_three_cluster_analysis(df, output_dir)
    
    print("\n" + "=" * 70)
    print("ANALYSIS COMPLETE!")
    print("=" * 70)
    print(f"\nAll output files saved to: {output_dir}")
    print("\nGenerated files:")
    print("  - clustering_analysis_4clusters.txt")
    print("  - student_data_with_clusters_4.csv")
    print("  - cluster_summary_4clusters.csv")
    print("  - cluster_centroids_4clusters.csv")
    print("  - student_data_with_clusters_3.csv")
    print("  - cluster_summary_3clusters.csv")
    print("  - cluster_centroids_3clusters.csv")


if __name__ == "__main__":
    main()
