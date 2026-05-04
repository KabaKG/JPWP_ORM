class ModelMeta(type):
    def __new__(mcs, name, bases, attrs):
        attrs["__tablename__"] = name.lower() + "s"

        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)

        attrs["__init__"] = __init__
        return super().__new__(mcs, name, bases, attrs)

class User(metaclass=ModelMeta):
    pass

u = User(name="Jan", email="jan@example.pl")
print(f"Tabela: {u.__tablename__}, Użytkownik: {u.name}")

