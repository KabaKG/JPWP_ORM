class Model:
    _table_name = "produkty"

    @classmethod
    def filter_sql(cls, **kwargs):
        # ZADANIE: Na podstawie kwargs zbuduj zapytanie SQL.
        # Przykład: filter_sql(kat="AGD", cena=100)
        # Ma zwrócić: ("SELECT * FROM produkty WHERE kat = ? AND cena = ?", ["AGD", 100])

        return ""


# TEST
sql, vals = Model.filter_sql(status="aktywny", priorytet=1)
print(sql)  # powinno być: SELECT * FROM produkty WHERE status = ? AND priorytet = ?