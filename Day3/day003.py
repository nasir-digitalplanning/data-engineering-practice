import polars as pl

# Load csv
df = pl.read_csv("employee_data.csv")

print("Full DataFrame: ")
print(df)

# Calculate total compensation (salary + bonus)
df = df.with_columns((pl.col("salary") + pl.col("bonus")).alias("total_compensation"))

print("\nWith total compensation: ")
print(df)

# Group by department and find max total compensation
max_comp = df.group_by("department").agg(pl.col("total_compensation").max().alias("max_total_comp"))

print("\nMax compensation by department: ")
print(max_comp)