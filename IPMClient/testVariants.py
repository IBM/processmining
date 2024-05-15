import pandas as pd
import json
import IPMClient as ipm
import os

os.chdir('IPMClient')

ipmConfigFilename = './IPMConfig.json'
with open(ipmConfigFilename, 'r') as file:
    ipmConfig = json.load(file)  

ipmClient = ipm.Client(ipmConfig['url'], ipmConfig['userid'], ipmConfig['apikey'])
ipmProject = ipmClient.getProjectByName('Bank Account Closure')
variants = ipmProject.retrieveVariants(300)
df = pd.DataFrame(variants)
df.keys()
df=df[['steps', 'id', 'frequency',
       'subProcessFrequency', 'ratio', 'avgDuration', 'activityNames',
       'minTime', 'maxTime', 'totalCost', 'avgCost']]
df.to_csv('allVariants.csv', index=None)
