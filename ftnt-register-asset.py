#! /usr/bin/env python3

import json
import logging
import os
import sys
import configparser
import re
from optparse import OptionParser

import requests

def init_forticare(file='.forticare'):

    """
    Initialize code with both the forticare url and token retrieved from a
    config file.

    Arguments:
    file -- the config file in INI format (default to .forticare)

    Returned values:
    forticare_url   -- the FortiCare url
    forticare_token -- the FortiCare token
    """

    config = configparser.ConfigParser()
    config.read(file)
    section = 'forticare'

    try:
        forticare_url = config[section]['url']
        forticare_token = config[section]['token']    
    except KeyError as k:
        logger.error('Missing key {} in configuration file "{}"'.format(k, file))
        quit()

    logger.debug(f'FortiCare URL: {forticare_url}, FortiCare Token: {forticare_token}')
    
    return forticare_url, forticare_token

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

def build_payload_product(options):

    if options.ip is None:
        options.ip = ''
        logger.debug('No IP address specified, set payload with an empty string.')

    if options.sn is None:
        options.sn = ''
        logger.debug('No Serial number specified, set payload with an empty string.')

    json_payload = {
        "Token": forticare_token,
        "Version": "1.0",
        "RegistrationUnits": [
            {
                "Serial_Number": options.sn,
                "Contract_Number": options.code,
                "Additional_Info": options.ip,
                "Is_Government": False,
            }
        ]
    }

    logger.debug('Payload to post is:')
    logger.debug(json.dumps(json_payload, indent=4))
    return json_payload

def build_payload_license(options):

    if options.ip is None:
        options.ip = ''
        logger.debug('No IP address specified, set payload it with an empty string.')

    if options.sn is None:
        options.sn = ''
        logger.debug('No Serial number specified, set payload with an empty string.')

    json_payload = {
        "Token": forticare_token,
        "Version": "1.0",
        "Serial_Number": options.sn,
        "License_Registration_Code": options.code,
        "Description": options.desc,
        "Additional_Info": options.ip,
        "Is_Government": False,
    }

    logger.debug('Payload to post is:')
    logger.debug(json.dumps(json_payload, indent=4))
    return json_payload

def do_register(api_function, payload):
    url = forticare_url + '/' + api_function
    r = requests.post(url=url, json=payload)
    logger.debug('Registration operation terminated with "%s"' % r.json()['Message'])
    logger.debug('JSON output is:')
    logger.debug(json.dumps(r.json(), indent=4))

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

def register_product(options):
    my_payload = build_payload_product(options)
    api_function = 'REST_RegisterUnits'
    do_register(api_function, my_payload)

def register_license(options):
    my_payload = build_payload_license(options)
    api_function = 'REST_RegisterLicense'
    jres = do_register(api_function, my_payload)

    if options.lic:
        logger.debug('Option --lic specified so license file will be saved.')
        file = jres['AssetDetails']['Serial_Number'] + ".lic"
        lic = jres['AssetDetails']['License']['License_File']
        write_license_file(lic, file)

def is_product(options):
    """
    Return whether the code we're using is for a "product" or a "license".
    If it's for a "product" then it means we're adding a service entitlement. If
    it's for a "license" then it means we're registering a new FGT, FMG or FAZ
    VM.
    
    Arguments:
    options:    The global dict initialized with function init_option_parser() 

    Returned values:
    True:      The code corresponds to a product
    False:     The code corresponds to a license
    """

    code = options.code
    result = re.search('-', code)

    return False if result else True

def main():

    global forticare_url, forticare_token

    init_logging()
    init_option_parser()
    forticare_url, forticare_token = init_forticare()

    if options.verbose is False:
        logger.setLevel(logging.INFO)

    if is_product(options):
        # Register Product
        register_product(options)
    else:
        # Register License
        register_license(options)

if __name__ == '__main__':
    main()
