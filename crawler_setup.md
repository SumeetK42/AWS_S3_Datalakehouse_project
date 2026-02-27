# AWS Glue Crawler Setup Guide

## Crawler Name
`csv-datalake-crawler`

---

# Overview

This Glue Crawler scans raw CSV stock data stored in Amazon S3 and creates metadata tables in the AWS Glue Data Catalog for querying through Amazon Athena.

---

# Step 1: Set Crawler Properties

**Name:**  
`csv-datalake-crawler`

**Description:**  
This crawler scans CSV stock price data in the Data Lake raw layer.

---

# Step 2: Choose Data Sources and Classifiers

## Data Source Configuration

| Property | Value |
|----------|-------|
| Type | S3 |
| S3 Path | `s3://hyn-motor-stock-datalake/raw/` |
| Recrawl Behavior | Recrawl all |

### Notes:
- The crawler scans the entire raw layer.
- Recrawl all ensures metadata is updated whenever new files are added.

---


### IAM Role Requirement

| IAM Role | `AwsGlueETLRole` |

The role `AwsGlueETLRole` must have permissions for:

- Reading from S3 raw bucket
- Writing to Glue Data Catalog
- Logging to CloudWatch

---


# Step 4: Create Database and Set Output and Scheduling

- Go to AWS Glue Console → Data Catalog → Databases → Click **Add database**.
- Enter Database name: `hyn_stocks_db`.
- (Optional) Add description: Stock Data Lake metadata database.
- Click **Create database** and verify it appears in the Glue Data Catalog and Athena.

| Setting | Value |
|----------|-------|
| Database | `hyn_stocks_db` |
| Table Prefix | `stocks_` |

### Behavior

- Tables created will follow this naming pattern:
  
  ```
  stocks_<folder_name>
  ```

- Example table name:
  
  ```
  stocks_raw
  ```

- Since schedule is **On demand**, the crawler must be manually triggered after new data is added.

---

# Expected Outcome

After running the crawler:

- A table will be created in:
  
  ```
  Glue Data Catalog → hyn_stocks_db
  ```

- The table will point to:
  
  ```
  s3://hyn-motor-stock-datalake/raw/
  ```

- The table can be queried using Amazon Athena.

---

# Architecture Context

Raw CSV Data (S3)  
→ Glue Crawler  
→ Glue Data Catalog Table  
→ Athena Query Engine  

---

# Environment

Project: Motor Stock Data Lake  
Layer: Raw (Bronze)  
Format: CSV  
Query Engine: Amazon Athena  

---