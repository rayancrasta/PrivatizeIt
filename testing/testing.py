import pandas as pd
import os

csv_path = os.path.join('data', 'card_data.csv')
df = pd.read_csv(csv_path)
df['SSN'] = df['SSN'].str.replace('-', '')
df['Card'] = df['Card'].str.replace('-', '')

# Convert 'Card' column to numeric, coercing errors to NaN
df['Card'] = pd.to_numeric(df['Card'], errors='coerce')
# Drop rows where 'Card' column contains NaN (non-integer) values
df = df.dropna(subset=['Card'])

# Convert SSN, Card, and Name columns to appropriate data types
df['SSN'] = df['SSN'].astype(int)
df['Card'] = df['Card'].astype(int)
df['Name'] = df['Name'].astype(str)

# print(df.shape)
print(df.dtypes)

## TESTING ###


