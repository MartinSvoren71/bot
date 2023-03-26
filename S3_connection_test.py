import boto3

# Replace these values with your own access key ID and secret access key
aws_access_key_id = 'AKIA5BVJA3S5MNPVO2MP'
aws_secret_access_key = 'QspohE+8VYcwJzA18cvfQJQZFst2q+WEgMtqvC1A'
aws_default_region = 'eu-central-1'

# Create an S3 client
s3_client = boto3.client(
    's3',
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key,
    region_name=aws_default_region
)

# Name of your S3 bucket
bucket_name = 'knowledgevortex'

# List the contents of your S3 bucket
def list_bucket_contents():
    response = s3_client.list_objects_v2(Bucket=bucket_name)
    for content in response.get('Contents', []):
        print(content['Key'])

if __name__ == '__main__':
    list_bucket_contents()
