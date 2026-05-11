import sqlite3
import os
import time
from functools import wraps


## Dekoratory

def log_sql(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        print(f"\n[ORM] Wywołanie metody: {func.__name__}")
        result = func(*args, **kwargs)
        print(f"[ORM] Zakończono metodę: {func.__name__}")
        return result
    return wrapper

def measure_time(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print(f"[TIME] {func.__name__}: {(end - start):.6f}s")
        return result
    return wrapper

def lazy_property(func):
    attr_name = "_lazy_" + func.__name__
    @property
    @wraps(func)
    def wrapper(self):
        if not hasattr(self, attr_name):
            print(f"[LAZY LOADING] Ładowanie danych: {func.__name__}")
            setattr(self, attr_name, func(self))
        return getattr(self, attr_name)
    return wrapper

class Field:
    def __init__(self, column_type, primary_key=False):
        self.column_type = column_type
        self.primary_key = primary_key
        self.name = None
    def __get__(self, instance, owner):
        if instance is None: return self
        return instance.__dict__.get(self.name)
    def __set__(self, instance, value):
        if self.name in instance.__dict__ and instance.__dict__[self.name] != value:
            instance._dirty_fields.add(self.name)
        instance.__dict__[self.name] = value

class StringField(Field):
    def __init__(self, primary_key=False):
        super().__init__("TEXT", primary_key)

class IntegerField(Field):
    def __init__(self, primary_key=False):
        super().__init__("INTEGER", primary_key)
    def __set__(self, instance, value):
        if not isinstance(value, int):
            raise TypeError(f"Pole '{self.name}' oczekuje typu int.")
        super().__set__(instance, value)

class ModelMeta(type):
    def __new__(cls, name, bases, attrs):
        if name == "Model": return super().__new__(cls, name, bases, attrs)
        fields = {k: v for k, v in attrs.items() if isinstance(v, Field)}
        for field_name, field_obj in fields.items():
            field_obj.name = field_name
        attrs["_fields"] = fields
        attrs["_table_name"] = name.lower()
        return super().__new__(cls, name, bases, attrs)

class Model(metaclass=ModelMeta):
    def __init__(self, **kwargs):
        self._dirty_fields = set()
        self._is_new = kwargs.pop("_is_new", True)
        self._connection = kwargs.pop("_connection", None)
        for key, value in kwargs.items():
            setattr(self, key, value)
        if not self._is_new: self._dirty_fields.clear()
    def __repr__(self):
        fields_str = ", ".join([f"{k}={getattr(self, k)}" for k in self._fields])
        status = " [NOWY]" if self._is_new else (" [ZMIENIONY]" if self._dirty_fields else "")
        return f"<{self.__class__.__name__}({fields_str}){status}>"
    @classmethod
    @log_sql
    def create_table(cls, connection):
        columns = [f"{f.name} {f.column_type}{' PRIMARY KEY' if f.primary_key else ''}" for f in cls._fields.values()]
        sql = f"CREATE TABLE IF NOT EXISTS {cls._table_name} ({', '.join(columns)});"
        connection.execute(sql)
        connection.commit()
    @classmethod
    @log_sql
    def get(cls, connection, obj_id):
        sql = f"SELECT * FROM {cls._table_name} WHERE id=?"
        row = connection.execute(sql, (obj_id,)).fetchone()
        if not row: return None
        data = {field_name: row[i] for i, field_name in enumerate(cls._fields)}
        return cls(**data, _is_new=False, _connection=connection)
    @log_sql
    @measure_time
    def save(self, connection):
        if not self._dirty_fields and not self._is_new: return
        columns = list(self._fields.keys())
        if self._is_new:
            values = [getattr(self, col) for col in columns]
            sql = f"INSERT INTO {self._table_name} ({', '.join(columns)}) VALUES ({', '.join(['?' for _ in values])})"
            connection.execute(sql, values)
        else:
            dirty_columns = list(self._dirty_fields)
            values = [getattr(self, col) for col in dirty_columns] + [self.id]
            sql = f"UPDATE {self._table_name} SET {', '.join([f'{c}=?' for c in dirty_columns])} WHERE id=?"
            connection.execute(sql, values)
        connection.commit()
        self._dirty_fields.clear()
        self._is_new = False

    @log_sql
    def delete(self, connection):
        if self._is_new:
            print("[ORM] Nie można usunąć obiektu, który nie istnieje w bazie.")
            return
        sql = f"DELETE FROM {self._table_name} WHERE id=?"
        connection.execute(sql, (self.id,))
        connection.commit()
        self._is_new = True
        print(f"[ORM] Usunięto obiekt o ID {self.id} z tabeli {self._table_name}")

    @classmethod
    @log_sql
    def all(cls, connection):
        rows = connection.execute(f"SELECT * FROM {cls._table_name}").fetchall()
        return [cls(**{field: row[i] for i, field in enumerate(cls._fields)}, _is_new=False, _connection=connection) for
                row in rows]


class Kategoria(Model):
    id = IntegerField(primary_key=True)
    nazwa = StringField()

class Produkt(Model):
    id = IntegerField(primary_key=True)
    nazwa = StringField()
    cena = IntegerField()
    kategoria_id = IntegerField()
    @lazy_property
    def kategoria(self):
        row = self._connection.execute("SELECT * FROM kategoria WHERE id=?", (self.kategoria_id,)).fetchone()
        return Kategoria(id=row[0], nazwa=row[1], _is_new=False, _connection=self._connection) if row else None

def main():
    db_file = "magazyn.db"
    with sqlite3.connect(db_file) as conn:
        Kategoria.create_table(conn)
        Produkt.create_table(conn)
        while True:
            try:
                print("\n##################### MAGAZYN #####################")
                print("\n1. Kat, 2. Prod, 3. Lista, 4. Cena, 5. Lazy, 6. usuń, 7.exit")
                choice = input("Wybór: ").strip()
                if choice == "1":
                    Kategoria(id=int(input("ID: ")), nazwa=input("Nazwa: ")).save(conn)
                elif choice == "2":
                    Produkt(id=int(input("ID: ")), nazwa=input("Nazwa: "), cena=int(input("Cena: ")), kategoria_id=int(input("Kat ID: ")), _connection=conn).save(conn)
                elif choice == "3":
                    produkty = Produkt.all(conn)
                    for p in produkty:
                        print(p)
                elif choice == "4":
                    p = Produkt.get(conn, int(input("ID: ")))
                    if p:
                        p.cena = int(input("Nowa cena: "))
                        p.save(conn)
                elif choice == "5":
                    p = Produkt.get(conn, int(input("ID: ")))
                    if p: print(f"Kat: {p.kategoria.nazwa}")
                elif choice == "6":
                    p_id = int(input("Podaj ID produktu do usunięcia: "))
                    p = Produkt.get(conn, p_id)
                    if p:
                        p.delete(conn)
                    else:
                        print("Nie znaleziono takiego produktu.")
                elif choice == "7": break
            except Exception as e: print(f"Błąd: {e}")
    if os.path.exists(db_file): os.remove(db_file)

if __name__ == "__main__":
    main()