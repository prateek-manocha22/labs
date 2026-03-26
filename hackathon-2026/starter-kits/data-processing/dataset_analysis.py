import pandas as pd

def analyze_dataset(file_path):
    # Load dataset
    df = pd.read_csv(file_path)

    # Basic stats
    print("--- Dataset Overview ---")
    print(df.info())
    print("\n--- Missing Values ---")
    print(df.isnull().sum())

    # Quality check placeholder (e.g., duplicates)
    duplicates = df.duplicated().sum()
    print(f"\nDuplicate rows detected: {duplicates}")

    # Export a cleaned version
    # df_clean = df.drop_duplicates().dropna()
    # df_clean.to_csv('cleaned_dataset.csv', index=False)

if __name__ == "__main__":
    print("Data Processing & Quality Starter Kit")
    # analyze_dataset('your_dataset.csv')
    print("Provide a CSV path to analyze.")
