# coding: utf-8

"""
Register a product entitlement or license.

In the case of a license, it can retrieve its license file.
"""

import configparser
import json
import logging
import os
import re
import sys
from optparse import OptionParser

import requests


def init_forticare(file=".forticare"):
    """
    Initialize code with both the forticare url and token retrieved from a config file.

    Parameters
    ----------
    file: str
        the config file in INI format (default to .forticare)

    Returns
    -------
    forticare_url: str
        the FortiCare url.
    forticare_token: str
        the FortiCare token.
    """
    config = configparser.ConfigParser()
    config.read(file)
    section = "forticare"

    try:
        forticare_url = config[section]["url"]
        forticare_token = config[section]["token"]
    except KeyError as k:
        logger.error('Missing key {} in configuration file "{}"'.format(k, file))
        quit()

    logger.debug(f"FortiCare URL: {forticare_url}, FortiCare Token: {forticare_token}")

    return forticare_url, forticare_token


def init_logging():
    """Initialize and return an Logger object.

    Returns
    -------
        logger: logger
            The logger object.
    """
    global logger

    prog = os.path.basename(sys.argv[0])

    # create logger
    logger = logging.getLogger(prog)
    logger.setLevel(logging.DEBUG)

    # create console handler and set level to debug
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)

    # create formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # add formatter to ch
    ch.setFormatter(formatter)

    # add ch to logger
    logger.addHandler(ch)

    return logger


def build_payload_product(options):
    """
    Build the JSON payload for a product entitlement.

    Parameters
    ----------
    options: dict
        Dictionnary as returned by the optparser module.

    Returns
    -------
    json_payload: dict
        A JSON payload to be used in the API call.
    """
    if options.ip is None:
        options.ip = ""
        logger.debug("No IP address specified, set payload with an empty string.")

    if options.sn is None:
        options.sn = ""
        logger.debug("No Serial number specified, set payload with an empty string.")

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
        ],
    }

    logger.debug("Payload to post is:")
    logger.debug(json.dumps(json_payload, indent=4))
    return json_payload


def build_payload_license(options):
    """
    Build the JSON payload for a product license.

    Parameters
    ----------
    options: dict
        Dictionnary as returned by the optparser module.

    Returns
    -------
    json_payload: dict
        A JSON payload to be used in the API call.
    """
    if options.ip is None:
        options.ip = ""
        logger.debug("No IP address specified, set payload it with an empty string.")

    if options.sn is None:
        options.sn = ""
        logger.debug("No Serial number specified, set payload with an empty string.")

    json_payload = {
        "Token": forticare_token,
        "Version": "1.0",
        "Serial_Number": options.sn,
        "License_Registration_Code": options.code,
        "Description": options.desc,
        "Additional_Info": options.ip,
        "Is_Government": False,
    }

    logger.debug("Payload to post is:")
    logger.debug(json.dumps(json_payload, indent=4))
    return json_payload


def do_register(api_function, payload):
    """
    Perform the API call as per the function and payload given in arguments.

    Parameters
    ----------
        api_function: str
            the API methode to call.
        payload:
            the JSON payload to pass to the call.

    Returns
    -------
        r.json: dict
            the content of the API call response in JSON format.
    """
    url = forticare_url + "/" + api_function
    r = requests.post(url=url, json=payload)
    logger.debug('Registration operation terminated with "%s"' % r.json()["Message"])
    logger.debug("JSON output is:")
    logger.debug(json.dumps(r.json(), indent=4))

    return r.json()


def init_option_parser():
    """
    Initialize an option parser object.

    Returns
    -------
        (options,args): tuple
            A tuple as returned by the optparse module.
    """
    global options, args

    usage = (
        "usage: %prog -c|--code REGCODE [ -d|--description DESCRIPTION ]"
        "[ -a|--address IPADDRESS ] [ -s|--serial SERIAL ]"
        "[ -l|--lic ] [ -v|--verbose ]"
    )

    parser = OptionParser(usage=usage)

    parser.add_option(
        "-c",
        "--code",
        dest="code",
        metavar="REGCODE",
        help="Registration code.",
    )
    parser.add_option(
        "-a",
        "--address",
        dest="ip",
        metavar="IPADDRESS",
        help="Managemen IP Address if required.",
    )
    parser.add_option(
        "-d",
        "--description",
        dest="desc",
        metavar="DESCRIPTION",
        help="Description field.",
    )
    parser.add_option(
        "-s",
        "--serial",
        dest="sn",
        metavar="SERIAL",
        help="Serial number associated with the registration code.",
    )
    parser.add_option(
        "-v",
        "--verbose",
        dest="verbose",
        action="store_true",
        default=False,
        help="Verbose output",
    )
    parser.add_option(
        "-l",
        "--lic",
        dest="lic",
        action="store_true",
        default=False,
        help=(
            "Retrieve the license file during the registration"
            "(filename is <SERIALNUMBER>.lic)."
        ),
    )
    (options, args) = parser.parse_args()

    #    if options.desc is None:
    #        parser.error('Description not specified.')

    if options.code is None:
        parser.error("Registration code not specified.")


def write_license_file(lic, file):
    """
    Write the content of the license to a file.

    Parameters
    ----------
        lic: str
            The content of the license file.
        file: str
            The file name.

    Returns
    -------
        None.
    """
    logger.debug("Creating output file %s" % file)
    f = open(file, "w")
    f.write(lic)
    f.close()


def register_product(options):
    """
    Register a product entitlement.

    Parameters
    ----------
    options: dict
        Dictionnary as returned by the optparser module.

    Returns
    -------
    None
    """
    my_payload = build_payload_product(options)
    api_function = "REST_RegisterUnits"
    do_register(api_function, my_payload)


def register_license(options):
    """
    Register a license and retrieve its license depending of the options provided during the script invocation.

    Parameters
    ----------
    options: dict
        Dictionnary as returned by the optparser module.

    Returns
    -------
    None
    """
    my_payload = build_payload_license(options)
    api_function = "REST_RegisterLicense"
    jres = do_register(api_function, my_payload)

    if options.lic:
        logger.debug("Option --lic specified so license file will be saved.")
        file = jres["AssetDetails"]["Serial_Number"] + ".lic"
        lic = jres["AssetDetails"]["License"]["License_File"]
        write_license_file(lic, file)


def is_product(options):
    """
    Return whether the code we're using is for a "product" or a "license". If it's for a "product" then it means we're adding a service entitlement. If it's for a "license" then it means we're registering a new FGT, FMG or FAZ VM.

    Parameters
    ----------
    options: dict
        the global dict initialized with function init_option_parser().

    Returns
    -------
    True: Boolean
        the code corresponds to a product.
    False: Boolean
        the code corresponds to a license
    """
    code = options.code
    result = re.search("-", code)

    return False if result else True


if __name__ == "__main__":
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
