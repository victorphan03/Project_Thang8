import pandas as pd
import numpy as np

df = pd.read_excel('Data_VN_filter_v5.xlsx')
target_vars = ['Donation', 'Decision']
numeric_vars = ['Income', 'MEAN RES', 'MEAN CES', 'MEAN DES'] + ['Park', 'Residential', 'Garden', 'Rooftop', 'Recreation', 'Agriculture', 'Nature']
categorical_vars = ['Gender', 'Career', 'Literacy', 'Frequency', 'Distance', 'Time', 'Transportation']

for col in categorical_vars:
    df[col] = df[col].astype(str)

all_vars = target_vars + numeric_vars + categorical_vars
df_subset = df[all_vars].dropna()
df_sample = df_subset.sample(n=200, random_state=42) if len(df_subset) > 200 else df_subset

X = pd.get_dummies(df_sample[numeric_vars + categorical_vars], drop_first=True, dtype=float)

# Find constant columns
constant_cols = [col for col in X.columns if X[col].nunique() <= 1]
print(f"Constant columns: {constant_cols}")

# Drop constant columns
X = X.drop(columns=constant_cols)

# Find highly correlated columns
corr_matrix = X.corr().abs()
upper = corr_matrix.where(np.triu(np.ones(corr_matrix.shape), k=1).astype(bool))
to_drop = [column for column in upper.columns if any(upper[column] > 0.99)]
print(f"Highly correlated columns (>0.99): {to_drop}")
