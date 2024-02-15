import random
import json
import time
from datetime import datetime as dt, timedelta
import sys
import ProcessMining_API as IPM
import pandas as pd

def load_history_df(history_file):
    try: 
        histo_df = pd.read_csv(history_file, dtype=str)
        print('Loading history file: %s' % history_file)
        return histo_df
    except:
        # First call: Create the historical CSV from scratch at the end
        print('First time execution, no history df')
        return pd.DataFrame()

def main(argv):

    # Example of a configuration object that could be stored as a config file passed as
    # a parameter of the program
    # custom_data are added to the alert fetched from the widget. They can be used to manage
    # some business logic with the alerts received
    if (len(argv)==2):
        try:
            with open(argv[1], 'r') as file:
                myconfig = json.load(file)
                print('Loading config file')
                print(myconfig)
        except:
            print('Error config file not found')
    else:
        myconfig = {
            "url":"https://ProcessMining.com",
            "user_id": "john.smith",
            "api_key":"8a5kga87eqvd1180",
            "project_key": "procure-to-pay",
            "org_key": "",
            "dashboard_name": "Alerts Dashboard",
            "widget_id": "alerts-widget-1",
            "custom_data": {"Status":"False", "Custom2":"default"}
        }

        
    IPM.ws_post_sign(myconfig)

    # Get the current values from the widget
    widgetAlerts = IPM.ws_get_widget_values(myconfig)
    print("%d current alerts for widget %s in dashboard %s" % (len(widgetAlerts), myconfig['widget_id'], myconfig['dashboard_name']))     
    widget_df = pd.DataFrame(widgetAlerts)

    # if the alert_history file does not exist, create it
    history_file = 'alert_history_' + myconfig['dashboard_name'] + '_' + myconfig['widget_id']+'.csv'
    summary_file = 'alert_summary_' + myconfig['dashboard_name'] + '_' + myconfig['widget_id']+'.csv'

    # Load alert history for this widget
    histo_df = load_history_df(history_file)
    if (len(histo_df) == 0):
        # First time execution
        if (len(widget_df) ==  0): # No alerts in the widget
            print('Empty widget, nothing to do')
            return
        else: # create the first history file and summary file and quit
            histo_df = pd.DataFrame(widgetAlerts)
            histo_df['alert_status'] = 'NEW'
            histo_df['alert_creation_date'] = dt.now().isoformat()
            histo_df['alert_closed_date'] = ''
            histo_df.to_csv(history_file, index=None)
            summary = {
                'update_date': dt.now().isoformat(),
                #'last_update_date': 0,
                #'last_new': 0,
                #'last_pending': 0,
                #'last_closed': 0,
                'new': len(histo_df),
                'pending': 0,
                'closed': 0,
                'new_to_pending': 0,
                'new_to_closed': 0,
                'pending_to_closed': 0,
                'pending_to_pending': 0,
                'any_to_closed': 0,
                'progression_rate': 0
            }
            summary_df = pd.DataFrame([summary])
            #summary_df.dtypes(str)
            summary_df.to_csv(summary_file, index=None)
            return

    # Load summary history for this widget
    try: 
        summary_df = pd.read_csv(summary_file)
        print('Loading summary file: %s' % summary_file)
        last_summary = summary_df.loc[len(summary_df) - 1]
    except:
        # First call: Create the summary df 
        summary_df = pd.DataFrame()
        last_summary = {
            'update_date': 0,
            'new': 0,
            'pending': 0,
            'closed': 0,
            'new_to_pending': 0,
            'new_to_closed': 0,
            'pending_to_closed': 0,
            'pending_to_pending': 0,
            'any_to_closed': 0,
            'progression_rate': 0
        }
    summary = {
        'update_date': dt.now().isoformat(),
        'new': 0,
        'pending': 0,
        'closed': last_summary['closed'],
        'new_to_pending': 0,
        'new_to_closed': 0,
        'pending_to_closed': 0,
        'pending_to_pending': 0,
        'any_to_closed': 0,
        'progression_rate': 0
    }

    # Collect the number of alerts in history for each status
    histo_closed_df = histo_df[histo_df['alert_status'] ==  'CLOSED']
    final_df = histo_closed_df # we keep the closed alerts

    # History: CLOSED alerts in histo are still closed
    if (last_summary['closed']):
        print('%d alerts already CLOSED' % last_summary['closed'])

    # If widget is empty, all the alerts are CLOSED
    if (len(widget_df) == 0):
        print("Empty widget, all alerts are closed")
        summary['new'] = 0
        summary['pending'] = 0
        summary['closed'] = len(histo_df)
        summary['new_to_closed'] = last_summary['new']
        summary['pending_to_closed'] = last_summary['pending']
        summary['any_to_closed'] = summary['new_to_closed'] + summary['pending_to_closed']
        summary['pending_to_pending'] = 0

        histo_any_to_close_df = histo_df[histo_df['alert_status'] != 'CLOSED']
        histo_any_to_close_df['alert_closed_date'] = dt.now().isoformat()
        histo_any_to_close_df['alert_status'] =  'CLOSED'
        final_df = pd.concat([final_df, histo_any_to_close_df])
        final_df.to_csv(history_file, index=None)


    else: # Widget is not empty
        
        # We remove CLOSED alerts from histo_df, such that we can add same alerts again if they appear in the widget
        histo_not_closed_df = histo_df[histo_df['alert_status'] != 'CLOSED']

        # NEW alerts in the widget
        widget_new_df = widget_df.merge(histo_not_closed_df, on=widget_df.columns.tolist(), how='left', indicator='alert_is_present_on')
        # Alerts in the widget with 'exist'==left_only are NEW
        widget_new_df = widget_new_df[widget_new_df['alert_is_present_on'] == 'left_only']
        summary['new'] = len(widget_new_df)
        if (summary['new']):
            widget_new_df['alert_status'] = 'NEW'
            widget_new_df['alert_creation_date'] = dt.now().isoformat()
            widget_new_df['alert_closed_date'] = ''
            print('%d new alerts' % summary['new'])
            final_df = pd.concat([final_df, widget_new_df.drop(columns=['alert_is_present_on'])])


        # Process alerts that are in the HISTORY
        histo_not_closed_df = histo_not_closed_df.merge(widget_df, on=widget_df.columns.tolist(), how='left', indicator='alert_is_present_on')
        # NEW to PENDING  
        histo_new_to_pending_df = histo_not_closed_df.query('alert_status=="NEW" & alert_is_present_on=="both"')
        summary['new_to_pending'] = len(histo_new_to_pending_df)
        summary['pending'] =  summary['new_to_pending']                                
        if (summary['new_to_pending']):
            print('%d alerts moved from NEW to PENDING' % summary['new_to_pending'])
            histo_new_to_pending_df['alert_status'] = 'PENDING'
            final_df = pd.concat([final_df, histo_new_to_pending_df.drop(columns=['alert_is_present_on'])])

        # NEW to CLOSE
        histo_new_to_close_df = histo_not_closed_df.query('alert_status=="NEW" & alert_is_present_on=="left_only"')
        summary['new_to_closed'] = len(histo_new_to_close_df)
        summary['closed'] += summary['new_to_closed']                              
        if (summary['new_to_closed']):
            print('%d alerts moved from NEW to CLOSED' % summary['new_to_closed'])
            histo_new_to_close_df['alert_status'] = 'CLOSED'
            histo_new_to_close_df['alert_closed_date'] = dt.now().isoformat()
            final_df = pd.concat([final_df, histo_new_to_close_df.drop(columns=['alert_is_present_on'])]) 

        # PENDING to PENDING
        histo_pending_to_pending_df = histo_not_closed_df.query('alert_status=="PENDING" & alert_is_present_on=="both"')
        summary['pending_to_pending'] = len(histo_pending_to_pending_df)
        summary['pending'] += summary['pending_to_pending']
        if (summary['pending_to_pending']):
            print('%d alerts still PENDING' % summary['pending_to_pending'])
            final_df = pd.concat([final_df, histo_pending_to_pending_df.drop(columns=['alert_is_present_on'])])

        # PENDING to CLOSE
        histo_pending_to_close_df = histo_not_closed_df.query('alert_status=="PENDING" & alert_is_present_on=="left_only"')
        summary['pending_to_closed'] = len(histo_pending_to_close_df)
        summary['closed'] += summary['pending_to_closed']                              

        if (summary['pending_to_closed']):
            print('%d alerts moved from PENDING to CLOSE' % summary['pending_to_closed'])
            final_df = pd.concat([final_df, histo_pending_to_close_df.drop(columns=['alert_is_present_on'])]) 

    # Save final_df in the history file
    final_df.to_csv(history_file, index=None)

    # Add the summary object to the summary dataframe
    if (last_summary['pending'] + last_summary['new']):
        summary['progression_rate'] = summary['any_to_closed'] / (last_summary['pending'] + last_summary['new'])
    else:
        summary['progression_rate'] = 0.0
    print('Progression rate: %d' % summary['progression_rate'])
    summary_df.loc[len(summary_df)] = summary
    summary_df.to_csv(summary_file, index=None)

if __name__ == "__main__":
    main(sys.argv)