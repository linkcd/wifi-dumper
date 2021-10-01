
Viz AP
```sql
WITH binned_query AS (
  SELECT bin(time, $__interval_ms) as bin_time, essid, AVG("measure_value::bigint") as mydbpower FROM "wifidumperDB"."accessPointTable" 
  WHERE $__timeFilter
  GROUP BY essid, bin(time,  $__interval_ms)
  ORDER BY bin_time
)
SELECT essid, CREATE_TIME_SERIES(bin_time, mydbpower)
FROM binned_query
GROUP BY essid
```

Viz client
```sql
WITH binned_query AS (
  SELECT bin(time, $__interval_ms) as bin_time, clientmac, AVG("measure_value::bigint") as power FROM "wifidumperDB"."clientTable" 
  WHERE $__timeFilter 
    AND measure_name = 'power'
    AND clientmac = 'xxxx'
  GROUP BY clientmac, bin(time,  $__interval_ms)
  ORDER BY bin_time
)
SELECT clientmac, CREATE_TIME_SERIES(bin_time, power)
FROM binned_query
GROUP BY clientmac
```


ref: 
https://stackoverflow.com/questions/64288404/timestream-grafana-not-recognizing-series-in-data
https://stackoverflow.com/questions/67713751/aggregating-counts-in-aws-timestream-error-causes-errors
https://stackoverflow.com/questions/68777076/timestream-grafana
https://github.com/aws-samples/amazon-timestream-simple-visualizer 

