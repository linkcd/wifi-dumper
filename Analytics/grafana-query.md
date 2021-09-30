
```sql
WITH binned_query AS (
  SELECT bin(time, $__interval_ms) as bin_time, bssid, AVG("measure_value::bigint") as mydbpower FROM "sampleDB"."ap_table" 
  WHERE $__timeFilter
  GROUP BY bssid, bin(time,  $__interval_ms)
  ORDER BY bin_time
)
SELECT bssid, CREATE_TIME_SERIES(bin_time, mydbpower)
FROM binned_query
GROUP BY bssid
```

ref: 
https://stackoverflow.com/questions/64288404/timestream-grafana-not-recognizing-series-in-data
https://stackoverflow.com/questions/67713751/aggregating-counts-in-aws-timestream-error-causes-errors
https://stackoverflow.com/questions/68777076/timestream-grafana
https://github.com/aws-samples/amazon-timestream-simple-visualizer 

