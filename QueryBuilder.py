class QueryBuilder:

    def __init__(self, x_col="", y_col="", aggregate="", group_by="", having="", sort_by="", where=""):
        self.x_col = x_col
        self.y_col = y_col
        self.aggregate = aggregate
        self.group_by = group_by
        self.having = having
        self.sort_by = sort_by
        self.where = where

    def build_query(self):
        if self.x_col == '' or self.y_col == '':
            return ""

        query = f'SELECT {self.x_col}, '

        if self.aggregate != '':
            query += f"{self.aggregate}({self.y_col}) "
        else:
            query += f"{self.y_col} "

        query += f"FROM data "

        if self.where != '':
            query += f"WHERE {self.where} "

        if self.group_by != '':
            query += f"GROUP BY {self.group_by} "

        if self.having != '':
            query += f"HAVING {self.having} "

        if self.sort_by != '':
            query += f"ORDER BY {self.sort_by}"
        else:
            query += f"ORDER BY {self.x_col}"

        print(query)
        return query
