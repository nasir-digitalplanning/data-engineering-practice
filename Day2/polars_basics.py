import polars as pl

# Load CSV into a Polars DataFrame
df = pl.read_csv("sample_data.csv")

# Show the full DataFrame
print("Full DataFrame:")
print(df)

# Filter: employees in IT department
it_dept = df.filter(df["department"] == "IT")
print("\nEmployees in IT:")
print(it_dept)

# Group by department and calculate average salary
avg_salary = df.group_by("department").agg(pl.col("salary").mean().alias("avg_salary"))

print("\nAverage salary by department:")
print(avg_salary)

# Sort by salary descending
sorted_df = df.sort("salary", descending=True)
print("\nEmployees sorted by salary:")
print(sorted_df)
