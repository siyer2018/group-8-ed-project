import boto3
import json
import urllib.parse
import pandas as pd
from numpy import mean
from botocore.exceptions import NoCredentialsError
from pandas.core.frame import DataFrame
from io import StringIO

KEY_FILE: str = 'keys.txt'
EXP_NAME: str = 'ball_go_zoom' #replace with filename detection
EXP_TYPE: str = '2D' #TYPE = 'AR' or '2D' or 'RL' #replace with filename detection
OFFICIAL_BUCKET: str = 'output-data-processing'
OUTER_CSV: str = "Outer_Data.csv"
CELL_CSV: str = "Data_Cell.csv" #replace with filename detection
FIXATION_CSV: str = "Fixation_Points.csv" #replace with filename detection
FIXATION_OFFSET: float = 0.2
s3 = boto3.client('s3')

def readCell(cell:str)->list[str]:
    """
    Returns list of integers from cell string
    """
    values = cell.split("'")
    values = list(map(float, values))
    return values

def readData(download_path:str, upload_path:str=None)->None:
    """
    Read data from Unity CSV, process, and store
    """
    def stripAndCombine(frame:DataFrame, columnName:str,headers:list[str])->DataFrame:
        for header in headers:
            frame[header]=frame[header].str.replace('(','', regex=False)
            frame[header]=frame[header].str.replace(')','', regex=False)
            frame[header]=frame[header].str.replace(' ','', regex=False)
        frame[columnName]=frame[headers].agg("'".join,axis=1)
        frame=frame.drop(headers, axis=1)
        return frame
    df = pd.read_csv(download_path, dtype=str)
    exp_date=df["Date and Time"][0][:10]
    df=df.drop("Date and Time", axis=1)
    df = df.loc[df["Left Blink"] == False]
    df = df.loc[df["Right Blink"] == False]
    df = df.loc[df["Confidence"] >= 0.75]
    df=stripAndCombine(df, "Fixation Point", ["Fixation Point X", "Fixation Point Y", "Fixation Point Z", "Confidence"])
    df=stripAndCombine(df, "Left + Right Blink", ["Left Blink", "Right Blink"])
    df=df[["Index","Fixation Point","Left + Right Blink"]]
    pd.DataFrame(df).to_csv(CELL_CSV,index=False)
    # fullData=[{"Data": df.to_csv(index=False,header=False), "Date": exp_date, "Exp Name": EXP_NAME}]
    # df=pd.DataFrame(fullData)
    # pd.DataFrame(df).to_csv(OUTER_CSV, index=False, sep=';')
    return

def getFixations(fileName:str, upload_path:str=None)->None:
    df = pd.read_csv(fileName, dtype=str)
    fixDf = pd.DataFrame(columns=["Start Time","End Time","Duration","Fix Avg X","Fix Avg Y"])
    startTime=None
    xList:list[float]=[]
    yList:list[float]=[]
    for row in df.iterrows():
        fixPoints = readCell(row[1]["Fixation Point"])
        x = fixPoints[0]
        y = fixPoints[1]
        xList.append(x)
        yList.append(y)
        if row[1].equals(df.iloc[0]): #initial row
            startTime = row[1]["Index"]
        if (x < mean(xList)-FIXATION_OFFSET) or (x > mean(xList)+FIXATION_OFFSET) or (y <mean(yList)-FIXATION_OFFSET) or (y > mean(yList)+FIXATION_OFFSET):
            # append prev row
            xList.pop()
            yList.pop()
            fixDf = fixDf.append({
                "Start Time":startTime,
                "End Time":row[1]["Index"],
                "Duration":str(int(row[1]["Index"])-int(startTime)),
                "Fix Avg X":mean(xList),
                "Fix Avg Y":mean(yList)},ignore_index=True)
            # create new row
            xList.clear()
            xList.append(x)
            yList.clear()
            yList.append(y)
            startTime = row[1]["Index"]
        if row[1].equals(df.iloc[-1]): #last row
            fixDf = fixDf.append({
                "Start Time":startTime,
                "End Time":row[1]["Index"],
                "Duration":str(int(row[1]["Index"])-int(startTime)+1),
                "Fix Avg X":mean(xList),
                "Fix Avg Y":mean(yList)},ignore_index=True)
            break
    #filter >1 and <-1 x and y values
    fixDf = fixDf.loc[fixDf["Fix Avg X"] >= -1]
    fixDf = fixDf.loc[fixDf["Fix Avg X"] <= 1]
    fixDf = fixDf.loc[fixDf["Fix Avg Y"] >= -1]
    fixDf = fixDf.loc[fixDf["Fix Avg Y"] <= 1]
    pd.DataFrame(fixDf).to_csv(FIXATION_CSV, sep=',')
    return

def outer_to_data_cell():
    """
    Creates a a csv file from the data cell of a broader csv file
    """
    df=pd.read_csv(OUTER_CSV, dtype=str)
    TESTDATA=StringIO(df.iloc[0,0])
    df=pd.read_csv(TESTDATA)
    pd.DataFrame(df).to_csv(CELL_CSV,index=False)

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

readData("1st_Quad.csv")
getFixations(CELL_CSV)