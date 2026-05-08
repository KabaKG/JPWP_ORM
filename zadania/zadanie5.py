import sqlite3


class Field:
    def __init__(self, column_type):
        self.column_type = column_type
        self.name = None

    def __get__(self, instance, owner):
        if instance is None: return self
        return instance.__dict__.get(self.name)

    def __set__(self, instance, value):
        if self.name in instance.__dict__ and instance.__dict__[self.name] != value:
            instance._dirty_fields.add(self.name)
        instance.__dict__[self.name] = value


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
    def __init__(self, **kwargs):
        self._dirty_fields = set()
        self._is_new = kwargs.pop('_is_new', True)
        for key, value in kwargs.items():
            setattr(self, key, value)
        if not self._is_new:
            self._dirty_fields.clear()

    @classmethod
    def create_table(cls, connection):
        cols = [f"{f.name} {f.column_type}" for f in cls._fields.values()]
        sql = f"CREATE TABLE IF NOT EXISTS {cls._table_name} ({', '.join(cols)});"
        connection.execute(sql)
        connection.commit()

    # --- ZADANIE 5: Napisz metodę save ---
    def save(self, connection):

        # 1. Jeśli self._is_new -> INSERT
        # 2. Jeśli nie -> UPDATE (tylko kolumny w self._dirty_fields)
        # 3. Na końcu: commit, clear dirty_fields, _is_new = False
        pass


# --- SKRYPT TESTOWY ---

if __name__ == "__main__":
    conn = sqlite3.connect(":memory:")


    class Pracownik(Model):
        id = IntegerField()
        imie = StringField()
        pensja = IntegerField()


    Pracownik.create_table(conn)
    print("Log: Tabela utworzona.\n")

    # TEST 1: INSERT
    print("--- TEST 1: INSERT ---")
    p = Pracownik(id=1, imie="Adam", pensja=3000)
    p.save(conn)

    row = conn.execute("SELECT * FROM pracownik").fetchone()
    if row == (1, "Adam", 3000):
        print("Status: SUCCESS (Rekord dodany poprawnie)")
    else:
        print(f"Status: FAILED (Oczekiwano (1, 'Adam', 3000), otrzymano {row})")

    # TEST 2: UPDATE
    print("\n--- TEST 2: UPDATE (Dirty Checking) ---")
    p.pensja = 3500
    p.save(conn)

    row = conn.execute("SELECT * FROM pracownik WHERE id = 1").fetchone()
    if row and row[2] == 3500:
        print("Status: SUCCESS (Pensja zaktualizowana)")
    else:
        print(f"Status: FAILED (Pensja w bazie to nadal {row[2] if row else 'Brak'})")

    # TEST 3: Brak zmian
    print("\n--- TEST 3: Ponowny zapis bez zmian ---")
    try:
        p.save(conn)
        print("Status: SUCCESS (Brak błędów przy pustym UPDATE)")
    except Exception as e:
        print(f"Status: FAILED (Błąd: {e})")

    conn.close()