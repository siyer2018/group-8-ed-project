from numpy.lib.shape_base import split
import processorFunctions
import urllib.parse
import boto3


s3 = boto3.client('s3')
OUTPUT_BUCKET = "output-data-processing"

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
    # print("Detected object is: " + str(key))
    exp_part: dict[str] = key_split(key)
    file_part = {
        "Raw": key,
        "Processed": exp_part["type"] + "_Processed_" + exp_part["name"],
        "Fixations": exp_part["type"] + "_Fixations_" + exp_part["name"],
        "path": "s3://",
        "folder": "tmp/",
        "bucket": bucket + "/",
        "output": OUTPUT_BUCKET + "/"}
    processorFunctions.environment(file_part)
    #clear input bucket
    s3.delete_object(bucket, key)
    return "File {} successfully uploaded".format(key)
