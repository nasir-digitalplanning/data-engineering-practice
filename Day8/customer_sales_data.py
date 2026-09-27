import logging
import polars as pl
import json
from pathlib import Path

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s [%(levelname)s]: %(message)s")

class ConfigLoader:
    """Load configuration settings from file path"""

    @staticmethod
    def load_config(config_file="config.json"):
        path = Path(config_file)
        if not path.exists():
            logging.error(f"Configuration file is not available in path: {path.resolve()}")
            raise FileNotFoundError(f"Config file {config_file} is not found")

        with path.open("r") as f:
            return json.load(f)

def _load_csv(csv_file_path):
    """Helper function to load csv file using polars"""
    try:
        path = Path(csv_file_path)
        df = pl.read_csv(csv_file_path, separator=",")
        logging.info(f"Loaded {path.name} with {df.shape[0]} rows and {df.shape[1]} columns")
        return df
    except Exception as e:
        logging.error(f"Failed to load CSV file {csv_file_path.name}. Error: {e}")
        raise

class CustomerPurchaseReport:
    """Day 8 Challenge: Find customer purchase pattern using polars"""

    def __init__(self, config):
        self.customer_file = config.get("csv_customer_sales_file")

        # Load dataframe
        self.customer_df = _load_csv(self.customer_file)

    def print_dataset(self):
        return self.customer_df

    def generate_ranking(self):

        logging.info("Computing Rank based on products per customer by spend")

        ranking = (self.customer_df.group_by(
        ["customer_id","product"])
                   .agg(pl.col("amount").sum().alias("Total_Spend"))
                   .with_columns(pl.col("Total_Spend")
                    .rank(method="dense",descending=True).over("customer_id").alias("Rank")))

        return ranking

    def total_spend_by_customer(self):
        logging.info("Computing Total Spending by each customer")

        spending = self.customer_df.group_by(
            pl.col("customer_id")).agg(pl.col("amount").sum().alias("Total_Spending"))

        return spending

def main():
    try:
        config = ConfigLoader.load_config()
        customer_report = CustomerPurchaseReport(config)

        # Step 1: Print raw data
        customer_df = customer_report.print_dataset()
        print("--- Step 1: Raw Customer Purchases ---")
        print(customer_df)

        # Step 2: Ranking of Products
        ranking_report = customer_report.generate_ranking()
        print("--- Step 2: Ranking by Product ---")
        print(ranking_report.sort(["customer_id","Rank"],descending=[False,False]))

        # Step 3: Ranking of Products
        spending_report = customer_report.total_spend_by_customer()
        print("--- Step 3: Spending Report ---")
        print(spending_report.sort("customer_id"))

        # Step 4: Top Product Per Customer
        top_product = ranking_report.filter(pl.col("Rank") == 1)
        print("--- Step 4: Top Product Per Customer Based on Spending")
        print(top_product.select(["customer_id","product"]).sort(["customer_id"]))

    except Exception as e:
        raise

if __name__ == "__main__":
    main()

