import sys
sys.stdout.reconfigure(encoding='utf-8')
import pandas as pd
import scipy.stats as stats
import os

base_dir = r'c:\Users\NASPC\Documents\Du án tại SG tháng 8\Project_Code_and_Results'
df = pd.read_excel(r'c:\Users\NASPC\Documents\Du án tại SG tháng 8\Data_VN_filter_v5_with_clusters.xlsx')

results = []
for var in ['Donation', 'Decision']:
    df_clean = df.dropna(subset=['Cluster', var])
    ct = pd.crosstab(df_clean['Cluster'], df_clean[var])
    chi2, p, dof, _ = stats.chi2_contingency(ct)
    
    ct_pct = ct.div(ct.sum(axis=1), axis=0) * 100
    print(f"\n--- {var} ---")
    print("Counts:")
    print(ct)
    print("\nPercentages:")
    print(ct_pct)
    print(f"Chi-square: {chi2:.4f}, p-value: {p:.4f}")
    
    res = pd.concat([ct, ct_pct.add_suffix('_Pct')], axis=1)
    res.to_csv(os.path.join(base_dir, '3_PCA_and_HCA', f'Profiling_H4_{var}_Contingency.csv'))

print("\nĐã xuất kết quả kiểm định H4.")
