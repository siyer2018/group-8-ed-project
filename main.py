import random
import csv
import boto3
import pandas as pd
import os
from botocore.exceptions import NoCredentialsError

CSV_NAME: str = 'data.csv'
CSV_HEADER: list[str] = ['DATA','EXPERIENCE']
KEY_FILE: str = 'keys.txt'
MAXIMUM_DIMENSION: int = 200
EXP_DURATION: int = 30
EXP_NAME: str = 'ball_go_zoom'
EXP_TYPE: str = '2D' #TYPE = 'AR' or '2D' or 'RL'
AR_BUCKET: str
TWOD_BUCKET: str
RL_BUCKET: str
TEST_BUCKET = 'apuentebuckettest'

def createFakeCSV()->None:
    """
    Create CSV file or replace existing csv
    Use for generating a fake csv file
    """
    def generateFakeData(lengthOfList:int=EXP_DURATION)->list[int]:
        """
        Returns list of length=lengthOfList with random ints (x,y) at each index
        """
        fakeData=[]
        for index in range(lengthOfList):
            fakeData.append((random.randint(0,MAXIMUM_DIMENSION),random.randint(0,MAXIMUM_DIMENSION)))
        return fakeData
    
    if os.path.exists(CSV_NAME): os.remove(CSV_NAME)
    CSV_filler: list[str] = [
        str(generateFakeData()).strip('[]'),
        EXP_NAME
    ]
    with open(CSV_NAME,'w') as data:
        writer=csv.writer(data)
        writer.writerow(CSV_HEADER)
        writer.writerow(CSV_filler)#writes to row[2], not row[1]? fix!
    return

def readData()->None:
    """
    Read data from Unity CSV
    """
    if os.path.exists(CSV_NAME): os.remove(CSV_NAME)
    return

def getKeys()->tuple:
    """
    Get keys from keys.txt
    """
    f=open(KEY_FILE)
    access = f.readline().split('=')[1].strip()
    secret = f.readline().split('=')[1].strip()
    return access,secret

def upload_to_aws(local_file, bucket, s3_file)->bool:
    ACCESS_KEY,SECRET_KEY = getKeys()
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

createFakeCSV()
#upload_to_aws(CSV_NAME,TEST_BUCKET,CSV_NAME)