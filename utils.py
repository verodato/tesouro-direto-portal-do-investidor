import re


def clean_string_BRL(data):
    '''Convert from this format R$0.00 to 0.00'''
    string = re.sub('R\$|\.', '', data)
    string = re.sub(',', '.', string)
    return string


def clean_percent(data):
    '''Convert from this format 0,00% to 0.00'''
    data = re.sub('%', '', data)
    data = re.sub(',', '.', data)
    return data
