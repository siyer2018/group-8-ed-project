import random
import csv
import boto3
import os
from botocore.exceptions import NoCredentialsError

CSV_NAME: str = 'data.csv'
CSV_HEADER: list[str] = ['DATA','EXPERIENCE']
MAXIMUM_DIMENSION: int = 200
EXP_DURATION: int = 30
EXP_NAME: str = 'ball_go_zoom'
EXP_TYPE: str = '2D' #TYPE = 'AR' or '2D' or 'RL'

def generateFakeData(lengthOfList:int=EXP_DURATION)->list:
    """
    Returns list of length=lengthOfList with random ints (x,y) at each index
    """
    fakeData=[]
    for index in range(lengthOfList):
        fakeData.append(xyTuple=(random.randint(0,MAXIMUM_DIMENSION),random.randint(0,MAXIMUM_DIMENSION)))
    return fakeData

def createFakeCSV()->None:
    """
    Create CSV file or replace existing csv
    Use for generating a fake csv file
    """
    if os.path.exists(CSV_NAME):
        os.remove(CSV_NAME)
    with open(CSV_NAME,'w') as data:
        writer=csv.writer(data)
        writer.writerow(CSV_HEADER)
        writer.writerow(generateFakeData(),EXP_TYPE,EXP_NAME)
    return

def readData()->None:
    """
    Read data from Unity CSV
    """
    return

def getKeys()->tuple:
    """
    Get keys from keys.txt
    """
    #Read your own keys from keys.txt and define below
    #ACCESS_KEY=
    #SECRET_KEY=
    return#(ACCESS_KEY,SECRET_KEY)

def initializeRun()->None:
    """
    Run all starting functions
    """
    createFakeCSV()
    ACCESS_KEY,SECRET_KEY = getKeys()
    return

def upload_to_aws(local_file, bucket, s3_file)->bool:
    s3 = boto3.client('s3', aws_access_key_id=ACCESS_KEY,
                      aws_secret_access_key=SECRET_KEY)
    try:
        s3.upload_file(local_file, bucket, s3_file)
        print("Upload Successful")
        return True
    except FileNotFoundError:
        print("The file was not found")
        return False
    except NoCredentialsError:
        print("Credentials not available")
        return False

#initializeRun()
#upload_to_aws('local_file', 'bucket_name', 's3_file_name')