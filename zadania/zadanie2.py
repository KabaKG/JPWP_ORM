class IntegerField: column_type = "INTEGER"
class StringField: column_type = "TEXT"

class Model:
    _fields = {"id": IntegerField(), "imie": StringField()}
    _table_name = "uzytkownik"

    @classmethod
    def get_create_sql(cls):


        # ZADANIE: Wygeneruj string "CREATE TABLE nazwa (kolumna TYP, kolumna TYP);"
        # Iteruj po cls._fields.items()
        return ""

# TEST
print(Model.get_create_sql())
# Ma wyjść: CREATE TABLE uzytkownik (id INTEGER, imie TEXT);