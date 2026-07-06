import boto3

s3 = boto3.client('s3', region_name='af-south-1')

bucket_name = 'ziphozethu-raw-data-lake'

# Create partitioned folder structure with a placeholder file
s3.put_object(
    Bucket=bucket_name,
    Key='nyc-taxi/year=2024/month=01/placeholder.txt',
    Body=b'test'
)

print("Upload successful!")

# List what's in the bucket
response = s3.list_objects_v2(Bucket=bucket_name)
for obj in response.get('Contents', []):
    print(obj['Key'])