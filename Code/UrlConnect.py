import requests
import sys
import os

DB_Path = './Database'
TB_Path = './Table'


class Connect:
    def __init__(self, option):
        self.option = option
        if option[0] == '-h':
            self.help()

        self.all_data = {'-u': None, '-c': None, '-m': None, '-d': None, '-p': None, '-db': '', '-tb': ''}
        self.cookie_dict = {}
        self.data_dict = {}

    def help(self):
        print('-------                       OPTIONS                       -------')
        print('-u : URL Setting option')
        print('-c : Cookie & Session Setting option')
        print('-m : HTTP Method Setting option (GET/POST)')
        print('-d : Method Data Setting option')
        print('-p : Method Test Parameter Setting option')
        print('-db : If you already have Databases list, Database Setting option')
        print('-tb : If you already have Tables list, Table Setting option')
        sys.exit(1)

    def parsing(self):
        for i in self.option:
            if i in self.all_data.keys():
                self.all_data[i] = self.option[self.option.index(i) + 1]

        if None in self.all_data.values():
            print('Option Error')
            sys.exit(1)

        if self.all_data['-db'] != '':
            self.db(self.all_data['-db'])
            print('db test')
        if self.all_data['-tb'] != '':
            self.tb(self.all_data['-tb'])
            print('tb test')

    def dict(self, data, emo):
        data_dict = {}
        data = data.split(emo)

        for i in data:
            data_dict.update({i.split('=')[0]: i.split('=')[1]})

        return data_dict

    def db(self, database):
        php = self.all_data['-u'].split('/')
        t_php = php[len(php) - 1].split('.')[0] + '.txt'

        if t_php not in os.listdir(DB_Path):
            print('No Such Database List')
            sys.exit(1)

        fr = open(DB_Path + '/{}'.format(t_php), 'r')

        if database not in fr.read().splitlines():
            print('No Such Database Name')
            sys.exit(1)

        fr.close()

        return database

    def tb(self, table):
        php = self.all_data['-u'].split('/')
        t_php = php[len(php) - 1].split('.')[0]
        t_table = '{}_{}.txt'.format(t_php, self.all_data['-db'])

        if t_table not in os.listdir(TB_Path):
            print('No Such Table List')
            sys.exit(1)

        fr = open(TB_Path + '/{}'.format(t_table), 'r')

        if table not in fr.read().splitlines():
            print('No Such Table Name')
            sys.exit(1)

        fr.close()

        return table

    def url_request(self):
        connect = []
        self.cookie_dict = self.dict(self.all_data['-c'], ';')
        self.data_dict = self.dict(self.all_data['-d'], '&')

        if self.all_data['-m'].lower() == 'get':
            connect = requests.get(self.all_data['-u'], cookies=self.cookie_dict, params=self.data_dict)
        elif self.all_data['-m'].lower() == 'post':
            connect = requests.post(self.all_data['-u'], cookies=self.cookie_dict, data=self.data_dict)

        if self.all_data['-m'].upper() not in str(connect.request):
            print('Your Session Is Wrong')
            sys.exit(1)

        return connect.status_code

    def normal(self):
        connect = requests.get(self.all_data['-u'], cookies=self.cookie_dict)

        return connect.text.splitlines(keepends=True)

    def setting(self):
        self.parsing()
        while True:
            http_connect = self.url_request()
            if http_connect == 200:
                break
            else:
                print("Connection Error")

        return self.normal()

    def parameter(self):

        return self.all_data['-u'], self.cookie_dict, self.all_data['-m'], self.data_dict, self.all_data['-p'], \
            self.all_data['-db'], self.all_data['-tb']
