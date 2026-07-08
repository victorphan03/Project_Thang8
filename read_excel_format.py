import pandas as pd
import sys
sys.stdout.reconfigure(encoding='utf-8')

file_path = r'c:\Users\NASPC\Documents\Du án tại SG tháng 8\PCA_HCA_sample\PCA n HCA.xlsx'
try:
    xls = pd.ExcelFile(file_path)
    print("Sheets in file:", xls.sheet_names)
    for sheet in xls.sheet_names:
        print(f"\n--- Sheet: {sheet} ---")
        df = pd.read_excel(file_path, sheet_name=sheet, header=None)
        print(df.head(15).to_string())
except Exception as e:
    print(f"Error reading excel file: {e}")
