import sqlite3


class Field:
    def __init__(self, column_type):
        self.column_type = column_type
        self.name = None


class IntegerField(Field):
    def __init__(self): super().__init__("INTEGER")


class StringField(Field):
    def __init__(self): super().__init__("TEXT")


class ModelMeta(type):
    def __new__(cls, name, bases, attrs):
        if name == "Model": return super().__new__(cls, name, bases, attrs)
        fields = {k: v for k, v in attrs.items() if isinstance(v, Field)}
        for k, v in fields.items(): v.name = k
        attrs["_fields"] = fields
        attrs["_table_name"] = name.lower()
        return super().__new__(cls, name, bases, attrs)


class Model(metaclass=ModelMeta):
    pass


# --- ZADANIE 4: Napisz dekorator table_sync ---
def table_sync(connection):
    """
    Dekorator ma przyjąć połączenie do bazy, a następnie:
    1. Pobrać pola z klasy modelu (cls._fields)
    2. Zbudować zapytanie CREATE TABLE IF NOT EXISTS
    3. Wykonać je na przesłanym połączeniu
    4. Zwrócić klasę bez zmian
    """

    def wrapper(cls):
        # TWOJA LOGIKA TUTAJ:
        # sql = "CREATE TABLE ..."
        # connection.execute(sql)
        return cls

    return wrapper


# --- SKRYPT TESTOWY ---

if __name__ == "__main__":
    conn = sqlite3.connect(":memory:")

    print("--- TEST 1: Rejestracja modelu przez dekorator ---")

    try:
        @table_sync(conn)
        class Faktura(Model):
            id = IntegerField()
            numer = StringField()
            kwota = IntegerField()

        cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='faktura'")
        check = cursor.fetchone()

        if check and check[0] == "faktura":
            print("Status: SUCCESS (Tabela 'faktura' została utworzona przez dekorator!)")
        else:
            print("Status: FAILED (Tabela nie istnieje w bazie danych)")

    except Exception as e:
        print(f"Status: ERROR (Wystąpił błąd w dekoratorze: {e})")

    conn.close()