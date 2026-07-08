import pandas as pd

df = pd.read_excel('Data_VN_filter_v5.xlsx')
cols = df.columns.tolist()

targets = ['Donation', 'Decision']
found_targets = [c for c in targets if c in cols]

print(f"Columns found: {found_targets}")

if found_targets:
    for t in found_targets:
        valid_count = df[t].dropna().count()
        print(f"Valid rows for {t}: {valid_count}")
        print(f"Value counts for {t}:\n{df[t].value_counts()}")
        
# Check MEAN variables
mean_vars = ['MEAN RES', 'MEAN CES', 'MEAN DES']
print(f"Mean vars found: {[c for c in mean_vars if c in cols]}")
