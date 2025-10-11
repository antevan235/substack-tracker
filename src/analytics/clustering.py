"""K-Means clustering analysis for student data.

This module provides k-Means clustering capabilities for analyzing student
behavioral and demographic data, including risk assessment and profiling.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler


class StudentClusteringAnalyzer:
    """Analyze student data using k-Means clustering."""
    
    def __init__(self, n_clusters: int = 4, random_state: int = 42):
        """Initialize the clustering analyzer.
        
        Args:
            n_clusters: Number of clusters for k-Means
            random_state: Random seed for reproducibility
        """
        self.n_clusters = n_clusters
        self.random_state = random_state
        self.kmeans = None
        self.scaler = StandardScaler()
        self.df = None
        self.cluster_labels = None
        self.centroids = None
        
    def load_data(self, data: pd.DataFrame) -> None:
        """Load and validate student data.
        
        Args:
            data: DataFrame with student information including:
                  StudentID, Gender, Grade, Arrests, Suspended, Expelled
        """
        required_cols = ['StudentID', 'Gender', 'Grade', 'Arrests', 'Suspended', 'Expelled']
        missing_cols = [col for col in required_cols if col not in data.columns]
        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")
        
        self.df = data.copy()
        
    def preprocess_data(self) -> pd.DataFrame:
        """Preprocess student data for clustering.
        
        Returns:
            Preprocessed DataFrame with scaled features
        """
        if self.df is None:
            raise ValueError("No data loaded. Call load_data() first.")
        
        # Select features for clustering
        feature_cols = ['Gender', 'Grade', 'Arrests', 'Suspended', 'Expelled']
        X = self.df[feature_cols].copy()
        
        # Handle any missing values
        X = X.fillna(0)
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        return pd.DataFrame(X_scaled, columns=feature_cols, index=self.df.index)
    
    def fit_kmeans(self) -> None:
        """Fit k-Means clustering model to preprocessed data."""
        X_scaled = self.preprocess_data()
        
        self.kmeans = KMeans(
            n_clusters=self.n_clusters,
            random_state=self.random_state,
            n_init=10
        )
        
        self.cluster_labels = self.kmeans.fit_predict(X_scaled)
        self.df['cluster'] = self.cluster_labels
        
        # Store centroids (in original scale for interpretation)
        feature_cols = ['Gender', 'Grade', 'Arrests', 'Suspended', 'Expelled']
        self.centroids = pd.DataFrame(
            self.scaler.inverse_transform(self.kmeans.cluster_centers_),
            columns=feature_cols
        )
        
    def get_cluster_sizes(self) -> Dict[int, int]:
        """Get the number of students in each cluster.
        
        Returns:
            Dictionary mapping cluster number to student count
        """
        if self.cluster_labels is None:
            raise ValueError("Model not fitted. Call fit_kmeans() first.")
        
        return dict(self.df['cluster'].value_counts().sort_index())
    
    def get_largest_cluster_size(self) -> int:
        """Get the size of the largest cluster.
        
        Returns:
            Number of students in the largest cluster
        """
        sizes = self.get_cluster_sizes()
        return max(sizes.values())
    
    def get_student_cluster(self, student_id: int) -> Optional[int]:
        """Find which cluster a specific student belongs to.
        
        Args:
            student_id: The student ID to look up
            
        Returns:
            Cluster number (0-indexed) or None if student not found
        """
        if self.df is None or 'cluster' not in self.df.columns:
            raise ValueError("Model not fitted. Call fit_kmeans() first.")
        
        student_data = self.df[self.df['StudentID'] == student_id]
        if len(student_data) == 0:
            return None
        
        return int(student_data['cluster'].iloc[0])
    
    def get_cluster_arrest_rates(self) -> Dict[int, float]:
        """Calculate arrest rate (average arrests) for each cluster.
        
        Returns:
            Dictionary mapping cluster number to average arrest count
        """
        if self.df is None or 'cluster' not in self.df.columns:
            raise ValueError("Model not fitted. Call fit_kmeans() first.")
        
        return dict(self.df.groupby('cluster')['Arrests'].mean().sort_index())
    
    def identify_critical_risk_cluster(self) -> Tuple[int, float]:
        """Identify the cluster with highest arrest rate.
        
        Returns:
            Tuple of (cluster_number, arrest_rate)
        """
        arrest_rates = self.get_cluster_arrest_rates()
        critical_cluster = max(arrest_rates.items(), key=lambda x: x[1])
        return critical_cluster
    
    def get_gender_distribution(self, cluster_num: int) -> Dict[str, int]:
        """Get gender distribution in a specific cluster.
        
        Args:
            cluster_num: Cluster number to analyze
            
        Returns:
            Dictionary with counts: {'Female': count, 'Male': count}
        """
        if self.df is None or 'cluster' not in self.df.columns:
            raise ValueError("Model not fitted. Call fit_kmeans() first.")
        
        cluster_data = self.df[self.df['cluster'] == cluster_num]
        gender_counts = cluster_data['Gender'].value_counts()
        
        return {
            'Female': int(gender_counts.get(0, 0)),
            'Male': int(gender_counts.get(1, 0))
        }
    
    def has_more_females_or_males(self, cluster_num: int) -> str:
        """Determine if a cluster has more females or males.
        
        Args:
            cluster_num: Cluster number to analyze
            
        Returns:
            'Female' or 'Male' depending on which has higher count
        """
        dist = self.get_gender_distribution(cluster_num)
        return 'Female' if dist['Female'] > dist['Male'] else 'Male'
    
    def get_suspension_proportion(self, cluster_num: int) -> float:
        """Calculate proportion of suspended students in a cluster.
        
        Args:
            cluster_num: Cluster number to analyze
            
        Returns:
            Proportion of students suspended (0.0 to 1.0)
        """
        if self.df is None or 'cluster' not in self.df.columns:
            raise ValueError("Model not fitted. Call fit_kmeans() first.")
        
        cluster_data = self.df[self.df['cluster'] == cluster_num]
        total = len(cluster_data)
        suspended = (cluster_data['Suspended'] == 1).sum()
        
        return suspended / total if total > 0 else 0.0
    
    def check_expulsions_in_cluster(self, cluster_num: int) -> Dict[str, any]:
        """Check if any students in a cluster have been expelled.
        
        Args:
            cluster_num: Cluster number to analyze
            
        Returns:
            Dictionary with 'has_expulsions' (bool), 'count' (int), 
            and 'student_ids' (list)
        """
        if self.df is None or 'cluster' not in self.df.columns:
            raise ValueError("Model not fitted. Call fit_kmeans() first.")
        
        cluster_data = self.df[self.df['cluster'] == cluster_num]
        expelled_students = cluster_data[cluster_data['Expelled'] == 1]
        
        return {
            'has_expulsions': len(expelled_students) > 0,
            'count': len(expelled_students),
            'student_ids': expelled_students['StudentID'].tolist()
        }
    
    def get_average_arrests(self, cluster_num: int) -> float:
        """Calculate average number of arrests in a cluster.
        
        Args:
            cluster_num: Cluster number to analyze
            
        Returns:
            Average arrest count
        """
        if self.df is None or 'cluster' not in self.df.columns:
            raise ValueError("Model not fitted. Call fit_kmeans() first.")
        
        cluster_data = self.df[self.df['cluster'] == cluster_num]
        return float(cluster_data['Arrests'].mean())
    
    def classify_middle_risk_clusters(self, threshold_low: float = 0.5, 
                                     threshold_high: float = 2.0) -> List[int]:
        """Classify clusters as middle-risk based on arrest rates.
        
        Args:
            threshold_low: Lower bound for middle-risk arrest rate
            threshold_high: Upper bound for middle-risk arrest rate
            
        Returns:
            List of cluster numbers classified as middle-risk
        """
        arrest_rates = self.get_cluster_arrest_rates()
        middle_risk = [
            cluster for cluster, rate in arrest_rates.items()
            if threshold_low <= rate <= threshold_high
        ]
        return middle_risk
    
    def count_middle_risk_students(self, middle_risk_clusters: List[int]) -> int:
        """Count total students in middle-risk clusters.
        
        Args:
            middle_risk_clusters: List of cluster numbers classified as middle-risk
            
        Returns:
            Total count of students in those clusters
        """
        if self.df is None or 'cluster' not in self.df.columns:
            raise ValueError("Model not fitted. Call fit_kmeans() first.")
        
        return int(self.df[self.df['cluster'].isin(middle_risk_clusters)].shape[0])
    
    def get_cluster_summary(self) -> pd.DataFrame:
        """Generate comprehensive summary of all clusters.
        
        Returns:
            DataFrame with cluster statistics
        """
        if self.df is None or 'cluster' not in self.df.columns:
            raise ValueError("Model not fitted. Call fit_kmeans() first.")
        
        summary = []
        for cluster_num in range(self.n_clusters):
            cluster_data = self.df[self.df['cluster'] == cluster_num]
            
            summary.append({
                'Cluster': cluster_num,
                'Size': len(cluster_data),
                'Avg_Arrests': cluster_data['Arrests'].mean(),
                'Avg_Grade': cluster_data['Grade'].mean(),
                'Pct_Suspended': (cluster_data['Suspended'] == 1).sum() / len(cluster_data) * 100,
                'Pct_Expelled': (cluster_data['Expelled'] == 1).sum() / len(cluster_data) * 100,
                'Pct_Female': (cluster_data['Gender'] == 0).sum() / len(cluster_data) * 100,
                'Pct_Male': (cluster_data['Gender'] == 1).sum() / len(cluster_data) * 100
            })
        
        return pd.DataFrame(summary)
    
    def get_centroids_dataframe(self) -> pd.DataFrame:
        """Get cluster centroids as a DataFrame.
        
        Returns:
            DataFrame with centroid values for each feature
        """
        if self.centroids is None:
            raise ValueError("Model not fitted. Call fit_kmeans() first.")
        
        centroids_df = self.centroids.copy()
        centroids_df.insert(0, 'Cluster', range(self.n_clusters))
        return centroids_df
    
    def refit_with_n_clusters(self, n_clusters: int) -> None:
        """Refit the model with a different number of clusters.
        
        Args:
            n_clusters: New number of clusters
        """
        self.n_clusters = n_clusters
        self.fit_kmeans()
    
    def interpret_grade_risk(self) -> str:
        """Interpret the relationship between grade and risk factors.
        
        Returns:
            Text interpretation of grade patterns across clusters
        """
        if self.df is None or 'cluster' not in self.df.columns:
            raise ValueError("Model not fitted. Call fit_kmeans() first.")
        
        summary = self.get_cluster_summary()
        
        # Find patterns
        high_risk = summary.loc[summary['Avg_Arrests'].idxmax()]
        low_risk = summary.loc[summary['Avg_Arrests'].idxmin()]
        
        interpretation = f"""Grade Risk Interpretation:
        
High-Risk Cluster (Cluster {int(high_risk['Cluster'])}):
  - Average Grade: {high_risk['Avg_Grade']:.2f}
  - Average Arrests: {high_risk['Avg_Arrests']:.2f}
  
Low-Risk Cluster (Cluster {int(low_risk['Cluster'])}):
  - Average Grade: {low_risk['Avg_Grade']:.2f}
  - Average Arrests: {low_risk['Avg_Arrests']:.2f}
  
Pattern: {'Higher grades associated with lower risk' if high_risk['Avg_Grade'] < low_risk['Avg_Grade'] else 'Lower grades associated with lower risk' if high_risk['Avg_Grade'] > low_risk['Avg_Grade'] else 'No clear grade-risk relationship'}
"""
        return interpretation


def generate_analysis_report(analyzer: StudentClusteringAnalyzer) -> str:
    """Generate a comprehensive analysis report.
    
    Args:
        analyzer: Fitted StudentClusteringAnalyzer instance
        
    Returns:
        Formatted text report with all analysis results
    """
    report = []
    report.append("=" * 70)
    report.append("K-MEANS CLUSTERING ANALYSIS REPORT")
    report.append("=" * 70)
    report.append("")
    
    # Cluster sizes
    report.append("1. CLUSTER SIZES")
    report.append("-" * 70)
    sizes = analyzer.get_cluster_sizes()
    for cluster, size in sizes.items():
        report.append(f"   Cluster {cluster}: {size} students")
    report.append(f"\n   Largest Cluster Size: {analyzer.get_largest_cluster_size()} students")
    report.append("")
    
    # Student 938 cluster
    report.append("2. STUDENT ID 938 CLUSTER ASSIGNMENT")
    report.append("-" * 70)
    cluster_938 = analyzer.get_student_cluster(938)
    if cluster_938 is not None:
        report.append(f"   Student ID 938 belongs to Cluster {cluster_938}")
    else:
        report.append("   Student ID 938 not found in dataset")
    report.append("")
    
    # Critical risk cluster
    report.append("3. CRITICAL RISK CLUSTER (Highest Arrest Rate)")
    report.append("-" * 70)
    critical_cluster, critical_rate = analyzer.identify_critical_risk_cluster()
    report.append(f"   Cluster {critical_cluster} - Average Arrests: {critical_rate:.2f}")
    report.append(f"   LABEL: Critical Risk")
    report.append("")
    
    # Gender distribution in cluster 0
    report.append("4. GENDER DISTRIBUTION IN CLUSTER 0")
    report.append("-" * 70)
    gender_dist = analyzer.get_gender_distribution(0)
    report.append(f"   Females (0): {gender_dist['Female']}")
    report.append(f"   Males (1): {gender_dist['Male']}")
    report.append(f"   More: {analyzer.has_more_females_or_males(0)}s")
    report.append("")
    
    # Suspension proportion in cluster 3
    report.append("5. SUSPENSION PROPORTION IN CLUSTER 3")
    report.append("-" * 70)
    susp_prop = analyzer.get_suspension_proportion(3)
    report.append(f"   Proportion Suspended: {susp_prop:.2%} ({susp_prop:.4f})")
    report.append("")
    
    # Expulsions in cluster 0
    report.append("6. EXPULSIONS IN CLUSTER 0")
    report.append("-" * 70)
    expulsion_info = analyzer.check_expulsions_in_cluster(0)
    report.append(f"   Has Expulsions: {expulsion_info['has_expulsions']}")
    report.append(f"   Count: {expulsion_info['count']}")
    if expulsion_info['student_ids']:
        report.append(f"   Student IDs: {expulsion_info['student_ids']}")
    report.append("")
    
    # Average arrests in cluster 2
    report.append("7. AVERAGE ARRESTS IN CLUSTER 2")
    report.append("-" * 70)
    avg_arrests = analyzer.get_average_arrests(2)
    report.append(f"   Average Arrests: {avg_arrests:.2f}")
    report.append("")
    
    # Middle-risk clusters
    report.append("8. MIDDLE-RISK CLUSTER CLASSIFICATION")
    report.append("-" * 70)
    middle_risk = analyzer.classify_middle_risk_clusters()
    report.append(f"   Middle-Risk Clusters: {middle_risk}")
    middle_risk_count = analyzer.count_middle_risk_students(middle_risk)
    report.append(f"   Total Students in Middle-Risk Clusters: {middle_risk_count}")
    report.append("")
    
    # Grade interpretation
    report.append("9. GRADE ATTRIBUTE INTERPRETATION")
    report.append("-" * 70)
    report.append(analyzer.interpret_grade_risk())
    report.append("")
    
    # Cluster summary
    report.append("10. COMPREHENSIVE CLUSTER SUMMARY")
    report.append("-" * 70)
    summary_df = analyzer.get_cluster_summary()
    report.append(summary_df.to_string(index=False))
    report.append("")
    
    # Centroids
    report.append("11. CLUSTER CENTROIDS")
    report.append("-" * 70)
    centroids_df = analyzer.get_centroids_dataframe()
    report.append(centroids_df.to_string(index=False))
    report.append("")
    
    report.append("=" * 70)
    
    return "\n".join(report)
