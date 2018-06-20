#!/usr/bin/env python

import base64, json, os, stat, sys, getopt
from time import sleep

from ambari_client import AmbariClient
from ambari_error import AmbariError

def run(service_name):
    try:
        resp = ac.check_service(service_name)
        return resp["Requests"]["id"]
    except AmbariError as e:
        print(e.message)

def run_list(service_name_list):
    try:
        resp = ac.check_service_batch(service_name_list)
        return resp["resources"][0]["RequestSchedule"]["id"]
    except AmbariError as e:
        print(e.message)

def run_all():
    try:
        resp = ac.check_service_batch(ac.get_service_list())
        return resp["resources"][0]["RequestSchedule"]["id"]
    except AmbariError as e:
        print(e.message)

def print_help():
    print 'Usage:'
    print 'test.py'
    print 'test.py -c <config>'
    print 'test.py -s <services_comma_separeted>'
    print 'test.py -c <config> -s <services_comma_separeted>'

def main(argv):
    config_file = "../conf/config"
    service_name_list = ""
    try:
        opts, args = getopt.getopt(argv,"hc:s:")
    except getopt.GetoptError:
        print_help()
        exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print_help()
            exit()
        elif opt in ("-c"):
            config_file = arg
        elif opt in ("-s"):
            service_name_list = arg.split(",")

    try:
        if int(oct((os.stat(config_file)).st_mode)[-2:]) > 0:
            print("Please set the correct permission on the config file, aborting...")
            exit(1)
        config = json.loads(open(config_file, "r").read())
        global ac
        ac = AmbariClient(config["hostname"],config["port"],config["cluster_name"],base64.b64encode("{0}:{1}".format(config["user"],config["password"])),config["ssl"])
    except OSError as e:
        print(e.strerror)
        exit(1)
    except KeyError as e:
        print("Config json is not valid, please check")
        exit(1)

    id = run_all() if not service_name_list else run_list(service_name_list)
    while True:
        status = ac.check_batch_job_status(id)
        print(status)
        if status != "SCHEDULED":
            print ac.check_batch_job(id)
            break
        sleep(15)

if __name__== "__main__":
    main(sys.argv[1:])
