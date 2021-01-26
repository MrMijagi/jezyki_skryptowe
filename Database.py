import sqlite3
import pandas as pd


def default(dataset, type):
    if type == 'text':
        return 'null'
    elif type == 'integer':
        return '0'
    elif type == 'real':
        return '0.0'


def load_preview_of_file(filename, row_count):
    with open(filename) as f:
        for i in range(row_count):
            yield f.readline()


class Database:
    def __init__(self, db_name):
        self.__db_name = db_name
        self.__columns = {}
        self.__connection = sqlite3.connect(':memory:')

    def close(self):
        self.__connection.close()

    def create_database(self):
        headers = self.__columns.keys()
        types = self.__columns.values()

        params = [self.__db_name]
        for header, typ in zip(headers, types):
            params.append(header + ' ' + typ)

        cursor = self.__connection.cursor()
        sql = "CREATE TABLE " + self.__db_name + " ("
        for header, typ in zip(headers, types):
            sql += header + ' ' + typ + ','

        sql = sql[:-1] + ')'
        cursor.execute(sql)

        self.__connection.commit()
        cursor.close()

    def get_query(self, query):
        cursor = self.__connection.cursor()
        for row in cursor.execute(query):
            yield row

        cursor.close()

    def get_columns(self):
        return self.__columns.keys()

    def load_to_db(self, filename, is_header, delimiter, types):
        cursor = self.__connection.cursor()

        with open(filename) as f:
            line = f.readline()
            if not line:
                return -1

            headers = []
            if is_header:
                headers = line.rstrip().split(delimiter)
                headers = [''.join(c for c in header if c not in " -=[]{};',./") for header in headers]
                line = f.readline()
                for header in headers:
                    self.__columns[header] = types.pop(0)
            else:
                count = len(line.rstrip().split(delimiter))
                for i in range(count):
                    self.__columns['X' + str(i+1)] = types.pop(0)
                    headers.append('X' + str(i+1))

            self.create_database()
            old_line_split = ['null'] * len(headers)

            while line:
                line_split = line.strip('\n').split(delimiter)

                for i in range(len(line_split)):
                    if line_split[i] != '':
                        old_line_split[i] = line_split[i]

                # fix splitted values in ""
                fixed_line = []
                found = False
                tmp = ''
                for val, old_val in zip(line_split, old_line_split):
                    if val == '':              # need to fill it
                        fixed_line.append(old_val)
                    elif val.find('"') != -1:
                        tmp += val
                        if found:
                            found = False
                            fixed_line.append(tmp)
                            tmp = ''
                        else:
                            found = True
                    else:
                        if found:
                            tmp += val
                        else:
                            fixed_line.append(val)

                line_split = fixed_line

                count = len(line_split)
                for i in range(len(headers)):
                    if self.__columns[headers[i]] == 'integer':
                        try:
                            line_split[i] = int(line_split[i])
                        except ValueError:
                            line_split[i] = 0
                    elif self.__columns[headers[i]] == 'real':
                        try:
                            line_split[i] = float(line_split[i])
                        except ValueError:
                            line_split[i] = 0.0

                cursor.execute("INSERT INTO " + self.__db_name + " VALUES (" + '?,' * (count - 1) + "?)", line_split)
                line = f.readline()

        self.__connection.commit()
        cursor.close()

        return 0

    def delete_database(self):
        cursor = self.__connection.cursor()

        cursor.execute("DROP TABLE IF EXISTS " + self.__db_name + ";")

        self.__connection.commit()
        cursor.close()

        self.__columns = {}
