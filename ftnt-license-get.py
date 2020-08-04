#! /usr/bin/env python3

import json
import logging
import os
import sys
from optparse import OptionParser

import requests

api_url = 'https://Support.Fortinet.COM/ES/FCWS_RegistrationService.svc/REST'
api_token = '<YOUR_FORTICARE_API_TOKEN>'

def init_logging():

    global logger

    prog = os.path.basename(sys.argv[0])
    
    # create logger
    logger = logging.getLogger(prog)
    logger.setLevel(logging.DEBUG)

    # create console handler and set level to debug
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)

    # create formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # add formatter to ch
    ch.setFormatter(formatter)

    # add ch to logger
    logger.addHandler(ch)
    
    return logger

def build_payload(sn):
    json_payload = { 
        'Token': api_token,
        'Version': '1.0',
        'Serial_Number': sn,
    }

    logger.debug('Payload to post is: %s' % json_payload)
    return json_payload

def retrieve_license(payload):
    api_function = 'REST_DownloadLicense'
    url = api_url + '/' + api_function
    r = requests.post(url=url, json=payload)
    logger.debug('Retrieved license information, status code is "%s"' % r.json()['Message'])
    return r.json()['License_File']

def write_license_file(lic, file):
    logger.debug('Creating output file %s' % file)
    f = open(file, 'w')
    f.write(lic)
    f.close()

def init_option_parser():
    usage = 'usage: %prog -s|--serial SERIAL [ --file FILENAME ] [ -v|--verbose ]'
    
    parser = OptionParser(usage=usage)

    parser.add_option(
        '-f', '--file', 
        dest='file', 
        metavar='FILENAME',
        help='License output filename.')
    parser.add_option(
        '-s', '--serial', 
        dest='sn', 
        metavar='SERIAL',
        help='Serial number of the unit you want the license for.')
    parser.add_option(
        '-v', '--verbose',
        dest='verbose', action='store_true',
        default=False, help='Verbose output')
    
    (options, args) = parser.parse_args()

    if options.sn is None:
        parser.error('Serial number not specified.')

    return (options,args)

def main():
    init_logging()
    (options, args) = init_option_parser()

    sn = options.sn
    file = options.file
    
    if file is None:
        file = sn + '.lic'

    if options.verbose is False:
        logger.setLevel(logging.INFO)
    
    my_payload = build_payload(sn)
    lic = retrieve_license(my_payload)
    write_license_file(lic, file)

if __name__ == '__main__':
        main()
