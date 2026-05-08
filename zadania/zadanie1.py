class Field:
    def __init__(self, column_type):
        self.column_type = column_type
        self.name = None

    def __get__(self, instance, owner):
        if instance is None: return self
        return None

        # ZADANIE:
        # 1. Sprawdź czy to pole typu "INTEGER" i czy wartość jest liczbą (opcjonalnie)
        # 2. Jeśli wartość w __dict__ jest inna niż nowa, dodaj self.name do instance._dirty_fields
        # 3. Zapisz wartość w instance.__dict__[self.name]
        pass

# TEST
class MockInstance:
    def __init__(self):
        self.__dict__ = {}
        self._dirty_fields = set()

f = Field("INTEGER")
f.name = "wiek"
inst = MockInstance()
f.__set__(inst, 25)
print("Wynik:", inst.__dict__.get("wiek")) # Powinno być 25