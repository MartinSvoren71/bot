import boto3
from flask import Flask, render_template
import os
from botocore.exceptions import ClientError

app = Flask(__name__)

AWS_ACCESS_KEY_ID = 'AKIA5BVJA3S5MNPVO2MP'
AWS_SECRET_ACCESS_KEY = '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'
AWS_DEFAULT_REGION = 'eu-central-1'
BUCKET_NAME = 'knowledgevortex'

s3_client = boto3.client(
    's3',
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_DEFAULT_REGION
)

def generate_presigned_url(bucket, key, expiration=3600):
    try:
        response = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': bucket, 'Key': key},
            ExpiresIn=expiration
        )
    except ClientError as e:
        print(e)
        return None
    return response


@app.route('/')
def list_files():
    contents = s3_client.list_objects(Bucket=BUCKET_NAME)
    files = contents['Contents']

    for file in files:
        file['PresignedURL'] = generate_presigned_url(BUCKET_NAME, file['Key'])
    return render_template('indexSplit.html', files=files)

if __name__ == '__main__':
    app.run(debug=True)
