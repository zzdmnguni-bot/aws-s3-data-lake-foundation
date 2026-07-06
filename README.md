# Project 1: S3 Data Lake Foundation

**AWS Cloud Data Engineering Portfolio — Ziphozethu Mnguni**

---

## Overview

This project implements a production-pattern, multi-zone S3 data lake on AWS. Raw source data lands in an ingestion bucket, flows through a cleaning and transformation layer, and is aggregated into an analytics-ready curated zone. The entire pipeline is driven by Python (Boto3) with no manual console interaction after initial setup.

**Dataset:** NYC Yellow Taxi Trip Records — January 2024 (~3M rows, Parquet format)  
**Source:** NYC Taxi & Limousine Commission via AWS Open Data

---

## Architecture

```
[Source Data]
      │
      ▼
┌─────────────────────────────┐
│   RAW ZONE                  │
│   ziphozethu-raw-data-lake  │
│                             │
│   nyc-taxi/                 │
│     year=2024/              │
│       month=01/             │
│         yellow_tripdata_    │
│         2024-01.parquet     │
│                             │
│   Versioning: Enabled       │
│   Lifecycle:                │
│     30d → Standard-IA       │
│     90d → Glacier           │
└────────────┬────────────────┘
             │ transform_to_processed.py
             ▼
┌─────────────────────────────────────┐
│   PROCESSED ZONE                    │
│   ziphozethu-processed-data-lake    │
│                                     │
│   Cleaned: nulls removed,           │
│   zero-distance & zero-fare         │
│   trips filtered out                │
│                                     │
│   2,754,465 rows retained           │
│   from 2,964,624 raw rows           │
│                                     │
│   Versioning: Enabled               │
└──────────────┬──────────────────────┘
               │ curate_to_curated.py
               ▼
┌─────────────────────────────────────┐
│   CURATED ZONE                      │
│   ziphozethu-curated-data-lake      │
│                                     │
│   Aggregated by PULocationID:       │
│     - avg_fare                      │
│     - avg_distance                  │
│     - total_trips                   │
│                                     │
│   253 location summaries            │
│   Analytics-ready for BI tools      │
│                                     │
│   Versioning: Enabled               │
└─────────────────────────────────────┘
```

---

## AWS Services Used

| Service | Usage |
|---------|-------|
| S3 | Multi-zone data lake storage |
| S3 Versioning | File history and recovery on all buckets |
| S3 Lifecycle Policies | Automatic cost tiering on raw zone |
| IAM | Least-privilege user (`ziphozethu-dev`) for CLI/Boto3 access |
| AWS CLI | Infrastructure provisioning from terminal |
| Boto3 | Python SDK for all S3 read/write operations |

---

## Design Decisions

**Why three separate buckets instead of one bucket with prefixes?**  
Separate buckets allow independent IAM policies per zone. In a production environment, a downstream analyst might have read access to curated only, while an ingestion service has write access to raw only. A single bucket makes this boundary harder to enforce cleanly.

**Why Parquet format?**  
Parquet is columnar — it compresses well and allows query engines like Athena or Spark to read only the columns they need rather than entire rows. This is the standard format for data lakes at scale.

**Why partition by year/month?**  
Partitioning (`year=2024/month=01/`) allows query engines to skip entire partitions when filtering by date. A query for January data never touches February files. This is a foundational performance pattern in data engineering.

**Why lifecycle policies on raw only?**  
Raw data is the highest volume and lowest query frequency zone — it's written once and rarely re-read after processing. Moving it to cheaper storage classes (Standard-IA at 30 days, Glacier at 90 days) reduces cost without impacting processed or curated zones which are accessed regularly by downstream consumers.

**Why `af-south-1` (Cape Town)?**  
Lowest latency from KwaZulu-Natal. Data residency stays on South African soil, which matters for compliance in financial and healthcare contexts.

---

## Project Structure

```
project-1-s3-data-lake/
│
├── ingest_nyc_taxi.py          # Downloads source data and lands in raw zone
├── transform_to_processed.py   # Cleans raw data, writes to processed zone
├── curate_to_curated.py        # Aggregates processed data, writes to curated zone
├── upload_to_raw.py            # Boto3 connection test (placeholder upload)
├── lifecycle-raw.json          # S3 lifecycle policy definition for raw bucket
└── README.md                   # This file
```

---

## Setup & Reproduction

### Prerequisites
- AWS account with IAM user credentials
- AWS CLI v2 installed and configured (`aws configure`)
- Python 3.x
- Dependencies: `pip install boto3 requests pandas pyarrow`

### Infrastructure (run once via CLI)

```bash
# Create buckets
aws s3api create-bucket --bucket ziphozethu-raw-data-lake --region af-south-1 --create-bucket-configuration LocationConstraint=af-south-1
aws s3api create-bucket --bucket ziphozethu-processed-data-lake --region af-south-1 --create-bucket-configuration LocationConstraint=af-south-1
aws s3api create-bucket --bucket ziphozethu-curated-data-lake --region af-south-1 --create-bucket-configuration LocationConstraint=af-south-1

# Enable versioning
aws s3api put-bucket-versioning --bucket ziphozethu-raw-data-lake --versioning-configuration Status=Enabled
aws s3api put-bucket-versioning --bucket ziphozethu-processed-data-lake --versioning-configuration Status=Enabled
aws s3api put-bucket-versioning --bucket ziphozethu-curated-data-lake --versioning-configuration Status=Enabled

# Apply lifecycle policy to raw bucket
aws s3api put-bucket-lifecycle-configuration --bucket ziphozethu-raw-data-lake --lifecycle-configuration file://lifecycle-raw.json
```

### Run the Pipeline

```bash
# Step 1 — Ingest raw data
python ingest_nyc_taxi.py

# Step 2 — Transform to processed
python transform_to_processed.py

# Step 3 — Aggregate to curated
python curate_to_curated.py
```

---

## Pipeline Results

| Stage | Rows | Notes |
|-------|------|-------|
| Raw ingestion | 2,964,624 | Full January 2024 dataset, untouched |
| Processed (cleaned) | 2,754,465 | Nulls, zero-distance, zero-fare trips removed |
| Curated (aggregated) | 253 | One row per NYC pickup location zone |

---

## Key Concepts Demonstrated

- Multi-zone data lake architecture (raw / processed / curated)
- S3 bucket provisioning and configuration via AWS CLI
- Boto3 for programmatic S3 interaction (put, get, list)
- Data cleaning and transformation with Pandas
- Columnar storage with Parquet and PyArrow
- S3 versioning for data recovery
- S3 lifecycle policies for cost management
- Partitioned folder structure for query performance
- IAM least-privilege access pattern

---

## Next Project

**Project 2: SQL Analytics Layer**  
PostgreSQL, window functions, CTEs — querying the curated data produced here with structured analytical SQL.

---

*AWS Cloud Data Engineering Portfolio — Built in KwaZulu-Natal, South Africa*  
*Region: af-south-1 (Cape Town)*