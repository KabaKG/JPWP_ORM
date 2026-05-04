#przykład adnotacji
class Column:
    def __init__(self, name: str, primary_key: bool = False):
        self.name = name
        self.primary_key = primary_key

class User:
    id = Column(name="user_id", primary_key=True)
    username = Column(name="login")
    email = Column(name="email_addr")

print(f"Pole 'id' mapuje się na kolumnę: {User.id.name}")

print(f"----------------------------------------")
#przykład refleksji
def inspect_object(obj):
    print(f"Analizuję obiekt klasy: {obj.__class__.__name__}")

    for attr_name, value in obj.__dict__.items():
        column_def = getattr(obj.__class__, attr_name, None)

        if isinstance(column_def, Column):
            print(f" -> Atrybut '{attr_name}' (Kolumna: {column_def.name}) ma wartość: {value}")
u = User()
u.username = "admin"
u.email = "admin@example.com"

inspect_object(u)
print(f"----------------------------------------")
#przykład proxy - lazy loadind
class LazyProxy:
    def __init__(self, cls, object_id):
        self._cls = cls
        self._object_id = object_id
        self._wrapped = None

    def _load(self):
        if self._wrapped is None:
            print(f"--- [PROXY]: Pobieram dane dla {self._cls.__name__} ID:{self._object_id} z bazy... ---")
            real_obj = self._cls()
            real_obj.username = "LazyAdmin"
            self._wrapped = real_obj
        return self._wrapped

    def __getattr__(self, name):
        obj = self._load()
        return getattr(obj, name)

user_proxy = LazyProxy(User, object_id=1)

print("Obiekt proxy utworzony (cisza w logach bazy)...")
print(f"Teraz potrzebuję loginu: {user_proxy.username}")

print(f"----------------------------------------")

# dekorator
def track_changes(cls):
    orig_setattr = cls.__setattr__

    def __setattr__(self, name, value):
        print(f"--- [LOG]: Zmiana pola {name} na {value} ---")
        orig_setattr(self, name, value)

    cls.__setattr__ = __setattr__
    return cls

@track_changes
class User:
    pass

u = User()
u.name = "Admin"

