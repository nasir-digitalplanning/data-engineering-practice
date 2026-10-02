import logging
import json
from pathlib import Path
from contextlib import contextmanager
import polars as pl
from typing import Generator

logging.basicConfig(level=logging.INFO,
            format="%(asctime)s %(levelname)s %(message)s")

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

class PriceChangeDataPipeline:

    def __init__(self, config_file: dict[str,str]):
        self.csv_file_path = config_file.get("csv_product_price_file")

    @contextmanager
    def _load_csv(self) -> Generator[pl.DataFrame, None, None]:
        try:
            df = pl.read_csv(self.csv_file_path, separator=",")
            yield df
        except FileNotFoundError as e:
            logging.error(f"Failed to load CSV file {self.csv_file_path}. Error: {e}")
            raise

    def analyze_price_changes(self) -> pl.DataFrame:
        with self._load_csv() as dataset:
            df = dataset
        df = df.with_columns(
            pl.col("date").str.strptime(pl.Date, "%Y-%m-%d").alias("parsed_date")
        ).sort(["product","parsed_date"])

        df = df.with_columns(
            pl.col("price").shift(1).over("product").alias("prev_price")
        )

        df = df.with_columns([
            (pl.col("price") - pl.col("prev_price")).alias("price_diff"),
            ((pl.col("price") - pl.col("prev_price")) / pl.col("prev_price") * 100)
            .round(2).alias("pct_change")
        ])
        return df

def main():
    try:
        config = ConfigLoader.load_config()
        trend_analysis = PriceChangeDataPipeline(config)

        # Step 1: Print raw data
        with trend_analysis._load_csv() as df:
            print("--- Step 1: Product Price Change Tracker Raw Dataset")
            print(df)

        # Step 2: Track price changes over time
        price_change = trend_analysis.analyze_price_changes()
        print("--- Step 2: Product price change analysis ")
        print(price_change)

    except Exception as e:
        raise

if __name__ == "__main__":
    main()
