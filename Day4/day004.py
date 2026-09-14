
import polars as pl

# load csv
df = pl.read_csv("sales_data.csv")

print("Full DataFrame: ")
print(df)

# Group by region with multiple aggregations
summary = df.group_by("region").agg([
    pl.col("sales").sum().alias("total_sales"),
    pl.col("sales").mean().alias("avg_sales"),
    pl.col("profit").sum().alias("total_profit"),
    pl.col("profit").mean().alias("avg_profit"),
    pl.len().alias("num_records")
])

print("\nSummary by region:")
print(summary)

# Add derived metric: profit margin (%)
summary = summary.with_columns(
    ((pl.col("total_profit") / pl.col("total_sales")) * 100.00).alias("profit_margin"))

print("\nWith profit margin:")
print(summary)

# Region with the highest profit margin
print("Highest Profit Margin")
print(summary.sort("profit_margin",descending=True).head(1))