from chardet.universaldetector import UniversalDetector
import csv
import os
import pandas as pd
import xlrd


class import_file:

    def __init__ (self, file):
        self.file = file

    def __fabric (self, format_file):
        if format_file == 'text/plain':
            CSV = CSV_reader(self.file)
            DF = CSV.parse()
            return DF
        elif 'application/vnd.ms-excel' in format_file or 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' in format_file:
            XLS = XLS_reader(self.file)
            DF = XLS.parse()
            return DF
        else:
            raise Exception(format_file, ' - format is not supported')

    def read (self):
        detecter = detect_format(self.file)
        format_file = detecter.detect()
        return self.__fabric(format_file)


class detect_format:

    def __init__ (self, file):
        self.file = file
        self.data = 'data.json'

    def detect (self):
        print('fab')
        with open(self.file, 'rb') as file:
            file_d = file.read(128)
        with open(self.data) as data_file:
            data = json.loads(data_file.read())
        stream = " ".join(['{:02X}'.format(byte) for byte in file_d])
        mime_list = []
        for element in data:
            for signature in element["signature"]:
                offset = element["offset"] * 2 + element["offset"]
                if signature == stream[offset:len(signature) + offset]:
                    mime_list.append(element['mime'])
        if len(mime_list)==0:
            with open(self.file, 'r') as file:
                file_d = file.read(250)
                if '\n' in file_d:
                    return 'text/plain'
                else:
                    return 'unknown'
        else:
            return mime_list


class CSV_reader (import_file):

    def __init__ (self, file):
        self.file = file

    def __find_encoding (self):
        detector = UniversalDetector()
        with open(self.file, 'rb') as fh:
            for i,line in enumerate(fh):
                detector.feed(line)
                if i>10:
                    break
        detector.close()
        encoding = detector.result['encoding']
        return encoding

    def __find_sep (self):
        encoding = self.__find_encoding()
        SEPARATORS=['\x00', '\x01',  '^', ':', ',', '\t', ':', ';', '|', '~', ' ']
        with open(self.file, 'r', encoding=encoding) as csvfile:
            line = next(csvfile)
            try:
                dialect = csv.Sniffer().sniff(line, SEPARATORS)
                sep = dialect.delimiter
            except:
                sep = '\t'
            return sep, encoding

    def parse (self):
        sep, encoding = self.__find_sep()
        try:
            DF = pd.read_csv(self.file, sep=sep, encoding=encoding)
            return DF
        except Exception as E:
            raise Exception('Bad, format error:', E)

class XLS_reader (import_file):

    def __init__ (self, file):
        self.file = file

    def count_sheets (self):
        wb = xlrd.open_workbook(self.file, on_demand=True)
        count_st = len(wb.sheet_names())
        if count_st > 1:
            print('WARNING: where ', count_st, ' in file. Names of sheets', wb.sheet_names())

    def parse (self, sheet_name=0):
        self.count_sheets()
        try:
            DF = pd.read_excel(self.file, sheet_name=sheet_name)
            return DF
        except Exception as E:
            raise Exception('Bad, format error:', E)
