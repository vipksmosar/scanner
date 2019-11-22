from chardet.universaldetector import UniversalDetector
import csv
import os

import pandas as pd
import magic
import xlrd




class import_file:
    
    def __init__ (self, file):
        self.file = file
    
    def __detect_format (self):
        #mime = MimeTypes()
        #mime_type = mime.guess_type(self.file)[0]
        mime_type = magic.from_file(self.file, mime=True)
        return mime_type
        
    def __fabric (self, format_file):
        if format_file == 'text/plain':
            CSV = CSV_reader(self.file)
            DF = CSV.parse()
            return DF
        elif format_file == 'application/vnd.ms-excel':
            XLS = XLS_reader(self.file)
            DF = XLS.parse()
            return DF
        else:
            raise Exception(format_file, ' - format is not supported')
    def read (self):
        format_file = self.__detect_format()
        return self.__fabric(format_file)

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
        
