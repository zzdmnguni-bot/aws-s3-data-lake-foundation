import boto3
import pandas as pd
import io

s3 = boto3.client('s3', region_name='af-south-1')

# Read from processed bucket
print("Reading from processed bucket...")
response = s3.get_object(
    Bucket='ziphozethu-processed-data-lake',
    Key='nyc-taxi/year=2024/month=01/yellow_tripdata_2024-01_cleaned.parquet'
)

df = pd.read_parquet(io.BytesIO(response['Body'].read()))

# Aggregate: average fare and trip distance by pickup location
print("Aggregating...")
curated = df.groupby('PULocationID').agg(
    avg_fare=('fare_amount', 'mean'),
    avg_distance=('trip_distance', 'mean'),
    total_trips=('fare_amount', 'count')
).reset_index()

print(curated.head())

# Write to curated bucket
buffer = io.BytesIO()
curated.to_parquet(buffer, index=False)
buffer.seek(0)

s3.put_object(
    Bucket='ziphozethu-curated-data-lake',
    Key='nyc-taxi/year=2024/month=01/pickup_location_summary.parquet',
    Body=buffer.getvalue()
)

print(f"\nCurated: {len(curated)} location summaries written to curated bucket!")