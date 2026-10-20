from loader import load_dataset


df = load_dataset("sample.csv")

print("Dataset loaded successfully!")
print()

print("Shape:")
print(df.shape)

print()

print("Columns:")
print(df.columns.tolist())

print()

print(df.head())