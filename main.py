import random
import boto3
import pandas as pd
import os
from botocore.exceptions import NoCredentialsError

CSV_HEADER: list[str] = ['DATA','EXPERIENCE']
KEY_FILE: str = 'keys.txt'
EXP_DURATION: int = 30
EXP_NAME: str = 'ball_go_zoom'
EXP_TYPE: str = '2D' #TYPE = 'AR' or '2D' or 'RL'
OFFICIAL_BUCKET: str = 'ed1-eye-tracker'
TEST_BUCKET: str = 'apuentebuckettest'

def findCSV()->str:
    """
    Returns string representing path leading to first CSV file detected
    """
    for file in os.listdir(os.getcwd()):
        if file.endswith('.csv'):
            return os.path.join(os.getcwd(),file),file
    print("No CSV file found.")
    return None,'data.csv'
CSV_PATH, CSV_NAME = findCSV()

def createFakeCSV()->None:
    """
    Create CSV file or replace existing csv
    Use for generating a fake csv file
    """
    def generateFakeData(lengthOfList:int=EXP_DURATION)->list[int]:
        """
        Returns list of length=lengthOfList with random ints (x,y) at each index
        """
        fakeData:list[int]=[]
        for index in range(lengthOfList):
            fakeData.append((random.randint(0,200),random.randint(0,200)))
        return fakeData
    if CSV_PATH is not None: os.remove(CSV_PATH)
    data = {
        'DATA':generateFakeData(),
        'EXPERIENCE':[EXP_NAME]*EXP_DURATION
    }
    pd.DataFrame(data).to_csv(CSV_NAME,index=False)
    return



def readData()->None:
    """
    Read data from Unity CSV
    """
    df = pd.read_csv(CSV_PATH)
    df = df['EXPERIENCE'] = EXP_NAME*df.shape(0)
    return


def upload_to_aws(local_file, bucket, s3_file)->bool:
    f=open(KEY_FILE)
    ACCESS_KEY = f.readline().split('=')[1].strip()
    SECRET_KEY = f.readline().split('=')[1].strip()
    s3 = boto3.client('s3', aws_access_key_id=ACCESS_KEY,
                      aws_secret_access_key=SECRET_KEY)
    try:
        s3.upload_file(local_file, bucket, s3_file)
        print("Upload Successful")
        os.remove(CSV_NAME)
        return True
    except FileNotFoundError:
        print("The file was not found")
        return False
    except NoCredentialsError:
        print("Credentials not available")
        return False

createFakeCSV()
upload_to_aws(CSV_NAME,TEST_BUCKET,CSV_NAME)



