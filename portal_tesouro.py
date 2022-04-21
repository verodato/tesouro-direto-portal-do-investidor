#!/usr/bin/env python
# -*- coding: utf-8 -*-

from browser import Browser
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pandas as pd
import os
import requests
import time
import json
from utils import *
from settings import path, pw, cpf

import warnings

warnings.filterwarnings('ignore')
GREEN = '\033[92m[+]\033[0m'
BLUE = '\033[34;1;4m{}\033[0m'
YELLOW = '\033[33m[-]\033[0m'
RED = '\033[31m[*]\033[0m'

'''
    This module interfaces directly with the pages of the direct treasure portal
'''


class PortalTesouro(Browser):
    def __init__(self):
        super().__init__()

    # Interact with the login form
    def login_td(self, cpf, pw):
        WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//input[@class="td-login-input"]')))
        self.driver.find_element(By.XPATH, '//input[@class="td-login-input"]').send_keys(cpf)
        self.driver.find_element(By.XPATH, '//div[contains(text(), "Continuar")]').click()
        print('Login...')
        WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//input[@name="UserPassword"]')))
        self.driver.find_element(By.XPATH, '//input[@name="UserPassword"]').send_keys(pw)
        self.driver.find_element(By.XPATH, '//div[contains(text(), "Entrar")]').click()
        print('Pw...')
        #time.sleep(3)

    # Data structure that will store the operations records found in the portal
    def format_dataframe(self):
        data = {
            'N Protocolo': [],
            'Data Investimento': [],
            'Corretora': [],
            'Status': [],
            'Tipo': [],
            'Titulo': [],
            'Quantidade de titulos': [],
            'Valor unitario': [],
            'Rentabilidade': [],
            'Valor liquido': [],
            'Taxa da instituicao financeira': [],
            'Taxa da B3': [],
            'Valor bruto': []}
        return data

    # Metadata used in the POST type request operation. The server expects this data to return dynamic content
    def set_payload(self, tipo_operacao):
        payload = json.dumps({
            "Operacao": tipo_operacao,
            "InstituicaoFinanceira": "selecione",
            "dataInicial": "",
            "dataFinal": ""
        })
        return payload

    # This object returns a header containing all the necessary parameters to make a request to the server
    # The data to populate this header are coming from cookies that were created in the interaction of the
    # webdriver with the server
    def set_headers(self):
        aspxauth = self.driver.get_cookie('.ASPXAUTH')['value']
        _clck = self.driver.get_cookie('_clck')['value']
        _clsk = self.driver.get_cookie('_clsk')['value']
        rxvt = self.driver.get_cookie('rxvt')['value']
        dtCookie = self.driver.get_cookie('dtCookie')['value']
        big_ip = self.driver.get_cookie('BIGipServerpool_portalinvestidor.tesourodireto.com.br_443')['value']
        __RequestVerificationToken = self.driver.get_cookie('__RequestVerificationToken')['value']
        optanon_consent = self.driver.get_cookie('OptanonConsent')['value']
        dtsa = self.driver.get_cookie('dtSa')['value']
        dtlatc = self.driver.get_cookie('dtLatC')['value']
        dtpc = self.driver.get_cookie('dtPC')['value']
        __RequestToken_form = self.driver.find_element(By.XPATH,
                                                       '//form[@id="__AjaxAntiForgeryForm"]/input['
                                                       '"__RequestVerificationToken"]').get_attribute('value')

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/99.0.4844.84 Safari/537.36',
            'Content-Type': 'application/json; charset=UTF-8',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'X-Requested-With': 'XMLHttpRequest',
            f'__RequestVerificationToken': __RequestToken_form,
            'Origin': 'https://portalinvestidor.tesourodireto.com.br',
            'Referer': 'https://portalinvestidor.tesourodireto.com.br/Consulta',
            'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
            'Cookie': f'__RequestVerificationToken={__RequestVerificationToken}; dtCookie={dtCookie}; '
                      f'BIGipServerpool_portalinvestidor.tesourodireto.com.br_443={big_ip}; .ASPXAUTH={aspxauth}; '
                      f'OptanonConsent={optanon_consent}; _clsk={_clsk}; dtLatC={dtlatc}; dtSa={dtsa}; rxvt={rxvt}; dtPC={dtpc}'
        }
        return headers

    # Definition of an object containing all types of operations
    # that are available in the filter of the portal query screen
    def format_operations(self):
        operations = {
            'Investimento': '1',
            'Investimento programado': '2',
            'Resgate': '3',
            'Resgate programado': '4',
            'Reinvestimento': '5',
            'Outros': '11'
        }
        return operations

    def set_file(self):
        file = [f for f in os.listdir('.') if path in f]
        if file:
            print('Arquivo de dados encontrado.')
            df = pd.read_csv(file[0], sep='\t')
        else:
            print('Criando arquivo para armazenamento de dados.')
            df = pd.DataFrame(columns=self.format_dataframe())
            df.to_csv(path, sep='\t', index=False)
        return df

    def start_scraping(self):

        # Request the main page of portal
        url = 'https://portalinvestidor.tesourodireto.com.br'
        self.driver.get(url)

        # Accept frame cookie
        WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//button[@id="onetrust-accept-btn-handler"]'))).click()
        # Try login
        try:
            self.login_td(cpf=cpf, pw=pw)
        except Exception as e:
            print('Error:',e)
            print('Fill the settings.py file with your credentials.')
            self.close_driver()
            exit(0)

        # Request for the page responsible for showing the registered operations
        self.driver.get('https://portalinvestidor.tesourodireto.com.br/Consulta')
        self.driver.implicitly_wait(10)

        headers = self.set_headers()
        type_operations = self.format_operations()
        data = self.format_dataframe()
        df_saved = self.set_file()
        #print('df_saved', df_saved)
        
        pd.set_option('display.max_rows', 500)


        # From now on we will make requests to the server using the requests library
        # Start of the loop that runs through all the categories of portal operations.
        # Let's take all registered operations and save in a .tsv file
        for key_operations in type_operations:
            payload = self.set_payload(type_operations[key_operations])
            response = requests.request("POST",
                                        'https://portalinvestidor.tesourodireto.com.br/Consulta/LoadOperacoes',
                                        headers=headers,
                                        data=payload,
                                        verify=False)
            if response.status_code == 200:
                # We follow if the server returns the records of operations
                operations_found = json.loads(response.content)['itemsCount']
                if operations_found > 0:
                    print(f'{BLUE.format(key_operations.upper())}: {operations_found} operations found.')
                    # If there are records of operations in the category, we take this page of records
                    # and passed it as a parameter to BeautifulSoup.
                    soup = BeautifulSoup(json.loads(response.content)['view'], 'lxml')
                    # In the soup object, let's get the links that take us to the pages that contain the details of
                    # each operation found.
                    for link in soup.find_all('a'):
                        operations = link.get('href')
                        n_protocol = operations.split("/")[2]
                        # Checking if the operation has already been saved
                        #print(n_protocol)
                        #print(str(df_saved['N Protocolo']))
                        if str(n_protocol) not in str(df_saved['N Protocolo']):
                            print(f'{GREEN} Protocol {n_protocol}: downloading information')
                            # Request operations details page
                            response = requests.request("GET",
                                                        url=url + operations,
                                                        headers=headers,
                                                        verify=False)
                            # Send to BS4.
                            soup = BeautifulSoup(response.content, 'lxml')
                            # Populating the data object with the operations record details
                            data['N Protocolo'].append(
                                soup.find("span", {'class': 'td-protocolo-numero'}).get_text().strip())
                            data['Data Investimento'].append(
                                soup.findAll("span", {'class': 'td-protocolo-info-base--blue'})[2].get_text().strip())
                            data['Corretora'].append(
                                soup.findAll("span", {'class': 'td-protocolo-info-base--blue'})[3].get_text().strip())
                            data['Status'].append(
                                soup.findAll("span", {'class': 'td-protocolo-info-base--blue'})[1].get_text().strip())
                            data['Tipo'].append(
                                soup.findAll("span", {'class': 'td-protocolo-info-base--blue'})[0].get_text().strip())
                            data['Titulo'].append(
                                soup.find("h3", {'class': 'td-protocolo-info-titulo'}).get_text().strip())
                            data['Quantidade de titulos'].append(clean_string_BRL(
                                soup.find_all("span", {'class': 'td-protocolo-info--valor'})[0].get_text().strip()))
                            data['Valor unitario'].append(clean_string_BRL(
                                soup.find_all("span", {'class': 'td-protocolo-info--valor'})[1].get_text().strip()))
                            data['Rentabilidade'].append(clean_percent(
                                soup.find_all("span", {'class': 'td-protocolo-info--valor'})[2].get_text().strip()))
                            data['Valor liquido'].append(clean_string_BRL(
                                soup.find_all("span", {'class': 'td-protocolo-info--valor'})[3].get_text().strip()))
                            data['Taxa da instituicao financeira'].append(clean_string_BRL(
                                soup.find_all("span", {'class': 'td-protocolo-info--valor'})[4].get_text().strip()))
                            data['Taxa da B3'].append(clean_string_BRL(
                                soup.find_all("span", {'class': 'td-protocolo-info--valor'})[5].get_text().strip()))
                            data['Valor bruto'].append(clean_string_BRL(
                                soup.find_all("span", {'class': 'td-protocolo-info--valor'})[6].get_text().strip()))
                        else:
                            print(f'{YELLOW}{n_protocol}: This operation is already registered.')
                else:
                    # if no records are found in the operations category.
                    print(f'{BLUE.format(key_operations.upper())}: No operations found.')
            else:
                # If the server does not return the page that contains the list of records for the category.
                print(f'{RED} Error requesting operations')

        # Creating and saving a file that stores all logs of operations found.
        # df_td = pd.DataFrame(data)
        df_new = pd.DataFrame(data)
        df_saved = pd.concat([df_saved, df_new])
        df_saved.to_csv(path, sep='\t', index=False)
        print(f'{GREEN} Updated file.')
        # Close webdriver
        self.close_driver()
