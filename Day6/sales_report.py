import logging
import json
import polars as pl
from pathlib import Path

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s [%(levelname)s]: %(message)s")

class LoadConfig:

    @staticmethod
    def load_config(config_file="config.json"):
        path = Path(config_file)
        if not path.exists():
            logging.error(f"Configuration file not found at: {path.resolve()}")
            raise FileNotFoundError(f"Missing configuration file: {config_file}")

        with path.open("r") as f:
            return json.load(f)

class SalesReport:

    def __init__(self, config):
        self.csv_path = config.get("csv_file_path")

        # Extract column names from config
        col_config = config.get("columns")
        self.col_sales = col_config.get("sales","Sales_Numbers")
        self.col_region = col_config.get("region","Region")

        # Load dataframe
        self.sales = self._load_csv()

    def _load_csv(self):
        try:
            df = pl.read_csv(self.csv_path,separator=",")
            logging.info(f"Loaded {df.shape[0]} rows and {df.shape[1]} columns from {self.csv_path}")
            return df
        except Exception as e:
            logging.error(f"Failed to load CSV file: {e}")
            raise

    def print_sales_data(self):
        return self.sales

    def generate_all_analytics(self):
        logging.info("Computing running totals, moving averages and ranking...")
        return self.sales.with_columns(
            # Running Totals
            pl.col(self.col_sales)
            .cum_sum().over(self.col_region)
            .alias("Running_Totals"),
            # Moving Averages
            pl.col(self.col_sales)
            .rolling_mean(window_size=3, min_samples=1)
            .over(self.col_region).round(2)
            .alias("3_Days_Avg"),
            # Ranking using Dense
            pl.col(self.col_sales)
            .rank(method="dense", descending= True)
            .over(self.col_region)
            .alias("Rank"),
            )

def main():
    try:
        config = LoadConfig.load_config()
        sales_report = SalesReport(config)

        # Step 1: Print Raw Data
        logging.info("--- Step 1: Raw Sales Data ---")
        print(sales_report.print_sales_data())

        # Step 2: Compute and Print All metrics at once
        logging.info("--- Step 2: Full Analytics Report ---")
        analytics_df = sales_report.generate_all_analytics()
        print(analytics_df)

    except Exception as e:
        logging.critical(f"Pipeline execution aborted: {e}")

if __name__ == "__main__":
    main()




