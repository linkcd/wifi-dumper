from __future__ import print_function
import boto3
import awswrangler as wr
import pandas as pd
import urllib

import data_helper as helper

s3 = boto3.client('s3')

def get_bucket_name(event):
    return event['Records'][0]['s3']['bucket']['name']

def get_key(event):
    return urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')

def get_raw_df(event):
    # Get the object body from event
    bucket = get_bucket_name(event)
    key = get_key(event)
    try:
        response = s3.get_object(Bucket=bucket, Key=key)
        body = response['Body'].read()

        sep = ',' #sep for AP CSV
        df_raw = helper.parse_df(body, sep) 
        return df_raw

    except Exception as e:
        print(e)
        print('Error getting object {} from bucket {}. Make sure they exist and your bucket is in the same region as this function.'.format(key, bucket))
        raise e

def handler(event, context):
    ap_df_raw = get_raw_df(event)
    
    clean_df = helper.get_clean_df(ap_df_raw)
    report_df = helper.get_report_df(clean_df)
    short_live_df = helper.get_short_live_ap_df(clean_df, report_df)

    return {
        'statusCode': 200,
        'body':ap_df_raw.shape
    }