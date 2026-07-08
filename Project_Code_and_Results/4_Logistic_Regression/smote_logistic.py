import pandas as pd
import numpy as np
import statsmodels.api as sm
from imblearn.over_sampling import SMOTE

df = pd.read_excel('Data_VN_filter_v5.xlsx')

target_vars = ['Donation']
numeric_vars = ['Income', 'MEAN RES', 'MEAN CES', 'MEAN DES'] + ['Park', 'Residential', 'Garden', 'Rooftop', 'Recreation', 'Agriculture', 'Nature']
categorical_vars = ['Gender', 'Career', 'Literacy', 'Frequency', 'Distance', 'Time', 'Transportation']

for col in categorical_vars:
    df[col] = df[col].astype(str)

all_vars = target_vars + numeric_vars + categorical_vars
df_subset = df[all_vars].dropna()

X = pd.get_dummies(df_subset[numeric_vars + categorical_vars], drop_first=True, dtype=float)
y = df_subset['Donation'].astype(float)

# Sử dụng toàn bộ dữ liệu hợp lệ (không sample 200) để tối đa hoá thông tin
# Áp dụng thuật toán cân bằng dữ liệu SMOTE để tạo ra mẫu ảo cho nhóm thiểu số (Donation=0)
smote = SMOTE(random_state=42)
X_res, y_res = smote.fit_resample(X, y)

print(f"Data shape after SMOTE: {X_res.shape}")
print(f"Donation=1: {sum(y_res==1)}, Donation=0: {sum(y_res==0)}")

X_res = sm.add_constant(X_res)

model = sm.Logit(y_res, X_res)
try:
    result = model.fit(method='bfgs', maxiter=1000, disp=False)
    
    summary_df = pd.DataFrame({
        'Beta (B)': result.params,
        'P-value': result.pvalues,
        'Odds Ratio EXP(B)': np.exp(result.params)
    })
    
    summary_df = summary_df.round(4)
    summary_df['Significance'] = summary_df['P-value'].apply(lambda p: '***' if p < 0.001 else ('**' if p < 0.01 else ('*' if p < 0.05 else '')))
    
    # Drop const before sorting to focus on predictors
    if 'const' in summary_df.index:
        summary_df_no_const = summary_df.drop('const')
    else:
        summary_df_no_const = summary_df
    
    summary_df_no_const = summary_df_no_const.sort_values('P-value')
    summary_df_no_const.to_csv('Logistic_Results_Donation_SMOTE.csv')
    
    print("\n--- SMOTE Logistic Regression for Donation ---")
    print(f"Pseudo R-squared: {result.prsquared:.4f}")
    print(summary_df_no_const.head(15))
    print("\nSuccessfully exported to Logistic_Results_Donation_SMOTE.csv")
    
except Exception as e:
    print(f"Model failed to converge: {e}")
