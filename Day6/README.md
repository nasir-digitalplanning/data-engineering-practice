# Day 6 - Polars Window Functions

## 📂 Project Overview
This project demonstrates the use of **window functions in Polars** to analyze sales data.  
Key concepts covered:
- Running totals per region
- 3-day moving averages
- Rankings within each region

## 📊 Dataset
**File:** `sales_data.csv`  
**Columns:**
- `Sales_Date` → Date of sale (DD-MM-YYYY format)
- `Region` → Sales region (North, South, East, West)
- `Sales_Numbers` → Daily sales figures

## 🧩 Transformations
1. **Running Totals**  
   Cumulative sum of sales per region.

2. **Moving Average (3 days)**  
   Rolling mean of sales numbers per region.

3. **Rankings**  
   Dense rank of sales within each region.

## 🖥️ How to Run
```bash
python sales_report.py
