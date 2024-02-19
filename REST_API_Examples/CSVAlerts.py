import random
import json
import time
from datetime import datetime as dt, timedelta
import sys
import ProcessMining_API as IPM
import pandas as pd

def join_and_cleanup(df1, df2, cols, suffix, suffix_for):
    # suffix_for = 'left' or 'right'
    if (suffix_for == 'left'): suffixes = (suffix, '')
    else: suffixes = ('', suffix)
    df = df1.merge(df2, how='left', on=cols, indicator='alert_is_present_on', suffixes=suffixes)
    # remove columns (duplicated) from log
    kept_cols = []
    for col in df.columns:
        if (suffix not in col):
            kept_cols.append(col)
    return df[kept_cols]

class processMiningConnector():
    def __init__(self, config):
        self.config = config


class widgetAlerts():
    def __init__(self, connector, dashboardName, widgetId, matchingColumnIndexes): # config is a json with the widget properties
        self.connector = connector
        self.dashboardName = dashboardName
        self.widgetId = widgetId
        self.matchingColumnIndexes = matchingColumnIndexes # replaced when the widget columns are known
        if (self.matchingColumnIndexes == 0 or self.matchingColumnIndexes == ''):
            self.matchingColumnIndexes = [0]
        self.logFileName = 'alert_log_' + self.dashboardName + '_' + self.widgetId +'.csv'
        self.summaryFileName = 'alert_summary_' + self.dashboardName + '_' + self.widgetId +'.csv'
        connector.config['dashboard_name'] = dashboardName
        connector.config['widget_id'] = widgetId


    def loadLog(self):
        # Load alert log for this widget
        try: 
            self.log_df = pd.read_csv(self.logFileName, dtype=str)
        except:
            # First call
            self.log_df = pd.DataFrame()

    def loadSummary(self):
        # Load summary file for this widget
        try: 
            self.summary_df = pd.read_csv(self.summaryFileName)
        except:
            # First call: Create the summary df 
            self.summary_df = pd.DataFrame()

    def loadWidgetData(self):
        IPM.ws_post_sign(self.connector.config)
        res = IPM.ws_get_widget_values(self.connector.config)
        if (res['status_code'] == 200):
            self.widget_df = pd.DataFrame(res['data'])
            self.setMatchingColumns() # matching columns: indexes replaced with column names

        else: 
            print('ERROR: Dashboard or Widget not found')
            self.widget_df = pd.DataFrame()

    def setMatchingColumns(self):
        # Get the widget columns used to match the alerts
        # Do the merge with the columns mentionned in the configuration as an array
        self.matchingColumns = []
        for i in range(len(self.widget_df.columns)):
            if (i in self.matchingColumnIndexes):
                self.matchingColumns.append(self.widget_df.columns[i])
        print("Matching columns used for existing alerts: %s" % self.matchingColumns)
    
    def updateAlertsFirstTime(self):
        if len(self.widget_df) == 0:
            print('Empty widget and no log yet. No data to generate')
            self.new_log_df = pd.DataFrame()
            self.summary_df = pd.DataFrame()
        else: #first time execution
            self.new_log_df = self.widget_df.copy()
            self.new_log_df['alert_status'] = 'NEW'
            self.new_log_df['alert_creation_date'] = dt.now().isoformat()
            self.new_log_df['alert_closed_date'] = ''
            self.summary_df = pd.DataFrame([{
                'update_date': dt.now().isoformat(),
                'new': len(self.widget_df),
                'pending': 0,
                'closed': 0,
                'new_to_pending': 0,
                'new_to_closed': 0,
                'pending_to_closed': 0,
                'pending_to_pending': 0,
                'any_to_closed': 0,
                'progression_rate': 0
            }])

    def updateAlerts(self):
        self.loadLog()
        self.loadSummary()
        self.loadWidgetData()

        if len(self.log_df) == 0: # No log yet
            self.updateAlertsFirstTime()
        else:
            self.new_log_df = self.log_df[self.log_df.alert_status == 'CLOSED'] # we don't touch CLOSED alerts
            # Add a new summary row
            self.summary_df.loc[len(self.summary_df)] = { 
                'update_date': dt.now().isoformat(),
                'new': 0,
                'pending': 0,
                'closed': self.summary_df.loc[len(self.summary_df)-1, 'closed'],
                'new_to_pending': 0,
                'new_to_closed': 0,
                'pending_to_closed': 0,
                'pending_to_pending': 0,
                'any_to_closed': 0,
                'progression_rate': 0
            }
            if len(self.widget_df) == 0: # no more alerts, close all NEW and PENDING from log
                self.closeAllAlerts()
            else:
                self.manageNewAlerts()
                self.manageExistingAlerts()
        
        self.log_df = self.new_log_df

    def closeAllAlerts(self):
        new_to_close_df = self.log_df[self.log_df.alert_status == 'NEW']
        new_to_close_df.alert_status = 'CLOSED'
        new_to_close_df.alert_closed_date = dt.now().isoformat()
        pending_to_close_df = self.log_df[self.log_df.alert_status == 'PENDING']
        pending_to_close_df.alert_status = 'CLOSED'
        pending_to_close_df.alert_closed_date = dt.now().isoformat()
        self.new_log_df = pd.concat([self.new_log_df, new_to_close_df, pending_to_close_df])
        self.summary_df.loc[len(self.summary_df) - 1, 'closed'] = len(self.log_df)
        self.summary_df.loc[len(self.summary_df) - 1, 'new_to_closed'] = len(new_to_close_df)
        self.summary_df.loc[len(self.summary_df) - 1, 'pending_to_closed'] = len(pending_to_close_df)

    def manageNewAlerts(self):
        not_closed_df = self.log_df[self.log_df.alert_status != 'CLOSED']
        widget_new_df = join_and_cleanup(self.widget_df, not_closed_df, self.matchingColumns, "_suffixFromlog", 'right')
        # Alerts in the widget with 'exist'==left_only are NEW
        widget_new_df = widget_new_df[widget_new_df.alert_is_present_on == 'left_only']
        widget_new_df.alert_status = 'NEW'
        widget_new_df.alert_creation_date = dt.now().isoformat()
        widget_new_df.alert_closed_date = ''
        self.new_log_df = pd.concat([self.new_log_df, widget_new_df.drop(columns=['alert_is_present_on'])])
        self.summary_df.loc[len(self.summary_df) - 1, 'new'] = len(widget_new_df)

    def manageExistingAlerts(self):
        not_closed_df = self.log_df[self.log_df.alert_status != 'CLOSED']
        not_closed_df = join_and_cleanup(not_closed_df, self.widget_df, self.matchingColumns, "_suffixFromlog", 'left')

        # NEW to PENDING  
        new_to_pending_df = not_closed_df.query('alert_status=="NEW" & alert_is_present_on=="both"')
        self.summary_df.loc[len(self.summary_df) - 1, 'new_to_pending'] = len(new_to_pending_df)
        self.summary_df.loc[len(self.summary_df) - 1, 'pending'] = len(new_to_pending_df)
        if (len(new_to_pending_df)):
            new_to_pending_df.alert_status = 'PENDING'
            self.new_log_df = pd.concat([self.new_log_df, new_to_pending_df.drop(columns=['alert_is_present_on'])])

        # NEW to CLOSED
        new_to_close_df = not_closed_df.query('alert_status=="NEW" & alert_is_present_on=="left_only"')
        self.summary_df.loc[len(self.summary_df) - 1, 'new_to_closed'] = len(new_to_close_df)
        self.summary_df.loc[len(self.summary_df) - 1, 'closed'] += len(new_to_close_df)
        if (len(new_to_close_df)):
            new_to_close_df.alert_status = 'CLOSED'
            new_to_close_df.alert_closed_date = dt.now().isoformat()
            self.new_log_df = pd.concat([self.new_log_df, new_to_close_df.drop(columns=['alert_is_present_on'])])

        # PENDING to PENDING
        pending_to_pending_df = not_closed_df.query('alert_status=="PENDING" & alert_is_present_on=="both"')
        self.summary_df.loc[len(self.summary_df) - 1, 'pending_to_pending'] = len(pending_to_pending_df)
        self.summary_df.loc[len(self.summary_df) - 1, 'pending'] += len(pending_to_pending_df)
        if (len(pending_to_pending_df)):
            pending_to_pending_df.alert_status = 'PENDING'
            self.new_log_df = pd.concat([self.new_log_df, pending_to_pending_df.drop(columns=['alert_is_present_on'])])    

        # PENDING to CLOSED
        pending_to_closed_df = not_closed_df.query('alert_status=="NEW" & alert_is_present_on=="left_only"')
        self.summary_df.loc[len(self.summary_df) - 1, 'pending_to_closed'] = len(pending_to_closed_df)
        self.summary_df.loc[len(self.summary_df) - 1, 'closed'] += len(pending_to_closed_df)
        if (len(pending_to_closed_df)):
            pending_to_closed_df.alert_status = 'CLOSED'
            pending_to_closed_df.alert_closed_date = dt.now().isoformat()
            self.new_log_df = pd.concat([self.new_log_df, pending_to_closed_df.drop(columns=['alert_is_present_on'])])

        self.computeProgressionRate()         

    def saveLogFile(self):
        if (len(self.log_df)):
            self.log_df.to_csv(self.logFileName, index=None)
    
    def saveSummaryFile(self):
        if (len(self.summary_df)):
            self.summary_df.to_csv(self.summaryFileName, index=None)

    def computeProgressionRate(self):
        l = len(self.summary_df)
        if (len(self.summary_df) < 2): # no previous summary
            self.summary_df.loc[l - 1, 'progression_rate'] = 0
        else:
            if (self.summary_df.loc[l - 2, 'pending'] + self.summary_df.loc[l - 2, 'new']):
                # there were pending and/or new alerts last time
                self.summary_df.loc[l - 1, 'progression_rate'] = (self.summary_df.loc[l - 1, 'new_to_closed'] + self.summary_df.loc[l - 1, 'pending_to_closed']) / (self.summary_df.loc[l - 2, 'pending'] + self.summary_df.loc[l - 2, 'new'])
            else: 
                self.summary_df.loc[l - 1, 'progression_rate'] = 0
            
    def updateAlertsAndSave(self):
        self.updateAlerts()
        self.saveLogFile()
        self.saveSummaryFile()

    def setLogFilename(self, filename):
        self.logFileName = filename

    def setSummaryFilename(self, filename):
        self.summaryFileName = filename

    def getLogs(self):
        return self.log_df
    
    def getSummary(self):
        return self.summary_df
    
    def setMatchingColumnIndexes(self, cols):
        self.matchingColumnIndexes = cols

def main(argv):
    if (len(argv)==2):
        try:
            with open(argv[1], 'r') as file:
                connectorConfig = json.load(file)
                print('Loading connector configuration file')
                print(connectorConfig)
        except:
            print('Error connector configuration file not found') 
    else:
        connectorConfig = {
            "url":"https://ProcessMining.com",
            "user_id": "john.smith",
            "api_key":"8a5kga87eqvd1180",
            "project_key": "procure-to-pay",
            "org_key": "",
        }
    # Constructors
    connector = processMiningConnector(connectorConfig)
    alerts1 = widgetAlerts(connector, 'alerts', 'invoices-withholding-tax', [0,1,2,3])
    # Optionnaly, the default filenames can be changed like this:
    alerts1.setLogFilename('mylog.csv')
    alerts1.setSummaryFilename('mysummary.csv')
    # The matching columns can be changed. Use columns with values that do not change at each update for the same alert (ex: no duration until now)
    alerts1.setMatchingColumnIndexes([0,1,2])
    alerts1.updateAlertsAndSave() # Load files, get widget values, match with log, update log and summary, save files
    print(alerts1.getLogs().head())
    print(alerts1.getSummary().head())

    alerts2 = widgetAlerts(connector, 'alerts', 'invoices-blocked-account', [0,1,2,3])
    alerts2.updateAlertsAndSave()
    print(alerts2.getLogs().head())
    print(alerts2.getSummary().head())


if __name__ == "__main__":
    main(sys.argv)