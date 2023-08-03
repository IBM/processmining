import pandas as pd

def execute(context):
    events = [
    {'pid':'p1', 'activity':'A1', 'date':'2023-01-01'},
    {'pid':'p1', 'activity':'A2 request', 'date':'2023-01-02'},
    {'pid':'p2', 'activity':'A1', 'date':'2023-01-02'},
    {'pid':'p2', 'activity':'A3', 'date':'2023-01-04'},
    ]
    df = pd.DataFrame(events)
    return df