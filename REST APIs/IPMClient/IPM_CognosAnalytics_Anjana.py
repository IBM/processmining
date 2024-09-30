import IPMClient as ipm
import CognosAnalyticsClient as cog
import sys
import json
import pandas as pd


def main(argv):

    ipmConfigFilename = './anjana.json'
    with open(ipmConfigFilename, 'r') as file:
        ipmConfig = json.load(file)

    ipmClient = ipm.Client(ipmConfig['url'], ipmConfig['userid'], ipmConfig['apikey'])
    ipmProject = ipmClient.getProjectByName('Banking Account Closure')

    # RETRIEVE MAIN STATISTICS OF A PROJECT AND SAVE AS SEVERAL CSV

    stats = ipmProject.retrieveModelStatistics()
    processStats = ipmProject.getProcessStatistics(stats)
    processStats_df = pd.json_normalize(processStats)
    processStats_df.keys()
    processStats_df = processStats_df[['minThroughputTime',
        'maxThroughputTime', 'avgThroughputTime', 'stdThroughputTime',
        'medianThroughputTime', 'minArrivalRate', 'maxArrivalRate',
        'avgArrivalRate', 'minTime', 'maxTime', 'filteredCases', 'filteredEvents','totalCases', 'totalEvents']]
    processStats_df.to_csv('processStats.csv', index=None)

    activityStats = ipmProject.getActivityStatistics(stats)
    activityStats_df = pd.json_normalize(activityStats)
    activityStats_df = activityStats_df[['activityName', 'statistics.frequency', 'statistics.avgDuration', 'statistics.medianDuration', 'statistics.minDuration', 'statistics.maxDuration', 'statistics.caseRepetition', 'statistics.avgRepetition', 'statistics.overallCost']]
    activityStats_df.rename({'statistics.frequency': 'frequency', 'statistics.avgDuration':'avgDuration', 'statistics.medianDuration':'medianDuration',
                            'statistics.minDuration':'minDuration', 'statistics.maxDuration':'maxDuration', 'statistics.caseRepetition':'caseRepetition',
                            'statistics.avgRepetition':'avgRepetition', 'statistics.overallCost':'overallCost'}, axis='columns', inplace=True)
    activityStats_df.to_csv('activityStats.csv', index=None)

    transitionStats = ipmProject.getTransitionStatistics(stats)
    transitionStats_df = pd.json_normalize(transitionStats)
    transitionStats_df.keys()
    transitionStats_df=transitionStats_df[['sourceActivity', 'targetActivity', 'statistics.frequency', 'statistics.avgDuration', 'statistics.medianDuration',
                                        'statistics.minDuration','statistics.maxDuration', 'statistics.parallelFrequency','statistics.caseRepetition','statistics.avgRepetition']]
    transitionStats_df.rename({'statistics.frequency':'frequency', 'statistics.avgDuration':'avgDuration', 'statistics.medianDuration':'medianDuration',
                                        'statistics.minDuration':'minDuration','statistics.maxDuration':'maxDuration',
                                        'statistics.parallelFrequency':'parallelFrequency','statistics.caseRepetition':'caseRepetition',
                                        'statistics.avgRepetition':'avgRepetition'}, axis='columns', inplace=True)
    transitionStats_df.to_csv('transitionStats.csv', index=None)

    dashboard = ipmProject.getDashboardByName('Banking account closure-test')
    print (dashboard)
    widget = dashboard.getWidgetByName('activities')
    values = widget.retrieveValues()
    values_df = pd.DataFrame(values)
    values_df.to_csv('acticityStatsFromWidget.csv', index=None)

    # RETRIEVE DATA USING PSEUDO SQL. Avoid being limited by the number of rows in a widget
'''
    query = "SELECT CASEID, leadtime, casecost(), CLOSURE_TYPE, CLOSURE_REASON, COUNTACTIVITIES, COUNTREWORKS FROM EVENTLOG GROUP BY CASEID"
    #res = ipmProject.retrieveFromSQL(query)
    headers = ipmClient.getHeaders()
    headers['content-type'] = 'application/x-www-form-urlencoded'
    data = "params={'query': '%s'}" % query
    res = ipmProject.sendPostRequest(
                url=f"{ipmProject.getURL()}/analytics/integration/{ipmProject.key}/query",
                verify=ipmProject.verify,
                params={'org' : ipmProject.organization.key},
                headers=headers,
                data=data,
                files=None,
                functionName='retrieve from SQL'
            )
    df = pd.DataFrame(res)
    df.columns = ['caseid', 'leadtime', 'cost', 'closure_type', 'closure_reason', 'count_activities', 'count_reworks']
    df.reindex()
    df['cost'] = df['cost'].apply(lambda x: x[0])
    df.to_csv('completedCases.csv', index=None)
    '''

    # Upload the files generated from IBM Process Mining, to IBM Cognos Analytics
    cognosConfigFilename = './CognosAnalytics.json'
    with open(cognosConfigFilename, 'r') as file:
        cognosConfig = json.load(file)


    cognosCredentials =  cog.cognosCreateCredentials(cognosConfig)
    auth = cog.cognosCreateSession(cognosConfig['url'], credentials=cognosCredentials)
    cog.cognosUploadFile(cognosConfig['url'], auth['authkey'], auth['authvalue'], filename='processStats.csv', append=False, silent=False)
    cog.cognosUploadFile(cognosConfig['url'], auth['authkey'], auth['authvalue'], filename='activityStats.csv', append=False, silent=False)
    cog.cognosUploadFile(cognosConfig['url'], auth['authkey'], auth['authvalue'], filename='transitionStats.csv', append=False, silent=False)
    cog.cognosUploadFile(cognosConfig['url'], auth['authkey'], auth['authvalue'], filename='completedCases.csv', append=False, silent=False)
    cog.cognosUploadFile(cognosConfig['url'], auth['authkey'], auth['authvalue'], filename='activityStatsFromWidget.csv', append=False, silent=False)


if __name__ == "__main__":
    main(sys.argv)
