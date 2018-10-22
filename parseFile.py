# coding=utf-8
from  bs4 import BeautifulSoup
from bs4.diagnose import diagnose

def parse_html_file(file_to_parse):
    try:
        with open(file_to_parse) as ftp:
            # parse html file to tree object
            try:
                soup = BeautifulSoup(ftp, 'lxml') #lxml is the fastest, but least lenient parser
            except Exception as e:
                try:
                    soup = BeautifulSoup(ftp, 'html.parser') #built-in parser, decent speed and leniency
                except Exception as e2:
                    try:
                        soup = BeautifulSoup(ftp, 'html5lib') #slowest, most lenient parser
                    except Exception as e3:
                        error_message = diagnose(ftp.read())
                        print(error_message)
                        print("Error parsing {0} with lxml: ".format(file_to_parse), e)
                        print("Error parsing {0} with html.parser: ".format(file_to_parse), e2)
                        print("Error parsing {0} with html5lib: ".format(file_to_parse), e3)
                        #TODO write to error collection
                        return None

            return soup
    except Exception as e4:
        print("File error: ", e4)
        #TODO write to error collection
        return None
