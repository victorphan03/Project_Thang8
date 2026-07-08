import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import json

df = pd.read_excel('Data_VN_filter_v5.xlsx')

# Tùy chỉnh font chữ matplotlib nếu cần
plt.rcParams.update({'font.size': 12})

output_data = {}

# 1. Kiểm tra biến Tuổi (Age)
if 'Age' in df.columns:
    # Convert age to numeric just in case
    age_data = pd.to_numeric(df['Age'], errors='coerce').dropna()
    stat, p = stats.shapiro(age_data)
    output_data['Age'] = {
        'Mean': age_data.mean(),
        'Std': age_data.std(),
        'Min': age_data.min(),
        'Max': age_data.max(),
        'Shapiro-Wilk_W': stat,
        'Shapiro-Wilk_p': p,
        'Normal_Distribution': bool(p > 0.05)
    }
    
    # Plot Age histogram
    plt.figure(figsize=(8, 5))
    sns.histplot(age_data, kde=True, color='skyblue')
    plt.title('Phân phối Tuổi (Age)')
    plt.xlabel('Tuổi')
    plt.ylabel('Tần số')
    plt.savefig('Age_Distribution.png', dpi=300, bbox_inches='tight')
    plt.close()

# 2. Nhân khẩu học (Demographics)
demo_cols = ['Gender', 'Income', 'Literacy', 'Career']
fig, axes = plt.subplots(2, 2, figsize=(16, 12))
fig.suptitle('Cơ cấu Nhân khẩu học của Mẫu Khảo sát (N = 307)', fontsize=18, fontweight='bold', y=1.02)

for i, col in enumerate(demo_cols):
    if col in df.columns:
        ax = axes[i//2, i%2]
        val_counts = df[col].value_counts()
        
        # Nếu biến có quá nhiều giá trị (như Income), vẽ Histogram thay vì Pie chart
        if len(val_counts) > 10 or col == 'Income':
            numeric_data = pd.to_numeric(df[col], errors='coerce').dropna()
            sns.histplot(numeric_data, kde=True, ax=ax, color='coral', bins=20)
            ax.set_title(f'Phân phối {col}', fontsize=14, pad=10)
            ax.set_xlabel(col)
            ax.set_ylabel('Tần số')
        else:
            # Plot Pie Chart cho biến phân loại
            wedges, texts, autotexts = ax.pie(val_counts, autopct='%1.1f%%', startangle=140, 
                                              colors=sns.color_palette('Set2'), pctdistance=0.8)
            ax.legend(wedges, val_counts.index, title=col, loc="center left", bbox_to_anchor=(1, 0.5))
            ax.set_title(f'Tỷ lệ {col}', fontsize=14, pad=10)
        
        output_data[col] = df[col].value_counts(normalize=True).mul(100).round(1).to_dict()

plt.tight_layout()
plt.savefig('Demographics_Charts.png', dpi=300, bbox_inches='tight')
plt.close()

# 3. Thói quen tương tác (Interactions)
habit_cols = ['Distance', 'Frequency', 'Time', 'Transportation']
output_data['Habits'] = {}
for col in habit_cols:
    if col in df.columns:
        counts = df[col].value_counts()
        pcts = df[col].value_counts(normalize=True).mul(100).round(1)
        output_data['Habits'][col] = {str(k): f"{pcts[k]}% (n={counts[k]})" for k in counts.index}

# 4. Các hoạt động phổ biến (Activities)
# Bảng hỏi thường dùng Yes/No (1/0) hoặc Likert. Tính tỷ lệ % chọn Yes (1).
act_cols = ['Jogging', 'Workout', 'Pet', 'Sightseeing', 'Talking', 'Photography']
output_data['Activities'] = {}
for col in act_cols:
    # Nếu biến là 'Pet Walking' thay vì 'Pet'
    actual_col = col if col in df.columns else (col + ' Walking' if col + ' Walking' in df.columns else None)
    if actual_col:
        mean_val = pd.to_numeric(df[actual_col], errors='coerce').mean()
        # Nếu mean < 1.5, có thể là dữ liệu nhị phân (0-1), ngược lại là Likert
        output_data['Activities'][actual_col] = round(mean_val, 2)

# Save summary to JSON
with open('descriptive_output.json', 'w', encoding='utf-8') as f:
    json.dump(output_data, f, ensure_ascii=False, indent=4)

print("Descriptive statistics run complete. Outputs saved.")
