#! /usr/bin/env python3

import zipfile
import PyPDF2
import re
import argparse
import os 

# Global
license_types = {
    'FG': 'FortiGate VM',
    'FMG': 'FortiManager VM',
    'FAZ': 'FortiAnalyzer VM',
    'FC': 'Service Entitlement',
}

def get_registration_code(string):
    result = re.search('Registration Code\s+:\s+(.{30})', string)

    return result.group(1) if result else None

def get_contract_registration_code(string):
    result = re.search('ContractRegistrationCode:(.{12})', string)

    return result.group(1) if result else None    

def get_serial_number(string):
    result = re.search('Evaluation license term\s+:\s+[0-9]{1,3}\s+days\s+[0-9A-Z-]{7}(.{14})', string)

    return result.group(1) if result else None

def parse_command_line_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--file', 
                        dest='zip_file', 
                        nargs=1,
                        required=True,
                        help='Specify a zip file')
    parser.add_argument('-d', '--desc', 
                        dest='desc', 
                        nargs=1,
                        required=True,                        
                        help='Indicate a description')

    parser.add_argument('-i', '--ip', 
                        dest='ip',
                        nargs=1,
                        required=True,                        
                        help='Indicate the license IP address')
    parser.add_argument('-l', '--licenses',
                        dest='licenses',
                        nargs=1,
                        required=False,
                        default=None,
                        help="Indicate a folder with FortiGate-VM .lic files")

    args = parser.parse_args()

    licenses = args.licenses[0] if args.licenses else None
        
    return (args.zip_file[0],
            args.ip[0],
            args.desc[0],
            licenses)

def get_license_type(zip_file):
    result = re.search('([A-Z]{2,3})-', zip_file)
    return result.group(1) if result else None

def get_fgt_sn_from_licenses_folder(licenses):
    """
    Retrieve the FortiGate serial number from the .lic files contained in
    "licenses" folder. Normally, this folder should contain file with <sn>.lic
    as naming convention. This function is returning the list of all <sn>.

    Arguments:
    licenses: a folder with one or multiple <sn>.lic file(s)

    Returned values:
    fgt_sns = list of serial numbers
    """
    fgt_sns = None

    with os.scandir(licenses) as entries:
        for entry in entries:
            filename = entry.name
            result = re.search('(FG.+)\.lic', filename)
            if result:
                sn = result.group(1)
                if fgt_sns:
                    fgt_sns.append(sn)
                else:
                    fgt_sns = [sn]

    return fgt_sns
    
def write_csv_output_fc(zip_file, ip, desc, licenses):
    fgt_sns = get_fgt_sn_from_licenses_folder(licenses)
    index_sn = 0
    with zipfile.ZipFile(zip_file) as myzip:
        for pdf_file_name in myzip.namelist():
            pdf_file_handler = myzip.open(pdf_file_name)
            pdf_reader = PyPDF2.PdfFileReader(pdf_file_handler)
            # Contract Registration Code is on page 2 (ie. index 1)
            page_text = pdf_reader.getPage(1).extractText()
            #print(page_text)
            registration_code = get_contract_registration_code(page_text)
            sn = fgt_sns[index_sn]
            index_sn += 1
            print('{},{},{},{}'.format(registration_code,
                                    ip,
                                    desc,
                                    sn))

def write_csv_output_fgt_fmg_faz(zip_file, ip, desc):
    with zipfile.ZipFile(zip_file) as myzip:
        for pdf_file_name in myzip.namelist():
            pdf_file_handler = myzip.open(pdf_file_name)
            pdf_reader = PyPDF2.PdfFileReader(pdf_file_handler)
            page_text = pdf_reader.getPage(0).extractText()
            #print(page_text)            
            registration_code = get_registration_code(page_text)
            print('{},{},{}'.format(registration_code,
                                    ip,
                                    desc))

if __name__ == '__main__':

    zip_file, ip, desc, licenses = parse_command_line_arguments()

    # Figure out the license type based on the ZIP file name
    license_type = get_license_type(zip_file)

    license_type_string = license_types.get(license_type)
    if license_type_string:
        print('# ZIP file is for [{}] license(s).'.format(license_types[license_type]))
        if license_type == 'FC':
            write_csv_output_fc(zip_file, ip, desc, licenses)
        else:
            write_csv_output_fgt_fmg_faz(zip_file, ip, desc)
    else:
        print('Unknown license type: please check the given ZIP file')
