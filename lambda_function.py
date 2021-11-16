import processorFunctions
import json
import urllib.parse
import boto3
import uuid

print("DATA PROCESSING INITIALIZED")

s3 = boto3.client('s3')
OUTPUT_BUCKET = "output-data-processing"

def lambda_handler(event, context):
    #print("Received event: " + json.dumps(event, indent=2))

    # Get the object from the event via key
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')
    print("Detected object is: " + str(key))
    #loop at event['Records'][i]
    download_path = '/tmp/{}{}'.format(uuid.uuid4(),key)
    upload_path = '/tmp/processed-{}'.format(key)
    s3.download_file(bucket, key, download_path)

    processorFunctions.readData(download_path, upload_path)
    processorFunctions.getFixations(download_path, upload_path)

    s3.upload_file(upload_path, OUTPUT_BUCKET, key)
    #clear bucket
    return "File {} successfully placed in {} bucket".format(key, OUTPUT_BUCKET)
