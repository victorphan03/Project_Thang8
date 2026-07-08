import sys
sys.stdout.reconfigure(encoding='utf-8')
import pandas as pd
import numpy as np
import statsmodels.api as sm
from scipy.optimize import minimize
from scipy.stats import norm

file_path = r'c:\Users\NASPC\Documents\Du án tại SG tháng 8\Data_VN_filter_v5_with_clusters.xlsx'
df = pd.read_excel(file_path)

numeric_vars = ['Income', 'MEAN RES', 'MEAN CES', 'MEAN DES', 
                'Literacy', 'Frequency', 'Distance', 'Time']
categorical_vars = ['Gender', 'Career', 'Transportation']

for col in numeric_vars:
    df[col] = pd.to_numeric(df[col], errors='coerce')
for col in categorical_vars:
    df[col] = df[col].astype(str)

df['Career'] = df['Career'].replace({'5.0': '4.0', '5': '4'})
df['Transportation'] = df['Transportation'].replace({'5.0': '4.0', '5': '4'})

# Lấy N=200 như script cũ để đồng bộ, hoặc lấy toàn bộ?
# Ở file run_final_logistic.py gốc, họ lấy sample 200.
# Chúng ta sẽ lọc bỏ NA và giữ toàn bộ hoặc sample. Để chính xác phản ánh N=307, ta giữ toàn bộ những dòng hợp lệ.
df_subset = df[['Donation'] + numeric_vars + categorical_vars].dropna()
print(f"Total valid samples: {len(df_subset)}")

X = pd.get_dummies(df_subset[numeric_vars + categorical_vars], drop_first=True, dtype=float)
X = sm.add_constant(X)
y = df_subset['Donation'].astype(float)

def firth_likelihood(beta, X, y):
    X = np.asarray(X)
    y = np.asarray(y)
    eta = np.dot(X, beta)
    pi = 1 / (1 + np.exp(-eta))
    eps = 1e-15
    pi = np.clip(pi, eps, 1 - eps)
    
    # Log-likelihood
    ll = np.sum(y * np.log(pi) + (1 - y) * np.log(1 - pi))
    
    # Fisher Information Matrix
    W = pi * (1 - pi)
    I = np.dot(X.T, W[:, None] * X)
    
    # Firth Penalty
    try:
        sign, logdet = np.linalg.slogdet(I)
        penalty = 0.5 * logdet if sign > 0 else 0
    except np.linalg.LinAlgError:
        penalty = 0
        
    return -(ll + penalty)

# Dùng L-BFGS-B vì ổn định hơn BFGS
initial_beta = np.zeros(X.shape[1])
res = minimize(firth_likelihood, initial_beta, args=(X, y), method='L-BFGS-B', 
               options={'disp': False, 'ftol': 1e-6, 'maxiter': 2000})

print("\nFirth Optimization Success:", res.success)

beta_firth = res.x
eta = np.dot(X, beta_firth)
pi = 1 / (1 + np.exp(-eta))
W = pi * (1 - pi)
I = np.dot(X.T, W[:, None] * X)
cov_matrix = np.linalg.inv(I)
se = np.sqrt(np.diag(cov_matrix))

z_stat = beta_firth / se
p_values = 2 * (1 - norm.cdf(np.abs(z_stat)))
odds_ratios = np.exp(beta_firth)

results_df = pd.DataFrame({
    'Beta (B)': beta_firth,
    'S.E.': se,
    'P-value': p_values,
    'Odds Ratio EXP(B)': odds_ratios
}, index=X.columns).round(4)

# Thêm Significance Stars
results_df['Significance'] = results_df['P-value'].apply(
    lambda p: '***' if p < 0.001 else ('**' if p < 0.01 else ('*' if p < 0.05 else ('.' if p < 0.10 else '')))
)

results_df = results_df.sort_values('P-value')

print("\n--- Final Firth Logistic Regression for Donation ---")
print(results_df.to_string())

# Lưu file kết quả
out_path = r'c:\Users\NASPC\Documents\Du án tại SG tháng 8\Logistic_Results_Donation_Firth.csv'
results_df.to_csv(out_path)
print(f"\nKết quả đã được lưu tại: {out_path}")
