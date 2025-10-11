"""Visualize clustering results (requires matplotlib)."""

import pandas as pd
import numpy as np
from pathlib import Path


def create_text_visualization(output_dir: Path = None):
    """Create a text-based visualization of cluster results.
    
    Args:
        output_dir: Directory containing clustering output files
    """
    if output_dir is None:
        output_dir = Path(__file__).parent / "output" / "clustering"
    
    # Load cluster summary
    summary_path = output_dir / "cluster_summary_4clusters.csv"
    if not summary_path.exists():
        print("Error: Clustering results not found. Run student_clustering_analysis.py first.")
        return
    
    summary = pd.read_csv(summary_path)
    
    print("\n" + "=" * 80)
    print("CLUSTER VISUALIZATION - TEXT REPRESENTATION")
    print("=" * 80)
    print()
    
    # Size visualization
    print("CLUSTER SIZES (Visual Bar Chart)")
    print("-" * 80)
    max_size = summary['Size'].max()
    for _, row in summary.iterrows():
        cluster = int(row['Cluster'])
        size = int(row['Size'])
        bar_length = int((size / max_size) * 50)
        bar = "█" * bar_length
        print(f"Cluster {cluster}: {bar} {size}")
    print()
    
    # Arrest rate visualization
    print("AVERAGE ARRESTS PER CLUSTER (Visual Bar Chart)")
    print("-" * 80)
    max_arrests = summary['Avg_Arrests'].max()
    for _, row in summary.iterrows():
        cluster = int(row['Cluster'])
        arrests = row['Avg_Arrests']
        bar_length = int((arrests / max_arrests) * 50) if max_arrests > 0 else 0
        bar = "█" * bar_length
        print(f"Cluster {cluster}: {bar} {arrests:.2f}")
    print()
    
    # Risk level classification
    print("RISK LEVEL CLASSIFICATION")
    print("-" * 80)
    for _, row in summary.iterrows():
        cluster = int(row['Cluster'])
        arrests = row['Avg_Arrests']
        suspended = row['Pct_Suspended']
        expelled = row['Pct_Expelled']
        
        # Classify risk
        if arrests >= 3 or expelled >= 50:
            risk = "CRITICAL RISK ⚠️"
            color = "🔴"
        elif arrests >= 1.5 or suspended >= 50:
            risk = "HIGH RISK"
            color = "🟠"
        elif arrests >= 0.5 or suspended >= 20:
            risk = "MODERATE RISK"
            color = "🟡"
        else:
            risk = "LOW RISK"
            color = "🟢"
        
        print(f"{color} Cluster {cluster}: {risk}")
        print(f"   Arrests: {arrests:.2f}, Suspended: {suspended:.1f}%, Expelled: {expelled:.1f}%")
    print()
    
    # Gender distribution
    print("GENDER DISTRIBUTION")
    print("-" * 80)
    for _, row in summary.iterrows():
        cluster = int(row['Cluster'])
        female_pct = row['Pct_Female']
        male_pct = row['Pct_Male']
        
        female_bar = "♀" * int(female_pct / 5)
        male_bar = "♂" * int(male_pct / 5)
        
        print(f"Cluster {cluster}:")
        print(f"   Female ({female_pct:.1f}%): {female_bar}")
        print(f"   Male   ({male_pct:.1f}%): {male_bar}")
    print()
    
    # Grade distribution
    print("AVERAGE GRADE LEVELS")
    print("-" * 80)
    min_grade = summary['Avg_Grade'].min()
    max_grade = summary['Avg_Grade'].max()
    for _, row in summary.iterrows():
        cluster = int(row['Cluster'])
        grade = row['Avg_Grade']
        
        # Create grade scale visualization
        scale_pos = int(((grade - min_grade) / (max_grade - min_grade)) * 40) if max_grade > min_grade else 20
        scale = ["-"] * 41
        scale[scale_pos] = "●"
        scale_str = "".join(scale)
        
        print(f"Cluster {cluster}: [{scale_str}] {grade:.2f}")
    print(f"              {'9.0':<20}{'10.0':<10}{'11.0':<10}{'12.0':<10}")
    print()
    
    # Suspension/Expulsion heatmap
    print("DISCIPLINARY ACTION HEATMAP")
    print("-" * 80)
    print(f"{'Cluster':<10} {'Suspended':<20} {'Expelled':<20}")
    print("-" * 80)
    for _, row in summary.iterrows():
        cluster = int(row['Cluster'])
        suspended = row['Pct_Suspended']
        expelled = row['Pct_Expelled']
        
        # Create visual indicators
        susp_level = "█" * int(suspended / 10)
        exp_level = "█" * int(expelled / 10)
        
        print(f"{cluster:<10} {susp_level:<20} {exp_level:<20}")
        print(f"{'':10} {suspended:.1f}%{'':14} {expelled:.1f}%")
    print()
    
    # Key findings summary
    print("KEY FINDINGS SUMMARY")
    print("-" * 80)
    
    # Find specific patterns
    largest_cluster = summary.loc[summary['Size'].idxmax()]
    highest_risk = summary.loc[summary['Avg_Arrests'].idxmax()]
    lowest_risk = summary.loc[summary['Avg_Arrests'].idxmin()]
    
    print(f"📊 Largest Cluster: {int(largest_cluster['Cluster'])} with {int(largest_cluster['Size'])} students")
    print(f"⚠️  Highest Risk: Cluster {int(highest_risk['Cluster'])} (Avg arrests: {highest_risk['Avg_Arrests']:.2f})")
    print(f"✅ Lowest Risk: Cluster {int(lowest_risk['Cluster'])} (Avg arrests: {lowest_risk['Avg_Arrests']:.2f})")
    
    # Grade-risk correlation
    if highest_risk['Avg_Grade'] < lowest_risk['Avg_Grade']:
        print(f"📈 Pattern: Lower grades correlate with higher risk")
    else:
        print(f"📉 Pattern: Higher grades correlate with higher risk")
    
    # Gender patterns
    if highest_risk['Pct_Male'] > 60:
        print(f"👤 Gender: High-risk cluster is predominantly male ({highest_risk['Pct_Male']:.1f}%)")
    elif highest_risk['Pct_Female'] > 60:
        print(f"👤 Gender: High-risk cluster is predominantly female ({highest_risk['Pct_Female']:.1f}%)")
    
    print()
    print("=" * 80)


def main():
    """Main execution function."""
    print("Cluster Visualization Tool")
    print("=" * 80)
    
    base_dir = Path(__file__).parent
    output_dir = base_dir / "output" / "clustering"
    
    if not output_dir.exists():
        print("\nError: Clustering output directory not found.")
        print("Please run: python src/student_clustering_analysis.py")
        return
    
    create_text_visualization(output_dir)
    
    print("\nFor advanced visualizations, consider installing matplotlib:")
    print("  pip install matplotlib seaborn")
    print("\nThen you can create:")
    print("  - Scatter plots (PCA/t-SNE projections)")
    print("  - Heatmaps of cluster characteristics")
    print("  - Bar charts comparing clusters")
    print("  - Distribution plots for each feature")


if __name__ == "__main__":
    main()
