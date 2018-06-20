# Ambari Service Check python util

You can use this python util to initiate Ambari service checks for selected or all services.

## Config
You can find below a sample config. Please set the permission that only the user who shell run this script can read it.

Sample config:

`
{
  "hostname": "localhost",
  "port": 8080,
  "cluster_name": "sandbox",
  "user": "admin",
  "password": "admin",
  "ssl": false
}
`

## Usage
You can specify two option:
1. config file location with `-c`
2. list of services you want to check with `-s`, please use only comma to separate the service_names

If you do not use `-s` option, that means the script will check all services
If you do not use `-c` option, that means the script will search the config file at `../conf/config`

Some samples:

`ambari_check_service.py -c ../conf/config -s HDFS`
`ambari_check_service.py -c ../conf/config -s HDFS,YARN`
`ambari_check_service.py -c ../conf/config`
