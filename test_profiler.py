
from loader import load_dataset
from profiler import profile_dataset

df = load_dataset("sample.csv")
report = profile_dataset(df)

print("UNIVERSAL DATA PROFILER")
print("=" * 35)

for section, result in report.items():
    print(f"\n{section}:")
    print(result)
