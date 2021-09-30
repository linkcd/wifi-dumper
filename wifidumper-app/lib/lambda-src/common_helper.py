import pandas as pd
import numpy as np
import boto3
import os
import io
import awswrangler as wr
from datetime import date

#Not used in lambda but in jupyter notebook
def read_prefix_to_df(prefix, sep):
    s3 = boto3.resource('s3')
    bucket = s3.Bucket('wifidumper')
    
    prefix_objs = bucket.objects.filter(Prefix=prefix)
    prefix_df = []
    for obj in prefix_objs:
        key = obj.key
        body = obj.get()['Body'].read()
        temp = parse_df(body, sep)      
        prefix_df.append(temp)
    return pd.concat(prefix_df)

def parse_df(body, sep):
    return pd.read_csv(io.BytesIO(body), 
                        encoding='utf8', 
                        sep=sep,
                        skipinitialspace=True,
                        engine='python',
                        parse_dates = ['First time seen', 'Last time seen'],
                        error_bad_lines=False) 

def enrich_duration(df):
    df["duration"] = df.apply(lambda x:(x.lastseen - x.firstseen)/np.timedelta64(1,'m'), axis=1)

def get_check_time_series(min_firstseen, max_lastseen, freq):
    round_freq = freq
    
    print("Check freq:", freq)
    
    start_time = min_firstseen.floor(freq=round_freq)
    print("min first seen:", min_firstseen, "->", "check_start_time_for_report:", start_time)
    
    end_time = max_lastseen.ceil(freq=round_freq)
    print("max last seen:", max_lastseen, "->", "check_end_time_for_report:", end_time)

    check_times = pd.Series(pd.date_range(start=start_time, end=end_time,  freq=freq))
    print(check_times)
    
    return check_times

def get_report_df(df_clean, check_time_freq):
    
    #Get check_times
    min_firstseen = df_clean.firstseen.min()
    max_lastseen = df_clean.lastseen.max()

    check_times = get_check_time_series(min_firstseen, max_lastseen, check_time_freq)
    
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
    ###End of function generate_report ###

    report_df = generate_report(check_times, df_clean)
    
    ##Enrich check time date for storage partition
    report_df['check_time_date'] = report_df['check_time'].dt.date
    
    print("Report dataframe shape:", report_df.shape)

    return report_df

def get_short_live_df(clean_df, report_df, key_column):
    short_live_df = clean_df.loc[~clean_df[key_column].isin(report_df[key_column])]
    print("Short live record that did NOT make into report:", short_live_df.shape)
    return short_live_df

def update_report_to_s3(report_df, key):
    if len(report_df) < 1:
        print("Empty data frame, skip saving...")
        return

    wr.s3.to_parquet(
        df=report_df,
        path=key,
        dataset=True,
        mode="append"#,
        #partition_cols=partition_cols
    )
    print("Saved report to:", key)

def save_df_to_timestream(df, measure_names_list, common_dimensions_cols_list, ts_db_name, ts_table_name):
    total_rejected_records = []
    
    for mn in measure_names_list:
        
        needed_col =common_dimensions_cols
        needed_col.append(mn)
        needed_df = df.copy()[needed_col].drop_duplicates()
        print("Saving to timestream db with measure name:", mn, "--- Dataframe count:", len(needed_df))
        
        rejected_records = wr.timestream.write(
                                df=needed_df,
                                database=ts_db_name,
                                table=ts_table_name,
                                time_col="check_time",
                                measure_col=mn,
                                dimensions_cols=common_dimensions_cols,
                            )
        print("Ingested data for:", mn, "... Timestream rejected record count:", len(rejected_records))
        total_rejected_records = total_rejected_records + rejected_records
        
    print("Saved. Total rejected records:", len(total_rejected_records))
    return total_rejected_records