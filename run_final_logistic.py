import pandas as pd
import numpy as np
import statsmodels.api as sm

df = pd.read_excel('Data_VN_filter_v5.xlsx')

# Chuyển các biến Ordinal thành Numeric thay vì Dummies để giảm số chiều, tránh Phân tách hoàn hảo
numeric_vars = ['Income', 'MEAN RES', 'MEAN CES', 'MEAN DES'] + \
               ['Park', 'Residential', 'Garden', 'Rooftop', 'Recreation', 'Agriculture', 'Nature'] + \
               ['Literacy', 'Frequency', 'Distance', 'Time']

# Các biến Nominal (Phân loại danh nghĩa) thực sự
categorical_vars = ['Gender', 'Career', 'Transportation']

for col in numeric_vars:
    df[col] = pd.to_numeric(df[col], errors='coerce')

for col in categorical_vars:
    df[col] = df[col].astype(str)

# Gộp các nhóm cực nhỏ gây ra 0-cell (Career_5 gộp vào Career_4, Transportation_5 gộp vào 4)
df['Career'] = df['Career'].replace({'5.0': '4.0', '5': '4'})
df['Transportation'] = df['Transportation'].replace({'5.0': '4.0', '5': '4'})

all_vars = ['Donation', 'Decision'] + numeric_vars + categorical_vars
df_subset = df[all_vars].dropna()

print(f"Total valid samples: {len(df_subset)}")
# Lấy mẫu N=200 như yêu cầu
df_sample = df_subset.sample(n=200, random_state=42)

# Xử lý Dummy
X = pd.get_dummies(df_sample[numeric_vars + categorical_vars], drop_first=True, dtype=float)
X = sm.add_constant(X)
y = df_sample['Donation'].astype(float)

# Run model for Donation
model = sm.Logit(y, X)
try:
    result = model.fit(method='newton', maxiter=1000, disp=False)
    summary_df = pd.DataFrame({
        'Beta (B)': result.params,
        'P-value': result.pvalues,
        'Odds Ratio EXP(B)': np.exp(result.params)
    }).round(4)
    summary_df['Significance'] = summary_df['P-value'].apply(lambda p: '***' if p < 0.001 else ('**' if p < 0.01 else ('*' if p < 0.05 else '')))
    summary_df = summary_df.sort_values('P-value')
    summary_df.to_csv('Logistic_Results_Donation_Final.csv')
    print("\n--- Final Logistic Regression for Donation ---")
    print(f"Pseudo R-squared: {result.prsquared:.4f}")
    print(summary_df.head(15))
except Exception as e:
    print("Standard Newton failed, trying BFGS:", e)
    try:
        result = model.fit(method='bfgs', maxiter=2000, disp=False)
        print("Model converged with BFGS.")
        summary_df = pd.DataFrame({
            'Beta (B)': result.params,
            'P-value': result.pvalues,
            'Odds Ratio EXP(B)': np.exp(result.params)
        }).round(4)
        print(summary_df.head(10))
    except Exception as e2:
        print("Failed totally:", e2)

# Chạy luôn cho Decision để đồng bộ
y_dec = df_sample['Decision'].astype(float)
model_dec = sm.Logit(y_dec, X)
res_dec = model_dec.fit(method='newton', maxiter=1000, disp=False)
sum_dec = pd.DataFrame({
    'Beta (B)': res_dec.params,
    'P-value': res_dec.pvalues,
    'Odds Ratio EXP(B)': np.exp(res_dec.params)
}).round(4)
sum_dec['Significance'] = sum_dec['P-value'].apply(lambda p: '***' if p < 0.001 else ('**' if p < 0.01 else ('*' if p < 0.05 else '')))
sum_dec = sum_dec.sort_values('P-value')
sum_dec.to_csv('Logistic_Results_Decision_Final.csv')
print("\n--- Final Logistic Regression for Decision ---")
print(sum_dec.head(10))
