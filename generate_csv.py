#! /usr/bin/env python3

import zipfile
import PyPDF2
import re
import argparse



file = 'FG-VMUL_27228668.zip'

def get_registration_code(string):
    result = re.search('Registration Code\s+:\s+(.{29})', string)

    if result:
        return result.group(1) 
    else:
        return None                        

def get_serial_number(string):
    result = re.search('Evaluation license term\s+:\s+[0-9]{1,3}\s+days\s+[0-9A-Z-]{7}(.{14})', string)
    print(result)
    if result:
        return result.group(1)
    else:
        return None

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

    args = parser.parse_args()

    return (args.zip_file[0],
            args.ip[0],
            args.desc[0])

if __name__ == '__main__':

    zip_file, ip, desc = parse_command_line_arguments()

    # Write the CVS output on STDOUT
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
