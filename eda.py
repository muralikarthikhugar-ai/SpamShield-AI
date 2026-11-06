# import pandas as pd

# df = pd.read_csv("data/spam.csv", encoding="latin-1")

# print(df.head())
# print(df.shape)
# print(df.info())
# print(df.isnull().sum())
# print(df["v1"].value_counts())

# seeing through the data, we can see that there are some extra columns that are not needed for our analysis. We will drop those columns and keep only the necessary ones. 


# import pandas as pd

# df = pd.read_csv("data/spam.csv", encoding="latin-1")

# print("Dataset shape:", df.shape)
# print("\nColumn names:")
# print(df.columns.tolist())

# print("\nFirst 10 rows:")
# print(df.head(10).to_string())

# print("\nNon-null values in extra columns:")
# for col in df.columns[2:]:
#     print(f"\n{col}:")
#     print("Non-null count:", df[col].notna().sum())
#     print(df.loc[df[col].notna(), col].head(10).tolist())

#analyzing the cleaned dataset.

# import pandas as pd

# df = pd.read_csv("data/cleaned_spam.csv")

# print("Cleaned dataset shape:", df.shape)

# print("\nColumns:")
# print(df.columns.tolist())

# print("\nFirst 10 records:")
# print(df.head(10).to_string())

# print("\nMissing values:")
# print(df.isnull().sum())

# print("\nLabel distribution:")
# print(df["label"].value_counts())

# import pandas as pd
# df= pd.read_csv("data/cleaned_spam.csv")
# print(df.shape)
# print(df.head())

#for confiramation, we can check the number of missing values and duplicates in the cleaned dataset.
import pandas as pd

df = pd.read_csv("data/cleaned_spam.csv")

print("Dataset shape:", df.shape)

print("\nMissing values:")
print(df.isnull().sum())

print("\nDuplicate messages:")
print(df.duplicated(subset=["label", "message"]).sum())

print("\nLabel distribution:")
print(df["label"].value_counts())

print("\nUnique labels:")
print(df["label"].unique())