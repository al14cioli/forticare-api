# coding: utf-8

"""Extract registration code from a bunch of PDF files in a ZIP archive and generate a CSV file."""

import argparse
import os
import re
import zipfile
from pathlib import Path

import PyPDF2

# Global
license_types = {
    "FG": "FortiGate VM",
    "FMG": "FortiManager VM",
    "FAC": "FortiAuthenticator VM",
    "FAZ": "FortiAnalyzer VM",
    "FPC": "FortiPortal VM",
    "FC": "Service Entitlement",
    "FC7": "FortiGate-VM (unlimited CPU) Subscription License with 360 Protection Bundle", 
}


def get_registration_code(string, license_type):
    """
    Extract the registration code.

    Parameters
    ----------
        string: str
            the string pattern from which is extracted the registration code.

        license_type: str
            one of the key from the dict global variable "license_types"

    Returns
    -------
        result:
            the found registration code
        None:
            None if no code is found in string.
    """
    if license_type == "FC7":
        result = re.search(r"ContractRegistrationCode:(.{12})", string)
    else:
        result = re.search(r"Registration Code\s+:\s+(.{30})", string)        

    return result.group(1) if result else None


def get_contract_registration_code(string):
    """
    Extract the contract registration code.

    Parameters
    ----------
        string: str
            the string pattern from which is extracted the contract registration code.

    Returns
    -------
        result:
            the found contract registration code
        None:
            None if no code is found in string.
    """
    result = re.search(r"ContractRegistrationCode:(.{12})", string)

    return result.group(1) if result else None


def get_serial_number(string):
    """
    Extract and return the serial number.

    Parameters
    ----------
        string: str
            the string pattern from which is extracted the serial number.

    Returns
    -------
        result:
            the found serial number.
        None:
            None if no serial number is found in string.
    """
    result = re.search(
        r"Evaluation license term\s+:\s+[0-9]{1,3}\s+days\s+[0-9A-Z-]{7}(.{14})", string
    )

    return result.group(1) if result else None


def parse_command_line_arguments():
    """
    Commande line management with an argparse instance.

    Returns
    -------
        (file, ip, desc, folder): (str, str, str, str)
            - file: the zip file that contains the PDF files.
            - ip: the IP address to use for the licenses
            - desc: a description for the licenses
            - folder: the folder where the licenses are.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-f",
        "--file",
        dest="zip_file",
        nargs=1,
        required=True,
        help="Specify a zip file",
    )
    parser.add_argument(
        "-d",
        "--desc",
        dest="desc",
        nargs=1,
        required=True,
        help="Indicate a description",
    )

    parser.add_argument(
        "-i",
        "--ip",
        dest="ip",
        nargs=1,
        required=True,
        help="Indicate the license IP address",
    )
    parser.add_argument(
        "-l",
        "--licenses",
        dest="licenses",
        nargs=1,
        required=False,
        default=None,
        help="Indicate a folder with FortiGate-VM .lic files",
    )

    args = parser.parse_args()

    licenses = args.licenses[0] if args.licenses else None

    return (args.zip_file[0], args.ip[0], args.desc[0], licenses)


def get_license_type(zip_file):
    """
    Extract the first 2 or 3 letters at the begining of the ZIP file name.

    Parameters
    ----------
        zip_file: str
            the ZIP file name

    Returns
    -------
        result.group(1): str
            the first 2 or 3 letters extracted from the ZIP file name.
    """
    result = re.search(r"([A-Z0-9]{2,3})-", zip_file)
    return result.group(1) if result else None


def get_fgt_sn_from_licenses_folder(licenses):
    """
    Retrieve the FortiGate serial number from the .lic files contained in "licenses" folder. Normally, this folder should contain file with <sn>.lic as naming convention. This function is returning the list of all <sn>.

    Parameters
    ----------
        licenses: str
            a folder with one or multiple <sn>.lic file(s).

    Returns
    -------
        fgt_sns: list
            list of serial numbers.
    """
    fgt_sns = None

    with os.scandir(licenses) as entries:
        for entry in entries:
            filename = entry.name
            result = re.search(r"(FG.+)\.lic", filename)
            if result:
                sn = result.group(1)
                if fgt_sns:
                    fgt_sns.append(sn)
                else:
                    fgt_sns = [sn]

    return fgt_sns


def write_csv_output_fc(zip_file, ip, desc, licenses):
    """
    Write a CSV file for product licenses.

    Parameters
    ----------
        zip_file: str
            the ZIP file name from where to extract the registration code.

        ip: str
            the IP address to associate to the licenses.

        desc: str
            the description to associate to the licenses.

        licenses: str
            the folder where are the license files.
    """
    fgt_sns = get_fgt_sn_from_licenses_folder(licenses)
    index_sn = 0
    with zipfile.ZipFile(zip_file) as myzip:
        myzip.extractall()
        for pdf_file_name in myzip.namelist():
            file = Path(pdf_file_name)
            with open(pdf_file_name, "rb") as f:
                pdf_reader = PyPDF2.PdfFileReader(f)
                # Contract Registration Code is on page 2 (ie. index 1)
                page_text = pdf_reader.getPage(1).extractText()
            f.close()
            file.unlink()
            registration_code = get_contract_registration_code(page_text)
            sn = fgt_sns[index_sn]
            index_sn += 1
            print("{},{},{},{}".format(registration_code, ip, desc, sn))


def write_csv_output(zip_file, ip, desc, license_type):
    """
    Write a CSV file for licenses.

    Parameters
    ----------
        zip_file: str
            the ZIP file name from where to extract the registration code.

        ip: str
            the IP address to associate to the licenses.

        desc: str
            the description to associate to the licenses.

        license_type: str
            one of the key from the dict global variable "license_types"
    """
    with zipfile.ZipFile(zip_file) as myzip:
        myzip.extractall()
        for pdf_file_name in myzip.namelist():
            file = Path(pdf_file_name)
            with open(pdf_file_name, "rb") as f:
                pdf_reader = PyPDF2.PdfFileReader(f)
                if license_type == "FC7":
                    # Registration Code is on page 2 (ie. index 1)
                    page_text = pdf_reader.getPage(1).extractText()
                else:
                    # Registration Code is on page 1 (ie. index 0)
                    page_text = pdf_reader.getPage(0).extractText()                    
            f.close()
            file.unlink()
            registration_code = get_registration_code(page_text, license_type)
            print("{},{},{}".format(registration_code, ip, desc))


if __name__ == "__main__":

    zip_file, ip, desc, licenses = parse_command_line_arguments()

    # Figure out the license type based on the ZIP file name
    license_type = get_license_type(zip_file)

    license_type_string = license_types.get(license_type)
    if license_type_string:
        print("# ZIP file is for [{}] license(s).".format(license_types[license_type]))
        if license_type == "FC":
            write_csv_output_fc(zip_file, ip, desc, licenses)
        else:
            write_csv_output(zip_file, ip, desc, license_type)
    else:
        print("Unknown license type: please check the given ZIP file")
