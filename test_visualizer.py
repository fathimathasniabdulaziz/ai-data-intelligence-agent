
from loader import load_dataset
from visualizer import generate_charts

df = load_dataset("sample.csv")
files = generate_charts(df)

print("CHART GENERATION RESULTS")
print("=" * 35)

if files:
    for file in files:
        print(f"Created: {file}")
else:
    print("No suitable charts could be generated.")

from loader import load_dataset
from visualizer import generate_charts

df = load_dataset("sample.csv")
files = generate_charts(df)

print("CHART GENERATION RESULTS")
print("=" * 35)

if files:
    for file in files:
        print(f"Created: {file}")
else:
    print("No suitable charts could be generated.")
