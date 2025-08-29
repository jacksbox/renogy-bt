# Concept

## Local Energy Status Monitor

### Version 0.1

* read battery data periodically
    * store in sqlite database
* local website
    * show current
        * state of charge abs/percentage
        * charge / discharge

### Version 0.2

* serve a local api
    * retrieve data as timeseries
        * filter by field
        * set sampling
        * _optional_ filter by time range

### Version 0.3

* local website
    * visualize
        * daily development (all measuremnts)
        * monthly development (by hour)
        * yearly development (by hour)

### Version 0.4

* database
    * accumulate periodically to safe storage (e.g. after 1 month -> by hour)