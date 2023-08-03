import pandas as pd

def execute(context):
    justatest = [
    {'processid':'p1', 'activity':'analyze request', 'date':'2023-01-01'},
    {'processid':'p1', 'activity':'approve request', 'date':'2023-01-02'},
    {'processid':'p2', 'activity':'approve request', 'date':'2023-01-02'},
    {'processid':'p2', 'activity':'reject request', 'date':'2023-01-04'},
    ]
    df = pd.DataFrame(justatest)
    return(df)

if __name__ == "__main__":

    df = execute({})
    df.to_csv('justatest.csv')