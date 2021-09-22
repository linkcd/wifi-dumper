from __future__ import print_function
import boto3
import awswrangler as wr
import pandas as pd
import urllib
import os
import json
from common_helper import *


CHECK_TIME_FREQ = os.getenv('CHECK_TIME_FREQ', '15T') #default 15min, 50% of data source freq, to avoid missing point in report
RESULT_DATA_S3_BUCKET = os.getenv('RESULT_DATA_S3_BUCKET', 'wifidumperresult') 
MAIN_REPORT_OUTPUT_KEY = os.getenv('MAIN_REPORT_OUTPUT_KEY', 'timeline-reports/ap.parquet')
SHORT_LIVE_REPORT_OUTPUT_KEY = os.getenv('SHORT_LIVE_REPORT_OUTPUT_KEY', 'timeline-reports/ap_shortlive.parquet')

s3 = boto3.client('s3')

def get_af_clean_df(ap_df_raw):
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
        enrich_duration(raw_df)
        
        def is_clean_data(row):
            if row['bssid']=='00:00:00:00:00:00':
                return False
            if (row['essid'] == "" or pd.isna(row['essid'])) and row['duration'] == 0:
                return False
            return True

        my_clean_df = raw_df.loc[raw_df.apply(lambda x: is_clean_data(x), axis=1)]
        return my_clean_df

    ap_df_clean = enrich_and_clean_data(ap_df_raw)
    print("Clean dataframe shape, before generating report:", ap_df_clean.shape)

    return ap_df_clean


def get_raw_df(bucket, key):
    # Get the object body from event
    try:
        print("loading from bucket:", bucket, "key:", key)
        response = s3.get_object(Bucket=bucket, Key=key)
        body = response['Body'].read()

        sep = ',' #sep for AP CSV
        df_raw = parse_df(body, sep) 
        return df_raw

    except Exception as e:
        print(e)
        print('Error getting object {} from bucket {}. Make sure they exist and your bucket is in the same region as this function.'.format(key, bucket))
        raise e

def handler(event, context):
    main_report_key = f"s3://{RESULT_DATA_S3_BUCKET}/{MAIN_REPORT_OUTPUT_KEY}"
    shortlive_report_key = f"s3://{RESULT_DATA_S3_BUCKET}/{SHORT_LIVE_REPORT_OUTPUT_KEY}"
    
    result_msg_list = []

    #Loops through every file uploaded
    for record in event['Records']:
        
        msgId = record['messageId']
        #pull the body out & json load it
        body_json=json.loads(record["body"]) 
        
        #now the normal stuff works
        bucket = body_json['Records'][0]['s3']['bucket']['name']
        key = urllib.parse.unquote_plus(body_json['Records'][0]['s3']['object']['key'], encoding='utf-8')

        ap_df_raw = get_raw_df(bucket, key)
        clean_df = get_af_clean_df(ap_df_raw)

        report_df = get_report_df(clean_df, CHECK_TIME_FREQ)
        shortlive_report_df = get_short_live_df(clean_df, report_df, 'bssid')

        update_report_to_s3(report_df, main_report_key)
        update_report_to_s3(shortlive_report_df, shortlive_report_key)

        resultMsg = f"Processed msg Id: {msgId} --> Main report added:{report_df.shape[0]}, Shortlive report added:{shortlive_report_df.shape[0]}"
        print(resultMsg)

        result_msg_list.append(resultMsg)

    print("done!")

    return {
        'statusCode': 200,
        'body':result_msg_list
    }