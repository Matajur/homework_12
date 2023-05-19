import pickle
import re
from collections import UserDict
from datetime import datetime
from copy import deepcopy


class Field:
    def __init__(self, value: str) -> None:
        self.value = value


class Name(Field):
    def __init__(self, name: str) -> None:
        super().__init__(name)

    def __repr__(self) -> str:
        return f"Name: {self.value}"


class Phone(Field):
    def __init__(self, phone: str) -> None:
        super().__init__(phone)
        self.__phone = None
        self.value = phone

    def __repr__(self) -> str:
        return f"Phones: {self.value}"

    @property
    def value(self):
        return self.__phone

    @value.setter
    def value(self, phone):
        normalized_phone = (
            phone.strip()
            .replace("+", "")
            .replace("-", "")
            .replace(" ", "")
            .replace(")", "")
            .replace("(", "")
        )
        if len(normalized_phone) == 12:
            if normalized_phone.isdigit():
                self.__phone = normalized_phone
            else:
                raise ValueError('Wrong phone format')
        else:
            raise ValueError('Wrong phone format')


class Birthday(Field):
    def __init__(self, birthday: str) -> None:
        super().__init__(birthday)
        self.__birthday = None
        self.value = birthday

    def __repr__(self) -> str:
        return f"Birthday: {self.value}"

    @property
    def value(self):
        return self.__birthday

    @value.setter
    def value(self, birthday):
        norm_birthday = (
            birthday.strip()
            .replace(" ", "-")
            .replace("/", "-")
            .replace(".", "-")
        )
        try:
            self.__birthday = datetime.strptime(
                norm_birthday, '%d-%m-%Y').date()
        except:
            try:
                self.__birthday = datetime.strptime(
                    norm_birthday, '%Y-%m-%d').date()
            except:
                raise ValueError('Wrond date format')


class Record:
    def __init__(self, name: Name, phone: Phone | str | None = None):
        self.name = name
        self.phones = []
        self.birthday = None
        if phone is not None:
            self.add_phone(phone)

    def add_phone(self, phone: Phone | str):
        if isinstance(phone, str):
            phone = self.create_phone(phone)
        self.phones.append(phone)

    def create_phone(self, phone: str):
        return Phone(phone)

    def edit_phone(self, old_phone, new_phone):
        for p in self.phones:
            if p.value == old_phone:
                p.value = new_phone
                return p
        return None

    def show(self):
        result = 'Phones:'
        for inx, p in enumerate(self.phones):
            result += f' {inx+1}: {p.value}'
        return result

    def remove_phones(self):
        self.phones.clear()

    def add_birthday(self, birthday: Birthday):
        self.birthday = birthday

    def days_to_birthday(self):
        today = datetime.now().date()
        birthdate = self.birthday.value.replace(year=today.year)
        delta = birthdate - today
        if delta.days >= 0:
            return delta.days
        else:
            birthdate.replace(year=today.year+1)
            delta = birthdate - today
            return delta.days

    def get_phone(self, inx):
        if len(self.phones) >= inx + 1:
            return self.phones[inx]

    def get_name(self):
        return self.name.value

    def __str__(self) -> str:
        return f'Contact {self.name}, {self.show() if self.phones else "No phones"}, {self.birthday if self.birthday else "No birthday"}'

    def __repr__(self) -> str:
        return f"Record({self.name!r}: {self.phones!r})"


class AddressBook(UserDict):

    def __init__(self, record: Record | None = None) -> None:
        self.records = {}
        if record is not None:
            self.add_record(record)

    def add_record(self, record: Record):
        self.records[record.get_name()] = record

    def show(self):
        for name, record in self.records.items():
            print(f'{name}:')
            print(record.show())

    def get_records(self, name: str) -> Record:
        return self.records[name]

    def iterator(self, N):
        counter = 0
        result = f'Printing {N} records'
        for item, record in self.records.items():
            result += f'\n{str(record)}'
            counter += 1
            if counter >= N:
                yield result
                counter = 0
                result = f'Printing next {N} records'

    def __str__(self) -> str:
        return '\n'.join(str(record) for record in self.records.values())

    def __repr__(self) -> str:
        return str(self)
    
    def __deepcopy__(self, memodict={}):
        copy_ab = AddressBook(self, self.records)
        memodict[id(self)] = copy_ab
        for el in self.records:
            copy_ab.append(deepcopy(el, memodict))
        return copy_ab


address_book = AddressBook()


def copy_class_addressbook(address_book):
    return deepcopy(address_book)


def input_error(func):
    def inner(*args):
        try:
            result = func(*args)
        except TypeError:
            result = 'Missing contact name or phone or date'
        except UnboundLocalError:
            result = 'Unknown command'
        except ValueError:
            result = 'Wrong phone format'
        except KeyError:
            result = f'Name: {args[0]} not in address book'
        return result
    return inner


def unknown_command(command: str) -> str:
    return f'Unknown command "{command}"'


def hello_user(*args) -> str:
    return 'How can I help you?'


def exit_func(*args) -> str:
    a = input('Would you like to save changes (Y/N)? ')
    if a == 'Y' or a == 'y':
        print(saver())
    return 'Goodbye!'


@input_error
def contact_adder(name: str, phone=None) -> str:
    if name in address_book.records.keys():
        return f'Contact Name: {name} already exists'

    record_name = Name(name)
    record = Record(record_name)

    if phone:
        record_phone = Phone(phone)
        record.add_phone(record_phone)

    address_book.add_record(record)

    return f'Added contact {record.name}, {record.show() if record.phones else "No phones"}'


@input_error
def phone_adder(name: str, phone: str) -> str:
    record = address_book.records[name]

    for ph in record.phones:
        if ph.value == phone:
            return f'Contact {record.name} has already Phone {phone}'

    record.add_phone(phone)

    return f'Contact {record.name} has new Phone: {phone}'


@input_error
def birthday_adder(name: str, birthday: str) -> str:
    record = address_book.records[name]

    if record.birthday:
        return f'Contact {record.name} already has {record.birthday}'
    else:
        record_birthday = Birthday(birthday)
        record.add_birthday(record_birthday)
        return f'Contact {record.name}, {record.birthday} is added'


@input_error
def phones_remover(name: str) -> str:
    record = address_book.records[name]
    record.remove_phones()
    return f'{record}'


@input_error
def phone_editor(name: str, old_phone: str) -> str:
    record = address_book.records[name]
    new_phone = input('Enter new phone: ')
    result = record.edit_phone(old_phone, new_phone)
    if result is not None:
        return f'Contact {record.name}, Phone: {old_phone} replaced with {new_phone}'
    else:
        return f'Contact {record.name} has no old Phone: {old_phone}'


@input_error
def birthday_changer(name: str, birthday: str) -> str:
    record = address_book.records[name]

    record_birthday = Birthday(birthday)
    record.add_birthday(record_birthday)
    return f'Contact {record.name}, {record.birthday} is updated'


@input_error
def contact_displayer(name: str) -> str:
    record = address_book.records[name]
    if record.birthday:
        return f'{record}\nDays to birthday - {record.days_to_birthday()}'
    else:
        return f'{record}'


@input_error
def phones_displayer(name: str) -> str:
    record = address_book.records[name]
    return record.show()


@input_error
def show_all() -> str:
    if address_book.records:
        N = int(input('How many contacts to show? '))
        if N < 1:
            return 'Input cannot be less that 1'
        elif N >= len(address_book.records):
            result = 'Printting all records:'
            for key, value in address_book.records.items():
                result += f'\n{value}'
            result += '\nEnd of address book'
            return result
        else:
            iter = address_book.iterator(N)
            for i in iter:
                print(i)
                input('Press any key to continue: ')
            if len(address_book.records) % 2 == 0:
                return 'End of address book'
            else:
                return f'{str(list(address_book.records.values())[-1])}\nEnd of address book'
    else:
        return 'No contacts, please add'
    
    
@input_error
def saver() -> str:
    if address_book.records:
        with open('backup.dat', 'wb') as file:
            pickle.dump(address_book, file)
        return 'Address Book successfully saved to backup.dat'
    else:
        return 'Address Book is empty'


@input_error
def loader() -> str:
    try:
        with open('backup.dat', 'rb') as file:
            global address_book
            address_book = pickle.load(file)
        return 'Address Book successfully loaded from backup.dat'
    except:
        return 'There are no contacts saved'
    
    
@input_error
def finder(value: str) -> str:
    result = 'Showing all matches'
    for item in address_book.records.values():
        finding = re.findall(value.lower(), str(item).lower())
        if finding:
            result += f'\n{item}'
    if result == 'Showing all matches':
        return 'No matches'
    return result


commands = {
    'hello': hello_user,
    'add contact': contact_adder,
    '+c': contact_adder,
    'add phone': phone_adder,
    '+p': phone_adder,
    'edit phone': phone_editor,
    'remove phones': phones_remover,
    'show all': show_all,
    'show contact': contact_displayer,
    'show phones': phones_displayer,
    '?c': contact_displayer,
    'exit': exit_func,
    'goodbye': exit_func,
    'good bye': exit_func,
    'close': exit_func,
    'add birthday': birthday_adder,
    '+b': birthday_adder,
    'change birthday': birthday_changer,
    'save': saver,
    'load': loader,
    'find': finder
}


def main():
    print(loader())
    while True:
        phrase = input('Please enter request: ').strip()
        command = None
        for key in commands:
            if phrase.lower().startswith(key):
                command = key
                break

        if not command:
            result = unknown_command(phrase.split(' ', 1)[0])
        else:
            data = phrase[len(command):].strip()
            if data:
                if ',' in data:
                    data = data.split(',', 1)
                else:
                    data = data.rsplit(' ', 1)

            handler = commands.get(command)
            result = handler(*data)
            if result == 'Goodbye!':
                print(result)
                break
        print(result)


if __name__ == '__main__':
    main()
