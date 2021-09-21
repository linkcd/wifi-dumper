CHECK_TIME_FREQ = "30T" #T mean minute

import pandas as pd
import numpy as np
import boto3
import io

def parse_df(body, sep):
    return pd.read_csv(io.BytesIO(body), 
                        encoding='utf8', 
                        sep=sep,
                        skipinitialspace=True,
                        engine='python',
                        parse_dates = ['First time seen', 'Last time seen'],
                        error_bad_lines=False) 

def get_clean_df(ap_df_raw):
    #rename column
    ap_df_raw.rename(columns={
            'BSSID' : 'bssid',
            'First time seen' : 'firstseen',
            'Last time seen' : 'lastseen',
            'channel' : 'channel',
            'Speed' : 'speed',
            'Privacy' : 'privacy',
            'Cipher' : 'cipher',
            'Authentication' : 'authentication',
            'Power' : 'dbpower',
            '# beacons' : 'beacons',
            '# IV' : 'iv',
            'LAN IP' : 'ip',
            'ID-length' : 'idlen',
            'ESSID' : 'essid',
            'Key' : 'key'
        }, inplace=True)

    def enrich_and_clean_data(raw_df):
        def online_duration(firstseen, lastseen):
            return (lastseen - firstseen)/np.timedelta64(1,'m') 

        def is_clean_data(row):
            if row['bssid']=='00:00:00:00:00:00':
                return False
            if (row['essid'] == "" or pd.isna(row['essid'])) and row['duration'] == 0:
                return False
            return True
        
        # enrichment
        raw_df["duration"] = raw_df.apply(lambda x:online_duration(x['firstseen'], x['lastseen']), axis=1)

        my_clean_df = raw_df.loc[raw_df.apply(lambda x: is_clean_data(x), axis=1)]
        return my_clean_df

    ap_df_clean = enrich_and_clean_data(ap_df_raw)
    print("datfame shape before generating report:", ap_df_clean.shape)

    return ap_df_clean

def get_report_df(ap_df_clean):
    print("the min firstseen in current df: ", ap_df_clean.firstseen.min())

    # Generate check_times of current day, from 00:00 for 24 hours, step definds the frequence.
    report_start_time=ap_df_clean.firstseen.min().date()
    report_end_time = ap_df_clean.firstseen.min().date() + pd.Timedelta(days=1)

    check_times = pd.Series(pd.date_range(start=report_start_time, end=report_end_time,  freq=CHECK_TIME_FREQ))

    #For each checkpoint, extract the client status that covers that check_time. If NOT found, then do nothing
    def generate_report(check_times, original_df):
        #define helper function
        def does_checkpoint_fall_in_between_first_last_seen(firstseen, lastseen, check_time):
            if firstseen <= check_time and check_time <= lastseen:
                return True
            else:
                return False

        results_df_list = []

        #loop all check_time
        for ct in check_times:
            foundRow = original_df.loc[original_df.apply(lambda x: does_checkpoint_fall_in_between_first_last_seen(x['firstseen'], x['lastseen'], ct), axis=1)]
            foundRow.insert(0, "check_time", ct, allow_duplicates = True)
            results_df_list.append(foundRow)

        final_df = pd.concat(results_df_list)
        return final_df

    report_df = generate_report(check_times, ap_df_clean)
    print("report dataframe shape:", report_df.shape)

    return report_df

def get_short_live_ap_df(ap_df_clean, report_df):
    short_live_ap_df = ap_df_clean.loc[~ap_df_clean.bssid.isin(report_df.bssid)]
    print("short live record that did not make into report:", short_live_ap_df.shape)
    return short_live_ap_df

### How to use in Jupyter notebook ###
# def read_prefix_to_df(prefix, sep):
#     s3 = boto3.resource('s3')
#     bucket = s3.Bucket('wifidumper')
    
#     prefix_objs = bucket.objects.filter(Prefix=prefix)
#     prefix_df = []
#     for obj in prefix_objs:
#         key = obj.key
#         body = obj.get()['Body'].read()
#         temp = parse_df(body, sep)      
#         prefix_df.append(temp)
#     return pd.concat(prefix_df)

# ap_df_raw=read_prefix_to_df("raw/ap/2021-09-21T09-34-14_ap.csv", ',')

# clean_df = get_clean_df(ap_df_raw)
# report_df = get_report_df(clean_df)
# short_live_df = get_short_live_ap_df(clean_df, report_df)
### End ###