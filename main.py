import boto3
import pandas as pd
from botocore.exceptions import NoCredentialsError
from pandas.core.frame import DataFrame
from io import StringIO

CSV_HEADER: list[str] = ['DATA','EXPERIENCE']
KEY_FILE: str = 'keys.txt'
EXP_DURATION: int = 30
EXP_NAME: str = 'ball_go_zoom'
EXP_TYPE: str = '2D' #TYPE = 'AR' or '2D' or 'RL'
OFFICIAL_BUCKET: str = 'ed1-eye-tracker'
TEST_BUCKET: str = 'apuentebuckettest'
PROCESS_CSV: str = "Process_Data.csv"

def stripAndCombine(frame:DataFrame, columnName:str,headers:list[str])->DataFrame:
    for header in headers:
        frame[header]=frame[header].str.replace('(','', regex=False)
        frame[header]=frame[header].str.replace(')','', regex=False)
        frame[header]=frame[header].str.replace(' ','', regex=False)
    frame[columnName]=frame[headers].agg("'".join,axis=1)
    frame=frame.drop(headers, axis=1)
    return frame

def readCell(cell:str,confidence:bool)->list[str]:
    """
    Returns list of integers from cell string; if confidence==true, drops last element
    """
    values = cell.split("'")
    if confidence: values.pop()
    values = list(map(int, values))
    return values

def readData()->None:
    """
    Read data from Unity CSV, process, and store
    """
    df = pd.read_csv("Raw_Eye_Data.csv", dtype=str)
    exp_date=df["Date and Time"][0][:10]
    df=df.drop("Date and Time", axis=1)
    df=stripAndCombine(df, "Fixation Point", ["Fixation Point X", "Fixation Point Y", "Fixation Point Z", "Confidence"])
    df=stripAndCombine(df, "Left Forward Gaze", ["Left Foward Gaze X", "Left Foward Gaze Y", "Left Foward Gaze Z"])
    df=stripAndCombine(df, "Right Forward Gaze", ["Right Forward Gaze X", "Right Forward Gaze Y", "Right Forward Gaze Z"])
    df=stripAndCombine(df, "Left Center Gaze", ["Left Center X", "Left Center Y", "Left Center Z", "Left Center Confidence"])
    df=stripAndCombine(df, "Right Center Gaze", ["Right Center X", "Right Center Y", "Right Center Z", "Right Center Confidence"])
    df=stripAndCombine(df, "Left Gaze WXYZ", ["Left Gaze W", "Left Gaze X", "Left Gaze Y", "Left Gaze Z"])
    df=stripAndCombine(df, "Right Gaze WXYZ", ["Right Gaze W", "Right Gaze X", "Right Gaze Y", "Right Gaze Z"])
    df=stripAndCombine(df, "Left + Right Blink", ["Left Blink", "Right Blink"])
    pd.DataFrame(df).to_csv("Test.csv",index=False)
    fullData=[{"Data": df.to_csv(index=False), "Date": exp_date, "Exp Name": EXP_NAME}]
    df=pd.DataFrame(fullData)
    pd.DataFrame(df).to_csv(PROCESS_CSV,index=False,sep=';')
    return


def getFixations(fileName:str)->None: #WIP
    df = pd.read_csv("Test.csv", dtype=str)
    fixDf = pd.DataFrame(columns=["Date","Start Time","End Time","Duration","Fix Avg X","Fix Avg Y"])
    prevX,prevY=None,None
    for index in df.index:
        fixPoints = readCell(df["Fixation Point"][index],True)
        x = fixPoints[0]; y = fixPoints[1]
        if (prevX == None) and (prevY == None): prevX = x; prevY = y; pass
        

    return

def openFullCSV():
    df=pd.read_csv(PROCESS_CSV, dtype=str)
    TESTDATA=StringIO(df.iloc[0,0])
    df=pd.read_csv(TESTDATA)
    pd.DataFrame(df).to_csv("Test.csv",index=False)

def upload_to_aws(local_file, bucket)->bool:
    f=open(KEY_FILE)
    ACCESS_KEY = f.readline().split('=')[1].strip()
    SECRET_KEY = f.readline().split('=')[1].strip()
    s3 = boto3.client('s3', aws_access_key_id=ACCESS_KEY,
                      aws_secret_access_key=SECRET_KEY)
    try:
        s3.upload_file(local_file, bucket, "Processed_Eye_Data.csv")
        print("Upload Successful")
        return True
    except FileNotFoundError:
        print("The file was not found")
        return False
    except NoCredentialsError:
        print("Credentials not available")
        return False

#readData()
#upload_to_aws(PROCESS_CSV,TEST_BUCKET)
#openFullCSV()

