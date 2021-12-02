import boto3
import awswrangler as wr
import pandas as pd
from numpy import mean, string_
from pandas.core.frame import DataFrame
from io import StringIO

KEY_FILE: str = 'keys.txt'
EXP_TYPE: str = '2D' #TYPE = 'AR' or '2D' or 'RL' #replace with filename detection
OUTER_CSV: str = "Outer_Data.csv"
FIXATION_OFFSET: float = 0.1 #+- fixation point averaging boundary
FIXATION_BOUNDARY: float = 0.4 #+- boundary for fixation points

def readData(df:DataFrame, file_part: dict[str])->None:
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
    # exp_date: str = df["Date and Time"][0][:10]
    
    df = df.drop("Date and Time", axis=1)
    df = df.loc[df["Left Blink"].isin(["False"])]
    df = df.loc[df["Right Blink"].isin(["False"])]
    df = df.loc[df["Confidence"].astype("float64") >= 0.75]

    df=stripAndCombine(df, "Fixation Point", ["Fixation Point X", "Fixation Point Y", "Fixation Point Z", "Confidence"])
    df=stripAndCombine(df, "Blink", ["Left Blink", "Right Blink"])
    # new columnk IsFocused : bool
    df=df[["Index","Fixation Point","Blink"]]
    fixDf: DataFrame = getFixations(df)
    pd.DataFrame(df).to_csv(file_part["Processed"],index=False,sep=',')
    pd.DataFrame(fixDf).to_csv(file_part["Fixations"], sep=',')
    # fullData=[{"Data": df.to_csv(index=False,header=False), "Date": exp_date, "Exp Name": EXP_NAME}]
    # df=pd.DataFrame(fullData)
    # pd.DataFrame(df).to_csv(OUTER_CSV, index=False, sep=';')
    return

def getFixations(frame:DataFrame)->DataFrame:
    def readCell(cell:str)->list[str]:
        """
        Returns list of integers from cell string
        """
        values = cell.split("'")
        values = list(map(float, values))
        return values
    fixDf = pd.DataFrame(columns=["Start Time","End Time","Duration","Fix Avg X","Fix Avg Y"])
    startTime: int = None
    fixated: int
    xList:list[float]=[]
    yList:list[float]=[]
    for row in frame.iterrows():
        fixPoints = readCell(row[1]["Fixation Point"])
        x = fixPoints[0]
        y = fixPoints[1]
        xList.append(x)
        yList.append(y)
        if row[1].equals(frame.iloc[0]): #initial row
            startTime = row[1]["Index"]
        if (x < (mean(xList)-FIXATION_OFFSET)) or (x > (mean(xList)+FIXATION_OFFSET)) or (y < (mean(yList)-FIXATION_OFFSET)) or (y > (mean(yList)+FIXATION_OFFSET)):
            # append prev row
            xList.pop()
            yList.pop()

            if ((mean(xList) >= 0) and (mean(yList) >= 0)):
                fixated = 1
            elif ((mean(xList) >= 0) and (mean(yList) <= 0)):
                fixated = 2
            elif ((mean(xList) <= 0) and (mean(yList) <= 0)):
                fixated = 3
            else:
                fixated = 4
            
            fixDf = fixDf.append({
                "Start Time":startTime,
                "End Time":row[1]["Index"],
                "Duration":str(int(row[1]["Index"])-int(startTime)),
                "Fix Avg X":mean(xList),
                "Fix Avg Y":mean(yList),
                "Fixated On Target":fixated},ignore_index=True)
            # create new row
            xList.clear()
            xList.append(x)
            yList.clear()
            yList.append(y)
            startTime = row[1]["Index"]
        if row[1].equals(frame.iloc[-1]): #last row
            fixDf = fixDf.append({
                "Start Time":startTime,
                "End Time":row[1]["Index"],
                "Duration":str(int(row[1]["Index"])-int(startTime)+1),
                "Fix Avg X":mean(xList),
                "Fix Avg Y":mean(yList),
                "Fixated On Target":fixated},ignore_index=True)
            break
    #filter >1 and <-1 x and y values
    fixDf = fixDf.loc[fixDf["Fix Avg X"] >= (-1*FIXATION_BOUNDARY)]
    fixDf = fixDf.loc[fixDf["Fix Avg X"] <= (1*FIXATION_BOUNDARY)]
    fixDf = fixDf.loc[fixDf["Fix Avg Y"] >= (-1*FIXATION_BOUNDARY)]
    fixDf = fixDf.loc[fixDf["Fix Avg Y"] <= (1*FIXATION_BOUNDARY)]
    return fixDf

def outer_to_data_cell():
    """
    Creates a a csv file from the data cell of a broader csv file
    """
    df=pd.read_csv(OUTER_CSV, dtype=str)
    TESTDATA=StringIO(df.iloc[0,0])
    df=pd.read_csv(TESTDATA)
    # pd.DataFrame(df).to_csv(CELL_CSV,index=False)

def environment(file_part:dict[str])->None:
    session = boto3.Session(
        aws_access_key_id="xxxxxxxxxxxx",
        aws_secret_access_key="xxxxxxxxxxx")
    data_path: str = file_part["path"] + file_part["input"] + file_part["Raw"]
    df: DataFrame = wr.s3.read_csv(
        path= data_path,
        boto3_session= session,
        dtype = str)
    readData(df,file_part)
    return

###############################
###############################
###############################
###############################

def key_split(key:str)->dict[str]:
    """
    Returns a dict containing experience type and experience name
    """
    split_key: list[str] = key.split("_")
    exp_part = {
        "type": split_key[0],
        "name": split_key[-1]}
    return exp_part

key = "AR_Raw_AllQuadrantPerformanceTest.csv"
bucket = "input-data-processing"
OUTPUT_BUCKET = "output-data-processing"
exp_part: dict[str] = key_split(key)
file_part = {
    "Raw": key,
    "Processed": exp_part["type"] + "_Processed_" + exp_part["name"],
    "Fixations": exp_part["type"] + "_Fixations_" + exp_part["name"],
    "path": "s3://",
    "folder": "tmp/",
    "bucket": bucket + "/",
    "output": OUTPUT_BUCKET + "/"}
session = boto3.Session(
    aws_access_key_id="AKIA443JJFV53DG4YJPH",
    aws_secret_access_key="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")
data_path: str = file_part["path"] + file_part["bucket"] + file_part["Raw"]
df: DataFrame = wr.s3.read_csv(
    path= data_path,
    boto3_session= session,
    dtype = str)

readData(df,file_part)
