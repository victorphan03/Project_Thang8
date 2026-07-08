import pandas as pd
import numpy as np
import statsmodels.api as sm

df = pd.read_excel('Data_VN_filter_v5.xlsx')

target_vars = ['Donation']
# Removed some categorical variables that have zero variance or cause perfect separation easily
numeric_vars = ['Income', 'MEAN RES', 'MEAN CES', 'MEAN DES'] + ['Park', 'Residential', 'Garden', 'Rooftop', 'Recreation']
categorical_vars = ['Gender', 'Frequency', 'Distance', 'Time']

for col in categorical_vars:
    df[col] = df[col].astype(str)

all_vars = target_vars + numeric_vars + categorical_vars
df_subset = df[all_vars].dropna()
df_sample = df_subset.sample(n=200, random_state=42)

X = pd.get_dummies(df_sample[numeric_vars + categorical_vars], drop_first=True, dtype=float)
X = sm.add_constant(X)
y = df_sample['Donation'].astype(float)

model = sm.Logit(y, X)
try:
    result = model.fit(disp=False)
    summary_df = pd.DataFrame({
        'Beta (B)': result.params,
        'P-value': result.pvalues,
        'Odds Ratio EXP(B)': np.exp(result.params)
    }).round(4)
    summary_df['Significance'] = summary_df['P-value'].apply(lambda p: '***' if p < 0.001 else ('**' if p < 0.01 else ('*' if p < 0.05 else '')))
    summary_df = summary_df.sort_values('P-value')
    summary_df.to_csv('Logistic_Results_Donation_Optimized.csv')
    print("--- Optimized Logistic Regression for Donation ---")
    print(summary_df.head(10))
except Exception as e:
    print("Standard fit failed:", e)
    result = model.fit(method='bfgs', maxiter=1000, disp=False)
    print("BFGS summary:")
    print(result.summary())
