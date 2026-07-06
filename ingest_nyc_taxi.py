import boto3
import requests

s3 = boto3.client('s3', region_name='af-south-1')

# Download NYC taxi data (January 2024, small sample)
url = "https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2024-01.parquet"

print("Downloading NYC Taxi data...")
response = requests.get(url, stream=True)

# Upload directly to raw bucket
s3.put_object(
    Bucket='ziphozethu-raw-data-lake',
    Key='nyc-taxi/year=2024/month=01/yellow_tripdata_2024-01.parquet',
    Body=response.content
)

print("Uploaded to raw bucket successfully!")
print("File: nyc-taxi/year=2024/month=01/yellow_tripdata_2024-01.parquet")