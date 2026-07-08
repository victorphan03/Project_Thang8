import sys
sys.stdout.reconfigure(encoding='utf-8')
import pandas as pd
import numpy as np
import scipy.stats as stats
from scipy.cluster.hierarchy import linkage, fcluster
import matplotlib.pyplot as plt
import seaborn as sns
from factor_analyzer.factor_analyzer import calculate_kmo, calculate_bartlett_sphericity
import os

# --- Helper function for Varimax Rotation ---
def varimax(loadings, max_iter=500, tolerance=1e-6):
    X = loadings.copy()
    n_rows, n_cols = X.shape
    if n_cols < 2:
        return X, np.eye(n_cols)
    
    R = np.eye(n_cols)
    d = 0
    for i in range(max_iter):
        d_old = d
        Lambda = np.dot(X, R)
        grad = np.dot(X.T, Lambda**3 - (1.0 / n_rows) * np.dot(Lambda, np.diag(np.sum(Lambda**2, axis=0))))
        u, s, vh = np.linalg.svd(grad)
        R = np.dot(u, vh)
        d = np.sum(s)
        if d_old != 0 and (d - d_old) / d_old < tolerance:
            break
            
    rotated_loadings = np.dot(X, R)
    return rotated_loadings, R

# --- Setup Paths ---
base_dir = r"c:\Users\NASPC\Documents\Du án tại SG tháng 8"
output_dir = os.path.join(base_dir, "PCA_HCA_Results")
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

file_path = os.path.join(base_dir, 'Data_VN_filter_v5.xlsx')
df = pd.read_excel(file_path)

# --- 1. Variables Definition ---
pca_vars = [
    'Temperature', 'Noise', 'Stormwind', 'Respiratory', # RES
    'Exercises', 'Culture', 'Beauty', 'Education', 'Society', 'Spirit', # CES
    'Dirty', 'Unsafe', 'Danger' # DES
]
demographic_vars = ['Gender', 'Career', 'Literacy']
habit_vars = ['Distance', 'Frequency', 'Time', 'Transportation']

# Ensure variables exist and drop NaNs for PCA
df_pca = df[pca_vars].dropna()
n_samples = len(df_pca)
print(f"--- Bước 2: Phân tích thành phần chính (PCA) ---")
print(f"Cỡ mẫu (N): {n_samples}")

# --- 2. KMO & Bartlett's Test ---
kmo_all, kmo_model = calculate_kmo(df_pca)
bartlett_stat, bartlett_p = calculate_bartlett_sphericity(df_pca)

print("\nBảng 1: Kaiser-Meyer-Olkin Test")
print(f"Overall MSA: {kmo_model:.5f}")
for var, kmo_val in zip(pca_vars, kmo_all):
    print(f"  {var}: {kmo_val:.5f}")

print("\nBảng 2: Bartlett's Test of Sphericity")
df_bartlett = len(pca_vars) * (len(pca_vars) - 1) / 2
print(f"X^2: {bartlett_stat:.5f}, df: {int(df_bartlett)}, p: {bartlett_p}")

# --- 3. PCA with Varimax Rotation ---
# Standardize with ddof=1 to match JASP
X_mean = df_pca.mean()
X_std = df_pca.std(ddof=1)
X_scaled = (df_pca - X_mean) / X_std

# Correlation matrix
R_corr = np.corrcoef(df_pca.T)
eigenvalues, eigenvectors = np.linalg.eigh(R_corr)

# Sort descending
idx = np.argsort(eigenvalues)[::-1]
eigenvalues = eigenvalues[idx]
eigenvectors = eigenvectors[:, idx]

print("\nBảng 6: Component Characteristics (Unrotated)")
for i, ev in enumerate(eigenvalues[:5]): # Print top 5 for illustration
    print(f"Component {i+1}: Eigenvalue = {ev:.5f}, Proportion = {ev/sum(eigenvalues):.5f}")

# Extract 2 components
unrotated_loadings = eigenvectors[:, :2] * np.sqrt(eigenvalues[:2])
rotated_loadings, R = varimax(unrotated_loadings)

# Align signs with JASP: PC1 positive for Beauty, PC2 positive for Dirty
idx_beauty = pca_vars.index('Beauty')
idx_dirty = pca_vars.index('Dirty')

if rotated_loadings[idx_beauty, 0] < 0:
    rotated_loadings[:, 0] = -rotated_loadings[:, 0]
    R[:, 0] = -R[:, 0]
if rotated_loadings[idx_dirty, 1] < 0:
    rotated_loadings[:, 1] = -rotated_loadings[:, 1]
    R[:, 1] = -R[:, 1]

uniqueness = 1 - np.sum(rotated_loadings**2, axis=1)

print("\nBảng 5: Component Loadings (Varimax Rotated)")
loadings_df = pd.DataFrame(rotated_loadings, index=pca_vars, columns=['PC1', 'PC2'])
loadings_df['Uniqueness'] = uniqueness
print(loadings_df.round(5).to_string())

# Save Loadings to CSV
loadings_df.to_csv(os.path.join(output_dir, 'PCA_Component_Loadings.csv'))

# --- 4. Plot PCA Loading Biplot ---
plt.figure(figsize=(10, 8))
plt.scatter(rotated_loadings[:, 0], rotated_loadings[:, 1], color='blue', alpha=0.5)
for i, txt in enumerate(pca_vars):
    plt.annotate(txt, (rotated_loadings[i, 0], rotated_loadings[i, 1]), xytext=(5,5), textcoords='offset points')
plt.axhline(0, color='black',linewidth=1, ls='--')
plt.axvline(0, color='black',linewidth=1, ls='--')
plt.xlabel('Component 1 (ESS)')
plt.ylabel('Component 2 (DES)')
plt.title('PCA Loading Plot (Varimax Rotated)')
plt.grid(True, linestyle=':', alpha=0.6)
plt.savefig(os.path.join(output_dir, 'PCA_Loading_Plot.png'), dpi=300)
plt.close()

# --- 5. Component Scores for HCA ---
# Calculate Standardized Component Scores
scores_std = (np.dot(X_scaled, eigenvectors[:, :2]) / np.sqrt(eigenvalues[:2])).dot(R)

print("\n--- Bước 3: Phân tích cụm phân cấp (HCA) & Chi-square ---")
# --- 6. HCA (Ward's Method) ---
Z = linkage(scores_std, method='ward')
clusters = fcluster(Z, 3, criterion='maxclust')

# Map clusters to original dataframe
# Note: Since we dropped NaNs for PCA, we need to carefully assign back
# Assuming original df has no NaNs in these columns based on previous logs (N=307 valid).
# Just to be safe, we assign via index.
df.loc[df_pca.index, 'Cluster'] = clusters
df.loc[df_pca.index, 'PC1_Score'] = scores_std[:, 0]
df.loc[df_pca.index, 'PC2_Score'] = scores_std[:, 1]

# Align cluster labels with JASP based on sizes (199, 61, 47) and Means
cluster_sizes = df['Cluster'].value_counts()
print(f"\nGiai đoạn 3.1 - Gom cụm (HCA)")
print("Cluster Sizes (Before Label Alignment):")
print(cluster_sizes)

# Map our generic cluster IDs (1, 2, 3) to JASP's cluster IDs
# From our previous test:
# Our Cluster with size 199 -> JASP Cluster 3 (Hài hòa & Thụ hưởng)
# Our Cluster with size 61 -> JASP Cluster 2 (Thờ ơ)
# Our Cluster with size 47 -> JASP Cluster 1 (Thực dụng & Lo ngại)
mapping = {}
for clst, size in cluster_sizes.items():
    if size == 199:
        mapping[clst] = 3
    elif size == 61:
        mapping[clst] = 2
    elif size == 47:
        mapping[clst] = 1
    else:
        mapping[clst] = clst # fallback

df['Cluster'] = df['Cluster'].map(mapping)
print("\nCluster Sizes (Aligned with JASP):")
print(df['Cluster'].value_counts())

cluster_means = df.groupby('Cluster')[['PC1_Score', 'PC2_Score']].mean()
print("\nBảng 3: Cluster Means")
print(cluster_means.round(5))

# Plot Cluster Means
cluster_means.plot(kind='bar', figsize=(10, 6))
plt.title('Cluster Means for PC1 and PC2')
plt.ylabel('Mean Standardized Score')
plt.xlabel('Cluster')
plt.axhline(0, color='black', linewidth=0.8, ls='--')
plt.xticks(rotation=0)
plt.savefig(os.path.join(output_dir, 'HCA_Cluster_Means_Plot.png'), dpi=300)
plt.close()

# Save DataFrame with Clusters
output_dataset_path = os.path.join(base_dir, 'Data_VN_filter_v5_with_clusters.xlsx')
df.to_excel(output_dataset_path, index=False)
print(f"\nĐã lưu dataset mới kèm nhãn Cụm và Điểm nhân tố tại: {output_dataset_path}")

# --- 7. Profiling (Chi-Square) ---
def compute_cramer_v(chi2, n, shape):
    return np.sqrt(chi2 / (n * (min(shape) - 1)))

def profile_clusters(df, variables, title):
    print(f"\n{title}")
    results = []
    
    for var in variables:
        if var not in df.columns:
            continue
        # Contingency table (cross-tabulation)
        ct = pd.crosstab(df['Cluster'], df[var])
        
        # Chi-square test
        chi2, p, dof, expected = stats.chi2_contingency(ct)
        n = ct.sum().sum()
        
        # Cramer's V and Phi
        v = compute_cramer_v(chi2, n, ct.shape)
        
        print(f"\n--- {var} ---")
        print("Contingency Table (Counts):")
        print(ct)
        print(f"Chi-Square: {chi2:.5f}, df: {dof}, p: {p:.5f}")
        print(f"Cramer's V (Contingency coefficient approx): {v:.5f}")
        
        results.append({
            'Variable': var,
            'Chi_Square': chi2,
            'df': dof,
            'p_value': p,
            'Cramers_V': v
        })
        
        # Detailed Table (like JASP) with row percentages
        ct_pct = ct.div(ct.sum(axis=1), axis=0) * 100
        # save detailed to csv just in case
        ct_detailed = pd.concat([ct, ct_pct.add_suffix('_Pct')], axis=1)
        ct_detailed.to_csv(os.path.join(output_dir, f'Profiling_{var}_Contingency.csv'))

    res_df = pd.DataFrame(results)
    res_df.to_csv(os.path.join(output_dir, f'Profiling_{title.replace(" ", "_")}_Summary.csv'), index=False)

profile_clusters(df, demographic_vars, "Lần so sánh 1: Nhân khẩu học (Demographics)")
profile_clusters(df, habit_vars, "Lần so sánh 2: Thói quen tương tác (Habits)")

print("\n--- HOÀN THÀNH ---")
print(f"Các bảng kết quả và biểu đồ đã được lưu tại: {output_dir}")
