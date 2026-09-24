import json
import logging
from pathlib import Path
import polars as pl

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s [%(levelname)s]: %(message)s")

class ConfigLoader:
    """Load config settings from file path"""

    @staticmethod
    def load_config(config_file="config.json"):
        path = Path(config_file)
        if not path.exists():
            logging.error(f"Configuration file is not available in path: {path.resolve()}")
            raise FileNotFoundError(f"Config file {config_file} is not found")

        with path.open("r") as f:
            return json.load(f)

def _load_csv(db_path):
    """Helper function to load dataframe"""
    try:
        path = Path(db_path)
        df = pl.read_csv(db_path, separator="\t")
        logging.info(f"Loaded {path.name} with {df.shape[0]} rows and {df.shape[1]} columns")
        return df
    except Exception as e:
        logging.error(f"Failed to load CSV file, ERROR: {e}")
        raise

class SalesReport:
    """Builds day 7 challenge joins using polars"""

    def __init__(self, config):
        self.sales_file = config.get("csv_sales_file")
        self.target_file = config.get("csv_targets_file")

        # Sales file columns
        col_config = config.get("sales_columns",{})
        self.sales_col_date = col_config.get("date","date")
        self.sales_col_regions = col_config.get("region","regions")
        self.sales_col_amount = col_config.get("sales_amount","sales")

        # Target file columns
        col_config = config.get("targets_columns",{})
        self.target_col_region = col_config.get("region","region")
        self.target_col_target = col_config.get("target","target")

        # Load dataframe
        self.sales_df = _load_csv(self.sales_file)
        self.target_df = _load_csv(self.target_file)

    def print_dataset(self):
        return self.sales_df, self.target_df

    def generate_all_reports(self):
        """Aggregate monthly sales per region, join with targets, and flag 90% achievement"""

        logging.info("Computing monthly sales vs targets...")

        # Step 1: Parse date and extract both month number and month name
        sales_with_month = (
            self.sales_df
            .with_columns(
                pl.col(self.sales_col_date).str.strptime(pl.Date, "%d-%m-%Y").alias("parsed_date")
            )
            .with_columns([
                pl.col("parsed_date").dt.month().alias("month_num"),   # numeric month
                pl.col("parsed_date").dt.strftime("%b").alias("month_name")  # short name
            ])
        )

        # Step 2: Aggregate monthly sales per region
        monthly_sales = (
            sales_with_month
            .group_by([self.sales_col_regions, "month_num", "month_name"])
            .agg(pl.col(self.sales_col_amount).sum().alias("monthly_sales"))
        )

        # Step 3: Join with targets
        joined = monthly_sales.join(
            self.target_df,
            left_on=self.sales_col_regions,
            right_on=self.target_col_region,
            how="left"
        )
        print(joined)
        # Step 4: Compute achievement % and flag 90% threshold
        report = joined.with_columns(
            (pl.col("monthly_sales") / pl.col(self.target_col_target) * 100).round(2).alias("achievement_pct"),
            (pl.col("monthly_sales") >= pl.col(self.target_col_target) * 0.9).alias("met_90pct")
        )

        # Step 5: Sort by numeric month for chronological order
        return report.sort(["month_num", self.sales_col_regions])

def main():
    try:
        config = ConfigLoader.load_config()
        sales_report = SalesReport(config)

        # Step 1: Print raw data
        sales, target = sales_report.print_dataset()
        print("--- Raw Sales Data ---")
        print(sales)

        print("\n--- Raw Target Data ---")
        print(target)

        print("\n--- Monthly Sales vs Targets ---")
        print(sales_report.generate_all_reports())

    except Exception as e:
        logging.critical(f"Pipeline execution aborted: {e}")

if __name__ == "__main__":
    main()
