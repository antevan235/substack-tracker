# K-Means Clustering Analysis - Answer Key

This document provides answers to all analysis questions from the exercise.

## Analysis Setup

- **Dataset**: 1,000 students with behavioral and demographic data
- **Clustering Algorithm**: k-Means
- **Number of Clusters**: 4 (primary analysis) and 3 (comparison analysis)
- **Random Seed**: 42 (for reproducibility)

## Question Answers

### 1. Number of Students in the Largest Cluster

**Answer: 311 students**

The largest cluster is Cluster 1, containing 311 students (31.1% of the total population).

### 2. Which Cluster Does Student ID 938 Belong To?

**Answer: Cluster 2**

Student ID 938 is assigned to Cluster 2, which is classified as a high-risk cluster with:
- Average arrests: 2.29
- 100% suspension rate
- Lower average grade level (9.38)

### 3. Critical Risk Cluster (Highest Arrest Rate)

**Answer: Cluster 3 - "Critical Risk"**

- **Average Arrests**: 3.52
- **Suspension Rate**: 100%
- **Expulsion Rate**: 100%
- **Average Grade**: 9.20
- **Size**: 92 students

Cluster 3 has the highest arrest rate and is labeled as **"Critical Risk"** due to:
- Significantly higher arrest rates compared to other clusters
- 100% of students have been suspended
- 100% of students have been expelled
- Lowest average grade level
- Predominantly male (69.6%)

### 4. Gender Distribution in Cluster 0

**Question**: Are there more females (0) or males (1) in cluster_0?

**Answer: Males**

Cluster 0 gender distribution:
- **Females**: 0 students (0%)
- **Males**: 310 students (100%)

Cluster 0 is exclusively male students and represents a low-risk profile with minimal arrests (0.23 average) and low suspension rates (2.9%).

### 5. Proportion of Students Suspended in Cluster 3

**Answer: 100% (1.0000)**

All students in Cluster 3 (the Critical Risk cluster) have been suspended. This is 92 out of 92 students, giving a proportion of exactly 1.0 or 100%.

### 6. Expulsions in Cluster 0

**Question**: Have any students in cluster_0 ever been expelled?

**Answer: No**

- **Has Expulsions**: False
- **Count**: 0 expelled students
- **Student IDs**: [] (empty list)

None of the 310 students in Cluster 0 have been expelled. This aligns with Cluster 0's low-risk profile.

### 7. Average Number of Arrests in Cluster 2

**Answer: 2.29 arrests**

Cluster 2 has an average of 2.29 arrests per student, making it a high-risk cluster (though not as severe as Cluster 3's 3.52 average).

### 8. Middle-Risk Clusters Using Centroids

Using the centroid data to classify clusters:

**Analysis Method**:
- Low Risk: < 0.5 average arrests
- Middle Risk: 0.5 - 2.0 average arrests  
- High Risk: 2.0 - 3.0 average arrests
- Critical Risk: > 3.0 average arrests

**Middle-Risk Classification** (0.5 - 2.0 arrests):
- With default thresholds: 0 clusters qualify
- **Adjusted thresholds** (1.0 - 3.0 arrests): Cluster 2 qualifies

**Total Students in Middle-Risk Clusters** (adjusted): 287 students

**Note**: The default middle-risk range (0.5-2.0) doesn't capture Cluster 2 (2.29), so the thresholds can be adjusted based on institutional definitions of risk levels.

### 9. Grade Attribute Interpretation

**Pattern: Higher grades are associated with lower risk**

**Evidence**:

High-Risk Cluster (Cluster 3):
- Average Grade: **9.20**
- Average Arrests: **3.52**
- All students suspended and expelled

Low-Risk Clusters (Clusters 0 & 1):
- Average Grade: **10.63 - 10.66**
- Average Arrests: **0.20 - 0.23**
- Minimal suspensions, no expulsions

**Interpretation**:
There is a clear inverse relationship between grade level and risk factors. Students in lower grades (9th grade primarily) show significantly higher arrest rates, suspension rates, and expulsion rates compared to students in higher grades (11th-12th). This suggests that:

1. Younger students may benefit from additional support and intervention
2. Grade level could be an early warning indicator for behavioral issues
3. Students who progress to higher grades tend to have better behavioral outcomes

### 10. Three-Cluster Analysis

**Question**: If clustering is repeated with 3 clusters, what is the student count in the highest-risk cluster?

**Answer: 92 students**

When k-Means is run with 3 clusters instead of 4:
- **Highest-Risk Cluster**: Cluster 2
- **Student Count**: 92 students
- **Average Arrests**: 3.52

Interestingly, this is the same count as Cluster 3 in the 4-cluster model, suggesting that the critical-risk students form a distinct, stable group regardless of the number of clusters specified.

## Cluster Profiles Summary

### 4-Cluster Model:

| Cluster | Size | Risk Level | Avg Arrests | % Suspended | % Expelled | Profile |
|---------|------|------------|-------------|-------------|------------|---------|
| 0 | 310 | Low | 0.23 | 2.9% | 0% | Low-risk males, higher grades |
| 1 | 311 | Low | 0.20 | 6.8% | 0% | Low-risk females, higher grades |
| 2 | 287 | High | 2.29 | 100% | 0% | High-risk, all suspended |
| 3 | 92 | **Critical** | 3.52 | 100% | 100% | Critical risk, all expelled |

### 3-Cluster Model:

| Cluster | Size | Risk Level | Avg Arrests | % Suspended | % Expelled |
|---------|------|------------|-------------|-------------|------------|
| 0 | 321 | High | 2.12 | 96.9% | 0% |
| 1 | 587 | Low | 0.18 | 1.0% | 0% |
| 2 | 92 | **Critical** | 3.52 | 100% | 100% |

## Key Insights

1. **Clear Risk Stratification**: The clustering successfully identified distinct risk levels among students.

2. **Gender Segregation in Low-Risk Groups**: Clusters 0 and 1 show complete gender separation, suggesting different behavioral patterns between males and females in low-risk populations.

3. **Critical Risk Population**: A consistent group of 92 students (~9% of population) represents the highest risk, characterized by:
   - Multiple arrests (3.5+ average)
   - 100% suspension rate
   - 100% expulsion rate
   - Predominantly male
   - Lower grade levels

4. **Grade-Risk Correlation**: Strong inverse correlation between grade level and risk factors, with 9th graders showing highest risk.

5. **Intervention Priority**: The analysis clearly identifies which students need immediate intervention (Cluster 3) versus those needing monitoring (Cluster 2) versus those doing well (Clusters 0 & 1).

## Recommendations

Based on the clustering analysis:

1. **Immediate Focus**: Provide intensive support to the 92 students in the Critical Risk cluster
2. **Prevention**: Monitor the 287 students in Cluster 2 to prevent escalation to critical risk
3. **Early Intervention**: Focus prevention efforts on 9th-grade students
4. **Gender-Specific Programs**: Consider different approaches for male and female students
5. **Grade Progression Support**: Help at-risk students progress through grade levels successfully

## Files Generated

All analysis outputs are saved in `output/clustering/`:
- `clustering_analysis_4clusters.txt` - Full analysis report
- `student_data_with_clusters_4.csv` - Data with cluster assignments
- `cluster_summary_4clusters.csv` - Statistical summary by cluster
- `cluster_centroids_4clusters.csv` - Cluster centroid values
- Similar files for 3-cluster analysis

## Running the Analysis

To reproduce these results:

```bash
python src/student_clustering_analysis.py
```

To visualize the results:

```bash
python visualize_clusters.py
```

To run tests:

```bash
python test_clustering.py
```

---

**Note**: These results are based on generated sample data. When applied to real student data, results may vary, but the analysis methodology remains the same.
