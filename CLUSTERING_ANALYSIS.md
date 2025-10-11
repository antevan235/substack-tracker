# Student Data K-Means Clustering Analysis

This document describes the k-Means clustering analysis performed on student behavioral and demographic data.

## Overview

The analysis applies k-Means clustering to identify distinct groups of students based on their behavioral patterns and risk factors. The implementation includes comprehensive analysis tools and reporting capabilities.

## Features

- **K-Means Clustering**: Configurable number of clusters (default: 4)
- **Risk Assessment**: Identify high-risk, medium-risk, and low-risk student clusters
- **Comprehensive Metrics**: Analyze arrest rates, suspension rates, expulsion rates, and demographic patterns
- **Flexible Data Loading**: Support for both CSV files and programmatically generated data
- **Detailed Reporting**: Automated generation of analysis reports with all key metrics

## Data Structure

The student data should contain the following columns:

- **StudentID**: Unique identifier for each student
- **Gender**: 0 = Female, 1 = Male
- **Grade**: Grade level (e.g., 9, 10, 11, 12)
- **Arrests**: Number of arrests
- **Suspended**: Binary flag (0 = No, 1 = Yes)
- **Expelled**: Binary flag (0 = No, 1 = Yes)

## Installation

Install required dependencies:

```bash
pip install -r requirements.txt
```

Required packages:
- pandas >= 2.0.0
- numpy >= 1.24.0
- scikit-learn >= 1.3.0

## Usage

### Running the Analysis

Execute the clustering analysis script:

```bash
python src/student_clustering_analysis.py
```

The script will:
1. Load student data from `data/student_data.csv` or generate sample data if not found
2. Run k-Means clustering with 4 clusters
3. Generate comprehensive analysis report
4. Run k-Means clustering with 3 clusters (for comparison)
5. Save all results to `output/clustering/`

### Using the API

You can also use the clustering module programmatically:

```python
import pandas as pd
from src.analytics.clustering import StudentClusteringAnalyzer, generate_analysis_report

# Load your data
df = pd.read_csv('data/student_data.csv')

# Initialize analyzer
analyzer = StudentClusteringAnalyzer(n_clusters=4, random_state=42)

# Load and fit data
analyzer.load_data(df)
analyzer.fit_kmeans()

# Get specific metrics
largest_cluster_size = analyzer.get_largest_cluster_size()
student_cluster = analyzer.get_student_cluster(938)
critical_cluster, critical_rate = analyzer.identify_critical_risk_cluster()

# Generate full report
report = generate_analysis_report(analyzer)
print(report)
```

## Analysis Results

### 4-Cluster Analysis

The analysis with 4 clusters provides answers to all key questions:

1. **Largest Cluster Size**: 311 students (Cluster 1)

2. **Student ID 938**: Belongs to Cluster 2

3. **Critical Risk Cluster**: Cluster 3 (highest arrest rate of 3.52)
   - Label: "Critical Risk"
   - 100% suspension rate
   - 100% expulsion rate
   - Lower grade levels (avg 9.20)

4. **Gender Distribution in Cluster 0**: 
   - More Males (310) than Females (0)

5. **Suspension Proportion in Cluster 3**: 100.00% (1.0000)

6. **Expulsions in Cluster 0**: 
   - No expulsions (count: 0)

7. **Average Arrests in Cluster 2**: 2.29

8. **Middle-Risk Classification**:
   - Based on arrest rate thresholds (0.5 - 2.0)
   - Can be customized using `classify_middle_risk_clusters()` method

9. **Grade Attribute Interpretation**:
   - Higher grades associated with lower risk
   - High-Risk Cluster (3): Grade 9.20, Arrests 3.52
   - Low-Risk Cluster (1): Grade 10.66, Arrests 0.20

### 3-Cluster Analysis

When clustering is repeated with 3 clusters:
- **Highest-Risk Cluster**: Cluster 2
- **Student Count**: 92 students
- **Average Arrests**: 3.52

### Cluster Profiles (4-Cluster Model)

| Cluster | Size | Avg Arrests | Avg Grade | % Suspended | % Expelled | Profile |
|---------|------|-------------|-----------|-------------|------------|---------|
| 0 | 310 | 0.23 | 10.63 | 2.90% | 0% | Low-risk males |
| 1 | 311 | 0.20 | 10.66 | 6.75% | 0% | Low-risk females |
| 2 | 287 | 2.29 | 9.38 | 100% | 0% | High-risk suspended |
| 3 | 92 | 3.52 | 9.20 | 100% | 100% | **Critical risk** |

## Output Files

All results are saved to `output/clustering/`:

### 4-Cluster Analysis:
- `clustering_analysis_4clusters.txt` - Complete text report
- `student_data_with_clusters_4.csv` - Original data with cluster assignments
- `cluster_summary_4clusters.csv` - Statistical summary of each cluster
- `cluster_centroids_4clusters.csv` - Cluster centroid values

### 3-Cluster Analysis:
- `student_data_with_clusters_3.csv` - Original data with cluster assignments
- `cluster_summary_3clusters.csv` - Statistical summary of each cluster
- `cluster_centroids_3clusters.csv` - Cluster centroid values

## Interpretation Guide

### Risk Levels

Based on the clustering results:

1. **Low Risk (Clusters 0 & 1)**:
   - Very few arrests (< 0.3 average)
   - Low suspension rates
   - Higher grade levels
   - No expulsions

2. **High Risk (Cluster 2)**:
   - Moderate arrests (2.29 average)
   - 100% suspension rate
   - Lower grade levels
   - No expulsions yet

3. **Critical Risk (Cluster 3)**:
   - High arrests (3.52 average)
   - 100% suspension rate
   - 100% expulsion rate
   - Lowest grade levels
   - Requires immediate intervention

### Patterns Observed

- **Grade-Risk Relationship**: Clear inverse relationship between grade level and risk factors
- **Gender Patterns**: Clusters 0 and 1 show gender segregation in low-risk groups
- **Escalation Path**: Cluster 2 → Cluster 3 represents risk escalation trajectory
- **Early Warning**: Students in Cluster 2 are at high risk of escalating to Critical Risk

## Customization

### Adjusting Cluster Count

```python
analyzer = StudentClusteringAnalyzer(n_clusters=5)
analyzer.load_data(df)
analyzer.fit_kmeans()
```

### Custom Risk Thresholds

```python
# Define custom middle-risk thresholds
middle_risk_clusters = analyzer.classify_middle_risk_clusters(
    threshold_low=1.0,
    threshold_high=3.0
)
```

### Feature Selection

Modify the `preprocess_data()` method in `src/analytics/clustering.py` to adjust which features are used for clustering.

## Methodology

### Preprocessing

1. Feature selection: Gender, Grade, Arrests, Suspended, Expelled
2. Missing value handling: Fill with 0
3. Feature scaling: StandardScaler (mean=0, std=1)

### Clustering

- Algorithm: k-Means
- Initialization: k-means++ (default)
- Number of initializations: 10
- Random state: 42 (for reproducibility)

### Validation

The model quality can be assessed by:
- Examining cluster separation in feature space
- Analyzing cluster silhouette scores
- Reviewing within-cluster variance
- Validating cluster interpretability

## References

This analysis supports exercises and questions related to:
- Student behavioral risk assessment
- Clustering-based profiling
- Educational intervention planning
- Predictive risk modeling

## Contributing

To extend the analysis:

1. Add new features to the student data
2. Implement additional clustering algorithms (DBSCAN, Hierarchical)
3. Add visualization capabilities (PCA plots, cluster heatmaps)
4. Develop predictive models based on cluster assignments

## License

This clustering analysis module is part of the Substack Tracker project.
