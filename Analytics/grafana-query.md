# Grafana dashboard

## 1. Dashboard for target networks 
### 1.1 Define a dashboard variable _target_essid (feel free to enable multi-values)
```bash
'essid-xxx', 'essid-yyy', 'essid-zzz'
```
### 1.2 Add new panel for **client**, apply the following queries, one for **power** and one for **numpkts**
#### Query #1
```sql
WITH target_ap AS(
  SELECT DISTINCT essid, bssid, channel FROM "wifidumperDB"."accessPointTable"
  WHERE essid in (${_target_essid:raw})
),
target_client AS (
  SELECT ct.*, ta.*
  FROM "wifidumperDB"."clientTable" ct  JOIN target_ap ta on ct.fixed_bssid = ta.bssid
),
binned_query AS (
    SELECT bin(time, $__interval_ms) as bin_time, clientmac, AVG("measure_value::bigint") as power FROM target_client
  WHERE $__timeFilter 
    AND measure_name = 'power'
  GROUP BY clientmac, bin(time,  $__interval_ms)
  ORDER BY bin_time
)
SELECT clientmac, CREATE_TIME_SERIES(bin_time, power)
FROM binned_query
GROUP BY clientmac
```
#### Query #2
```sql
WITH target_ap AS(
  SELECT DISTINCT essid, bssid, channel FROM "wifidumperDB"."accessPointTable"
  WHERE essid in (${_target_essid:raw})
),
target_client AS (
  SELECT ct.*, ta.*
  FROM "wifidumperDB"."clientTable" ct  JOIN target_ap ta on ct.fixed_bssid = ta.bssid
),
binned_query AS (
    SELECT bin(time, $__interval_ms) as bin_time, clientmac, AVG("measure_value::bigint") as numpkts FROM target_client
  WHERE $__timeFilter 
    AND measure_name = 'numpkts'
  GROUP BY clientmac, bin(time,  $__interval_ms)
  ORDER BY bin_time
)
SELECT clientmac, CREATE_TIME_SERIES(bin_time, numpkts)
FROM binned_query
GROUP BY clientmac
```

### 1.3 Add new panel for **AP**
```sql
WITH binned_query AS (
  SELECT bin(time, $__interval_ms) as bin_time, essid, AVG("measure_value::bigint") as mydbpower FROM "wifidumperDB"."accessPointTable" 
  WHERE $__timeFilter
  GROUP BY essid, bin(time,  $__interval_ms)
  ORDER BY bin_time
)
SELECT essid, CREATE_TIME_SERIES(bin_time, mydbpower)
FROM binned_query
WHERE essid in (${_target_essid:raw})
GROUP BY essid
```

## 2. Dashboard for single device
```sql
WITH binned_query AS (
  SELECT bin(time, $__interval_ms) as bin_time, clientmac, AVG("measure_value::bigint") as power FROM "wifidumperDB"."clientTable" 
  WHERE $__timeFilter 
    AND measure_name = 'power'
    AND clientmac = '[YOUR_CLIENT_MAC_ADDRESS]'
  GROUP BY clientmac, bin(time,  $__interval_ms)
  ORDER BY bin_time
)
SELECT clientmac, CREATE_TIME_SERIES(bin_time, power)
FROM binned_query
GROUP BY clientmac
```

## Ref: 
- https://stackoverflow.com/questions/64288404/timestream-grafana-not-recognizing-series-in-data
- https://stackoverflow.com/questions/67713751/aggregating-counts-in-aws-timestream-error-causes-errors
- https://stackoverflow.com/questions/68777076/timestream-grafana
- https://github.com/aws-samples/amazon-timestream-simple-visualizer 