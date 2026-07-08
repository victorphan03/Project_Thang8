import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Đọc ma trận RHO đã tính từ file CSV
corr = pd.read_csv('CA_Detailed_Correlation_Matrix.csv', index_col=0)

# Vẽ biểu đồ nhiệt (Heatmap)
plt.figure(figsize=(14, 8))
sns.heatmap(corr, annot=True, fmt=".2f", cmap="coolwarm", center=0, 
            vmin=-1, vmax=1, linewidths=.5, cbar_kws={"shrink": .8})

plt.title('Spearman RHO Correlation Matrix (UGS vs Specific ESS/DES)', fontsize=16, pad=20)
plt.ylabel('UGS Types', fontsize=12)
plt.xlabel('ESS/DES Variables', fontsize=12)

# Xoay nhãn trục X để dễ đọc hơn
plt.xticks(rotation=45, ha='right')
plt.yticks(rotation=0)

plt.tight_layout()
plt.savefig('RHO_Heatmap.png', dpi=300)
corr.to_csv('RHO_Matrix.csv')
print("Heatmap saved to RHO_Heatmap.png and data to RHO_Matrix.csv")
