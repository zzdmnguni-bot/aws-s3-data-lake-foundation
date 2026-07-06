import boto3
import pandas as pd
import io

s3 = boto3.client('s3', region_name='af-south-1')

# Read from raw bucket
print("Reading from raw bucket...")
response = s3.get_object(
    Bucket='ziphozethu-raw-data-lake',
    Key='nyc-taxi/year=2024/month=01/yellow_tripdata_2024-01.parquet'
)

df = pd.read_parquet(io.BytesIO(response['Body'].read()))
print(f"Rows loaded: {len(df)}")

# Basic cleaning
df = df.dropna()
df = df[df['trip_distance'] > 0]
df = df[df['fare_amount'] > 0]
print(f"Rows after cleaning: {len(df)}")

# Write cleaned data to processed bucket
buffer = io.BytesIO()
df.to_parquet(buffer, index=False)
buffer.seek(0)

s3.put_object(
    Bucket='ziphozethu-processed-data-lake',
    Key='nyc-taxi/year=2024/month=01/yellow_tripdata_2024-01_cleaned.parquet',
    Body=buffer.getvalue()
)

print("Written to processed bucket successfully!")