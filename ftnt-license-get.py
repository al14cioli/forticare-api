# coding: utf-8

"""Retrieve a license file from a serial number."""

import logging
import os
import sys
from optparse import OptionParser

import requests

api_url = "https://Support.Fortinet.COM/ES/FCWS_RegistrationService.svc/REST"
api_token = "<YOUR_FORTICARE_API_TOKEN>"


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


def build_payload(sn):
    """
    Build the JSON payload.

    Parameters
    ----------
    sn: str
        The serial number of the device.

    Returns
    -------
    json_payload: dict
        A JSON dictionnary.
    """
    json_payload = {
        "Token": api_token,
        "Version": "1.0",
        "Serial_Number": sn,
    }

    logger.debug("Payload to post is: %s" % json_payload)
    return json_payload


def retrieve_license(payload):
    """
    Retrieve the license file with an API call.

    parameters
    ----------
        payload: dict
            The JSON payload for that is passed to the API call.

    Returns
    -------
        license: str
            The content of the license file.
    """
    api_function = "REST_DownloadLicense"
    url = api_url + "/" + api_function
    r = requests.post(url=url, json=payload)
    logger.debug(
        'Retrieved license information, status code is "%s"' % r.json()["Message"]
    )
    return r.json()["License_File"]


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


def init_option_parser():
    """
    Initialize an option parser object.

    Returns
    -------
        (options,args): tuple
            A tuple as returned by the optparse module.
    """
    usage = "usage: %prog -s|--serial SERIAL [ --file FILENAME ] [ -v|--verbose ]"

    parser = OptionParser(usage=usage)

    parser.add_option(
        "-f", "--file", dest="file", metavar="FILENAME", help="License output filename."
    )
    parser.add_option(
        "-s",
        "--serial",
        dest="sn",
        metavar="SERIAL",
        help="Serial number of the unit you want the license for.",
    )
    parser.add_option(
        "-v",
        "--verbose",
        dest="verbose",
        action="store_true",
        default=False,
        help="Verbose output",
    )

    (options, args) = parser.parse_args()

    if options.sn is None:
        parser.error("Serial number not specified.")

    return (options, args)


if __name__ == "__main__":
    init_logging()
    (options, args) = init_option_parser()

    sn = options.sn
    file = options.file

    if file is None:
        file = sn + ".lic"

    if options.verbose is False:
        logger.setLevel(logging.INFO)

    my_payload = build_payload(sn)
    lic = retrieve_license(my_payload)
    write_license_file(lic, file)
