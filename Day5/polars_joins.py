import polars as pl

# Load csv
employees = pl.read_csv("./employees.csv")
salaries = pl.read_csv("./salaries.csv")

print("Employees: ")
print(employees)

print("\nSalaries: ")
print(salaries)

# Join on emp_id
df = employees.join(salaries, on="emp_id", how="inner")

print("\nJoined Dataframe: ")
print(df)

# Add total Compensation
df = df.with_columns((pl.col("salary") + pl.col("bonus")).alias("Total_Compensation"))

print("\nWith Total Compensation")
print(df)

# Group by department and calculate average compensation
summary = df.group_by("department").agg(pl.col("Total_Compensation").mean().alias("avg_compensation"))

print("\nAverage compensation by department")
print(summary)

print("\n",summary.sort("avg_compensation",descending=True))