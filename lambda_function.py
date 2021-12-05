import processorFunctions

import awswrangler as wr
import urllib.parse
import boto3


ACCESS_KEY: str = 'X'
SECRET_KEY: str = 'X'
OUTPUT_BUCKET = "output-data-processing"
s3 = boto3.client('s3')

def key_split(key:str)->dict[str]:
    """
    Returns a dict containing experience type and experience name
    """
    split_key: list[str] = key.split("_")
    exp_part = {
        "type": split_key[0],
        "name": split_key[-1]}
    return exp_part

def lambda_handler(event, context):
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')
    exp_part: dict[str] = key_split(key)
    file_part = {
        "Raw": key,
        "Processed": exp_part["type"] + "_Processed_" + exp_part["name"],
        "Fixations": exp_part["type"] + "_Fixations_" + exp_part["name"],
        "Meta": exp_part["type"] + "_Meta_" + exp_part["name"],
        "path": "s3://",
        "folder": "tmp/",
        "bucket": bucket + "/",
        "output": OUTPUT_BUCKET + "/"}
    session = boto3.Session(
        aws_access_key_id=ACCESS_KEY,
        aws_secret_access_key=SECRET_KEY)
    processorFunctions.environment(file_part, session)
    wr.s3.delete_objects(path=file_part["path"]+file_part["bucket"]+file_part["Raw"], boto3_session=session)
    return
