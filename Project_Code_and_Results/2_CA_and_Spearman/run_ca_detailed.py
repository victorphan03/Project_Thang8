import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import prince

# Load data
df = pd.read_excel('Data_VN_filter_v5.xlsx')

# Extract variables
ugs_cols = ['Park', 'Residential', 'Garden', 'Rooftop', 'Recreation', 'Agriculture', 'Nature']

# Detailed ESS and DES variables
ess_des_detailed = [
    # RES (Điều hòa)
    'Temperature', 'Noise', 'Stormwind', 'Respiratory',
    # CES (Văn hóa)
    'Exercises', 'Culture', 'Beauty', 'Education', 'Society', 'Spirit',
    # DES (Bất lợi)
    'Dirty', 'Unsafe', 'Danger'
]

# Ensure the columns exist in df
available_detailed = [col for col in ess_des_detailed if col in df.columns]

# We want to run CA on the relationships between the 7 UGS types and the 13 specific services.
# Dữ liệu thang đo Likert thường là dữ liệu thứ bậc (Ordinal), nên dùng Spearman's rho sẽ chính xác hơn Pearson.
data = df[ugs_cols + available_detailed].dropna()
corr = data.corr(method='spearman').loc[ugs_cols, available_detailed]

# Tương tự như trước, dịch chuyển ma trận hệ số RHO để các giá trị đều dương (dùng cho CA)
# Alternatively, since prince CA handles frequencies, we can just pass the raw data? 
# If we pass raw data of shape (307, 20), CA will treat rows as individuals. 
# We want to see relationships between UGS and Detailed Services. Passing the correlation matrix (shifted) is a good proxy for similarity.
corr_shifted = corr + 1

# Initialize CA
ca = prince.CA(n_components=2, n_iter=3, copy=True, check_input=True, engine='scipy', random_state=42)
ca = ca.fit(corr_shifted)

# Extract column and row coordinates
row_coords = ca.row_coordinates(corr_shifted) # UGS
col_coords = ca.column_coordinates(corr_shifted) # Detailed Services

# Save to CSV
corr.to_csv('CA_Detailed_Correlation_Matrix.csv')
row_coords.to_csv('CA_Detailed_UGS_Coords.csv')
col_coords.to_csv('CA_Detailed_Services_Coords.csv')

# Plot Biplot
fig, ax = plt.subplots(figsize=(20, 15))

# Plot UGS points (blue dots)
p_ugs = ax.scatter(row_coords[0], row_coords[1], c='blue', label='UGS Types', s=80, marker='o', edgecolors='black')

# Plot ESS/DES points (red/green squares)
res_cols = ['Temperature', 'Noise', 'Stormwind', 'Respiratory']
ces_cols = ['Exercises', 'Culture', 'Beauty', 'Education', 'Society', 'Spirit']
des_cols = ['Dirty', 'Unsafe', 'Danger']

p_ess = []
for col in available_detailed:
    color = 'green' if col in res_cols else ('purple' if col in ces_cols else 'red')
    p = ax.scatter(col_coords.loc[col, 0], col_coords.loc[col, 1], c=color, marker='s', s=80, edgecolors='black')
    p_ess.append(p)

# Gắn nhãn (Text) tĩnh để đảm bảo tính nhất quán (Deterministic) 100% mỗi lần chạy
# Phân tách vị trí nhãn: UGS nằm lệch trên-trái, ESS/DES nằm lệch dưới-phải
for i, txt in enumerate(ugs_cols):
    ax.annotate(txt, (row_coords.iloc[i, 0], row_coords.iloc[i, 1]), 
                xytext=(-10, 10), textcoords='offset points', 
                color='blue', fontweight='bold', fontsize=12, ha='right', va='bottom')

for col in available_detailed:
    color = 'green' if col in res_cols else ('purple' if col in ces_cols else 'red')
    ax.annotate(col, (col_coords.loc[col, 0], col_coords.loc[col, 1]), 
                xytext=(10, -10), textcoords='offset points', 
                color=color, fontsize=12, fontweight='bold', ha='left', va='top')

# Add dummy plots for legend
ax.scatter([], [], c='green', marker='s', label='RES (Điều hòa)')
ax.scatter([], [], c='purple', marker='s', label='CES (Văn hóa)')
ax.scatter([], [], c='red', marker='s', label='DES (Bất lợi)')

ax.axhline(0, color='grey', linestyle='--', linewidth=1)
ax.axvline(0, color='grey', linestyle='--', linewidth=1)
ax.set_title('Detailed CA Biplot (UGS vs Specific ESS/DES)', fontsize=16)
ax.set_xlabel('Component 0', fontsize=12)
ax.set_ylabel('Component 1', fontsize=12)
ax.legend(loc='center left', bbox_to_anchor=(1.02, 0.5), fontsize=12)
plt.grid(True, linestyle=':', alpha=0.6)
plt.savefig('CA_plot_detailed.png', dpi=300, bbox_inches='tight')
print("\nDetailed CA Plot saved to CA_plot_detailed.png")
print("Detailed data exported to CSV files.")
