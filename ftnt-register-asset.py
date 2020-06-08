#! /usr/bin/env python3

import json
import logging
import os
import sys
from optparse import OptionParser

import requests

api_url = 'https://Support.Fortinet.COM/ES/FCWS_RegistrationService.svc/REST'
api_token = '153C-9GBH-I4AV-O5Q2-Y0BX-H1TB-OA32-GKW6'

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

def build_payload(options):

    if options.ip is None:
        options.ip = ''
        logger.debug('No IP address specified, set payload it with an empty string.')

    if options.sn is None:
        options.sn = ''
        logger.debug('No Serial number specified, set payload with an empty string.')

    json_payload = {
        "Token": api_token,
        "Version": "1.0",
        "Serial_Number": options.sn,
        "License_Registration_Code": options.code,
        "Description": options.desc,
        "Additional_Info": options.ip,
        "Is_Government": False,
    }

    logger.debug('Payload to post is: %s' % json_payload)
    return json_payload

def register(payload):
    api_function = 'REST_RegisterLicense'
    url = api_url + '/' + api_function
    r = requests.post(url=url, json=payload)
    logger.debug('Registration operation terminated with "%s"' % r.json()['Message'])
    logger.debug('JSON output is:\n%s' % r.json())

    return r.json()

def init_option_parser():
    global options, args

    usage = 'usage: %prog -c|--code REGCODE [ -d|--description DESCRIPTION ] [ -a|--address IPADDRESS ] [ -s|--serial SERIAL ] [ -l|--lic ] [ -v|--verbose ]'
    
    parser = OptionParser(usage=usage)

    parser.add_option(
        '-c', '--code', 
        dest='code', 
        metavar='REGCODE',
        help='Registration code.')
    parser.add_option(
        '-a', '--address', 
        dest='ip', 
        metavar='IPADDRESS',
        help='Managemen IP Address if required.')
    parser.add_option(
        '-d', '--description', 
        dest='desc', 
        metavar='DESCRIPTION',
        help='Description field.')
    parser.add_option(
        '-s', '--serial', 
        dest='sn', 
        metavar='SERIAL',
        help='Serial number associated with the registration code.')
    parser.add_option(
        '-v', '--verbose',
        dest='verbose', action='store_true',
        default=False, help='Verbose output')
    parser.add_option(
        '-l', '--lic', 
        dest='lic', action='store_true', default=False,
        help='Retrieve the license file during the registration (filename is <SERIALNUMBER>.lic).')
    
    (options, args) = parser.parse_args()

#    if options.desc is None:
#        parser.error('Description not specified.')

    if options.code is None:
        parser.error('Registration code not specified.')

def write_license_file(lic, file):
    logger.debug('Creating output file %s' % file)
    f = open(file, 'w')
    f.write(lic)
    f.close()
    
def main():
    init_logging()
    init_option_parser()

    if options.verbose is False:
        logger.setLevel(logging.INFO)
    
    my_payload = build_payload(options)
    jres = register(my_payload)

    if options.lic:
        logger.debug('Option --lic specified so license file will be saved.')
        file = jres['AssetDetails']['Serial_Number'] + ".lic"
        lic = jres['AssetDetails']['License']['License_File']
        write_license_file(lic, file)

if __name__ == '__main__':
        main()
