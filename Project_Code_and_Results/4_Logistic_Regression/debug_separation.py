import pandas as pd
import numpy as np

df = pd.read_excel('Data_VN_filter_v5.xlsx')
target_vars = ['Donation']
numeric_vars = ['Income', 'MEAN RES', 'MEAN CES', 'MEAN DES'] + ['Park', 'Residential', 'Garden', 'Rooftop', 'Recreation', 'Agriculture', 'Nature']
categorical_vars = ['Gender', 'Career', 'Literacy', 'Frequency', 'Distance', 'Time', 'Transportation']

for col in categorical_vars:
    df[col] = df[col].astype(str)

all_vars = target_vars + numeric_vars + categorical_vars
df_subset = df[all_vars].dropna()
df_sample = df_subset.sample(n=200, random_state=42)

X = pd.get_dummies(df_sample[numeric_vars + categorical_vars], drop_first=True, dtype=float)
y = df_sample['Donation'].astype(float)

print("Zero variance columns:")
zero_var = X.columns[X.var() == 0]
print(zero_var.tolist())

print("\nCross tab checks (looking for 0 counts):")
for col in X.columns:
    crosstab = pd.crosstab(X[col], y)
    if (crosstab == 0).any().any():
        print(f"{col} has 0-cells!")
        print(crosstab)
