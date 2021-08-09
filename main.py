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
PROCESS_CSV: str = "In_Process_Data.csv"

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

#Multiline commented: NOT BEING USED
'''
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
'''

def readData()->None:
    """
    Read data from Unity CSV, process, and store
    """
    df = pd.read_csv(CSV_PATH)
    df=df[['Index','Fixation Point X','Fixation Point Y']]
    df['EXP_TYPE']='2D'
    df1=pd.DataFrame(df).copy()
    df1['EXP_TYPE']='AR'
    df=pd.concat([df,df1])
    print(df)
    pd.DataFrame(df).to_csv(PROCESS_CSV,index=False)
    return

'''In progress'''
# def readData()->None:
#     """
#     Read data from Unity CSV, process, and store
#     """
#     df = pd.read_csv(CSV_PATH, header=None)
#     df=df.drop(0)
#     data = {'DATA':[df,df],
#             'EXP_TYPE':['2D','AR']}
#     df=pd.DataFrame(data)
#     pd.DataFrame(df).to_csv(PROCESS_CSV,index=False)
#     return

def upload_to_aws(local_file, bucket)->bool:
    f=open(KEY_FILE)
    ACCESS_KEY = f.readline().split('=')[1].strip()
    SECRET_KEY = f.readline().split('=')[1].strip()
    s3 = boto3.client('s3', aws_access_key_id=ACCESS_KEY,
                      aws_secret_access_key=SECRET_KEY)
    try:
        s3.upload_file(local_file, bucket, "Processed_Eye_Data.csv")
        print("Upload Successful")
        #os.remove(CSV_NAME)
        return True
    except FileNotFoundError:
        print("The file was not found")
        return False
    except NoCredentialsError:
        print("Credentials not available")
        return False

readData()
upload_to_aws(PROCESS_CSV,TEST_BUCKET)



