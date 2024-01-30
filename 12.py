import pickle
from collections import UserDict
from datetime import datetime
import re


class AddressBook(UserDict):
    def __init__(self, file_path="address_book.pkl"):
        super().__init__()
        self.file_path = file_path

    def save_to_disk(self):
        with open(self.file_path, "wb") as file:
            pickle.dump(self.data, file)

    def load_from_disk(self):
        try:
            with open(self.file_path, "rb") as file:
                self.data = pickle.load(file)
        except FileNotFoundError:
            self.data = {}

    def add_record(self, record):
        self.data[record.name.value] = record

    def search_records(self, item):
        result = []

        for name, record in self.data.items():
            if item.lower() in name.lower():
                result.append(name)
                result.append(record)

            elif item.isdigit():
                for phone in record.phones:
                    if item in phone.value.value:
                        result.append(record)
                        result.append(name)
                    else:
                        wzor = "[" + re.escape(item) + r"]+"
                        wynik = re.search(wzor, phone.value.value)
                        result.append(wynik)
            else:
                item = item.lower()
                wzor = "[" + re.escape(item) + r"]+"
                wynik = re.search(wzor, name)
                result.append(wynik)

        print(f"Result for", item)
        return result

    def iterator(self, N):
        records = list(self.data.values())
        for i in range(0, len(records), N):
            yield records[i : i + N]

    def __repr__(self):
        return f"{repr(self.data)}"


class Field:
    def __init__(self, value):
        self._value = value

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, new_value):
        self._value = new_value

    def __repr__(self):
        return f"{repr(self.value)}"


class Name(Field):
    pass


class Phone(Field):
    @Field.value.setter
    def value(self, new_value):
        if isinstance(new_value, str) and len(new_value) > 0:
            self._value = new_value
        else:
            print("Invalid phone number:", new_value)


class Birthday(Field):
    @Field.value.setter
    def value(self, new_value):
        if isinstance(new_value, datetime):
            self._value = new_value
        else:
            print(f"Invalid birthday format for value:", new_value)


class Record:
    def __init__(self, name, phone=None, birthday=None):
        self.name = name
        self.phones = [Phone(phone)] if phone else []
        self.birthday = Birthday(birthday) if birthday else None

    def days_to_birthday(self):
        if not self.birthday:
            return None

        today = datetime.now()

        next_birthday = self.birthday.value.replace(year=today.year)

        if next_birthday < today:
            next_birthday = next_birthday.replace(year=today.year + 1)

        days_until_birthday = (next_birthday - today).days
        return days_until_birthday

    def add_phone(self, phone):
        self.phones.append(Phone(phone))

    def remove_phone(self, phone):
        new_phones = []
        for p in self.phones:
            if p.value != phone:
                new_phones.append(p)
        self.phones = new_phones

    def edit_phone(self, old_phone, new_phone):
        for phone in self.phones:
            if phone.value == old_phone:
                phone.value = new_phone

    def __repr__(self):
        return f"{repr(self.phones)}"


if __name__ == "__main__":
    address_book = AddressBook()

    address_book.load_from_disk()

    while True:
        print("1. Dodaj nowy kontakt")
        print("2. Wyszukaj kontakty")
        print("3. Wyjście i zapis danych")

        choice = input("Wybierz opcję: ")

        if choice == "1":
            name = input("Podaj imię i nazwisko: ")
            phone = input("Podaj numer telefonu: ")
            date_pattern = re.compile(r"^\d{4}-\d{2}-\d{2}$")

            while True:
                birthday_str = input("Podaj datę urodzenia (RRRR-MM-DD): ")
                if date_pattern.match(birthday_str):
                    birthday = datetime.strptime(birthday_str, "%Y-%m-%d")
                    record1 = Record(Name(name), Phone(phone), Birthday(birthday_str))
                    address_book.add_record(record1)
                    break

                else:
                    print("Błędny format daty. Spróbuj ponownie.")

        elif choice == "2":
            search_term = input("Wpisz imię, nazwisko lub numer telefonu: ")
            results = address_book.search_records(search_term)

            if results:
                print("Znalezione kontakty:")

                print(results)
            else:
                print("Brak wyników dla:", search_term)

        elif choice == "3":
            address_book.save_to_disk()
            break

        else:
            print("Nieprawidłowy wybór. Wybierz ponownie.")
