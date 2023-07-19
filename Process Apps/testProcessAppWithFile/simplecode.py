import pandas as pd
from zipfile import ZipFile

def execute(context):

    myFileUploadName = context["fileUploadName"]
    with ZipFile(myFileUploadName, 'r') as f:
        f.extractall()
    df = pd.read_csv('./justatest.csv')
    return(df)

if __name__ == "__main__":

    df = execute({})
    df.to_csv('justatest.csv')