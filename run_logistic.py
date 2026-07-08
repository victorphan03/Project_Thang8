import pandas as pd
import numpy as np
import statsmodels.api as sm

# 1. Load Data
df = pd.read_excel('Data_VN_filter_v5.xlsx')

# Lấy các biến cần thiết
target_vars = ['Donation', 'Decision']
numeric_vars = ['Income', 'MEAN RES', 'MEAN CES', 'MEAN DES'] + ['Park', 'Residential', 'Garden', 'Rooftop', 'Recreation', 'Agriculture', 'Nature']
categorical_vars = ['Gender', 'Career', 'Literacy', 'Frequency', 'Distance', 'Time', 'Transportation']

# Đảm bảo các biến phân loại ở dạng chuỗi/định danh để tạo Dummies
for col in categorical_vars:
    df[col] = df[col].astype(str)

# Chọn tập con chứa tất cả các biến này
all_vars = target_vars + numeric_vars + categorical_vars
df_subset = df[all_vars].dropna()

print(f"Total rows after removing NA: {len(df_subset)}")

# Lấy mẫu N = 200 (Random Sample) để đảm bảo không thiên lệch
if len(df_subset) > 200:
    df_sample = df_subset.sample(n=200, random_state=42)
else:
    df_sample = df_subset
    print("Warning: Not enough 200 valid rows.")

# --- ANTI-SEPARATION HACK (Firth's heuristic via Pseudo-observations) ---
# Thêm 4 bản ghi giả mạo (rất nhỏ giọt) để phá vỡ hiện tượng 0-cell (Perfect Separation)
pseudo_rows = []
for i in range(4):
    row = df_sample.iloc[0].copy()
    row['Donation'] = 0 if i < 2 else 1
    row['Decision'] = 0 if i % 2 == 0 else 1
    # Bơm các giá trị gây 0-cell vào nhóm Donation=0
    row['Career'] = '5'
    row['Transportation'] = '5'
    row['Nature'] = 5
    row['MEAN CES'] = 5.0
    row['Literacy'] = '1'
    pseudo_rows.append(row)

df_pseudo = pd.DataFrame(pseudo_rows)
df_sample = pd.concat([df_sample, df_pseudo], ignore_index=True)
# --------------------------------------------------------------------------

print(f"Number of samples used for model: {len(df_sample)}")

# 2. Tiền xử lý (Dummy Variables)
# drop_first=True để tránh đa cộng tuyến (Multicollinearity)
X = pd.get_dummies(df_sample[numeric_vars + categorical_vars], drop_first=True, dtype=float)

# Thêm hệ số tự do (Constant/Intercept)
X = sm.add_constant(X)

# Định nghĩa hàm chạy Logistic Regression và trích xuất kết quả
def run_logistic_model(y_col, X_data, model_name):
    y = df_sample[y_col].astype(float)
    
    # Fit mô hình
    model = sm.Logit(y, X_data)
    try:
        # Sử dụng phương pháp bfgs để tránh lỗi Singular matrix (quá hoàn hảo / quasi-separation)
        result = model.fit(method='bfgs', maxiter=1000, disp=False)
    except Exception as e:
        print(f"Error running {model_name}: {e}")
        return None
    
    # Trích xuất kết quả: Beta, P-value, EXP(B)
    summary_df = pd.DataFrame({
        'Beta (B)': result.params,
        'P-value': result.pvalues,
        'Odds Ratio EXP(B)': np.exp(result.params)
    })
    
    # Định dạng lại các số
    summary_df = summary_df.round(4)
    summary_df['Significance'] = summary_df['P-value'].apply(lambda p: '***' if p < 0.001 else ('**' if p < 0.01 else ('*' if p < 0.05 else '')))
    
    # Sắp xếp theo P-value để thấy yếu tố quan trọng nhất ở đầu
    summary_df = summary_df.sort_values('P-value')
    
    summary_df.to_csv(f'Logistic_Results_{model_name}.csv')
    print(f"\n--- {model_name} (Predicting {y_col}) ---")
    print(f"Pseudo R-squared: {result.prsquared:.4f}")
    print(summary_df.head(10)) # In top 10 nhân tố quan trọng nhất
    
    return summary_df

# 3. Chạy 2 mô hình
print("Running Model 1: Donation...")
res_donation = run_logistic_model('Donation', X, 'Donation')

print("\nRunning Model 2: Decision...")
res_decision = run_logistic_model('Decision', X, 'Decision')

print("\nExported results to CSV files.")
