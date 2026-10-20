
from loader import load_dataset
from analyzer import analyze_dataset

df = load_dataset("sample.csv")
results = analyze_dataset(df)

print("AUTOMATIC DATA ANALYSIS")
print("=" * 35)

for section, result in results.items():
    print(f"\n{section.replace('_', ' ').title()}:")
    print(result)
