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
MAIN_REPORT_OUTPUT_KEY = os.getenv('MAIN_REPORT_OUTPUT_KEY', 'timeline-reports/client.parquet')
SHORT_LIVE_REPORT_OUTPUT_KEY = os.getenv('SHORT_LIVE_REPORT_OUTPUT_KEY', 'timeline-reports/client_shortlive.parquet')

s3 = boto3.client('s3')

# Client function
# Fix parse error
def getBSSID(raw_bssid):
    return raw_bssid.split(",", 1)[0]

def getProbedSSID(raw_bssid):
    return raw_bssid.split(",", 1)[1]

def get_client_clean_df(raw_df):
    #rename column
    raw_df.columns = ['clientmac', 'firstseen', 'lastseen', 'power', 'numpkts', 'raw_bssid', 'raw_probedssids']
    
    raw_df["fixed_bssid"] = raw_df["raw_bssid"].apply(lambda x: getBSSID(x))
    raw_df["fixed_probedSSID"] = raw_df["raw_bssid"].apply(lambda x: getProbedSSID(x))

    def enrich_and_clean_data(raw_df):
        enrich_duration(raw_df)
        
        def is_clean_data(row):
            return True

        my_clean_df = raw_df.loc[raw_df.apply(lambda x: is_clean_data(x), axis=1)]
        return my_clean_df

    clean_df = enrich_and_clean_data(raw_df)
    print("Clean dataframe shape, before generating report:", clean_df.shape)

    return clean_df


def get_raw_df(bucket, key):
    # Get the object body from event
    try:
        print("loading from bucket:", bucket, "key:", key)
        response = s3.get_object(Bucket=bucket, Key=key)
        body = response['Body'].read()

        sep = ', ' #sep for CLIENT CSV
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

        client_df_raw = get_raw_df(bucket, key)

        clean_df = get_client_clean_df(raw_df)
        report_df = get_report_df(clean_df, CHECK_TIME_FREQ)
        shortlive_report_df = get_short_live_df(clean_df, report_df, 'clientmac')

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