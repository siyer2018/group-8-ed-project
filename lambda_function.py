import processorFunctions
import json
import urllib.parse
import boto3
import uuid

print("DATA PROCESSING INITIALIZED")

s3 = boto3.client('s3')
OUTPUT_BUCKET = "output-data-processing"

def key_split(key:str)->tuple[str,str]:
    """
    Returns a tuple containing experience type and experience name
    """

    #split key into type and name
    split_key: list[str] = key.split("_")
    exp_type: str = split_key[0]
    exp_name: str = split_key[-1]
    return exp_type, exp_name

def lambda_handler(event, context):
    # Get the object from the event via key
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')
    print("Detected object is: " + str(key))
    #loop at event['Records'][i]
    file_path = '/tmp/'
    download_path = file_path + key
    s3.download_file(bucket, key, download_path)

    keyDetail: tuple[str, str] = processorFunctions.key_split(key)
    
    fileName: str = download_path + keyDetail[0] + "_" + "Processed" + "_" + keyDetail[1]
    fileName = download_path + keyDetail[0] + "_" + "Fixations" + "_" + keyDetail[1]
    processorFunctions.readData(download_path, upload_path)
    processorFunctions.getFixations(download_path, upload_path)

    s3.upload_file(upload_path, OUTPUT_BUCKET, key)
    #clear bucket
    return "File {} successfully placed in {} bucket".format(key, OUTPUT_BUCKET)
