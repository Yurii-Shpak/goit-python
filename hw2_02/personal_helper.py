from abc import abstractmethod, ABC
from collections import UserDict, defaultdict
from datetime import datetime, timedelta
import os.path
import pickle
import re
import clean

# --------------------------------Prompt Toolkit-------------------------------
from prompt_toolkit import prompt
from prompt_toolkit.history import FileHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.lexers import PygmentsLexer
from prompt_toolkit.styles import Style

SqlCompleter = WordCompleter([
    'add', 'close', 'exit', 'save', 'remove', 'add address', 'add birthday', 'add email', 'add phone',
    'delete address', 'delete birthday', 'delete email', 'delete phone',
    'change email', 'change birthday', 'change address', 'change phone',
    'coming birthday', 'good bye', "add note", "find note", "change note",
    "delete note", "tag note", "help", 'show all', 'search', 'clean'], ignore_case=True)

style = Style.from_dict({
    'completion-menu.completion': 'bg:#008888 #ffffff',
    'completion-menu.completion.current': 'bg:#00aaaa #000000',
    'scrollbar.background': 'bg:#88aaaa',
    'scrollbar.button': 'bg:#222222',
})
# --------------------------------Prompt Toolkit-------------------------------


class OutputTo(ABC):

    @abstractmethod
    def output_record(self, record):
        pass

    @abstractmethod
    def output_note(self, record):
        pass

    @abstractmethod
    def output_help(self, content):
        pass


class OutputToTerminal(OutputTo):

    def output_record(self, record):
        name = record.name
        email = '---' if record.email == None else record.email
        address = '---' if record.address == None else record.address
        birthday = '---' if record.birthday == None else record.birthday
        if len(record.phones_list) == 0:
            phones = '---'
        else:
            phones = ', '.join(record.phones_list)
        return f'\nā{"-" * 108}ā\n| {name:<51} Phones: {phones:<46} |\
                 \n| Email: {email:<73} Date of birth: {birthday:<10} |\
                 \n| Address: {address:<97} |\nā{"-" * 108}ā\n'

    def output_note(self, note):
        return f'ā{"-" * 108}ā\n| {note[:note.find("::")-1]} | {note[note.find("::")+3 : len(note)-1]:<82} |\nā{"-" * 108}ā'

    def output_help(self, content):
        for i in content:
            # Š·Š°Š±ŠøŠ»Šø ŠæŠ¾ŃŠ»ŠµŠ“Š½ŠøŠ¹ ŃŠøŠ¼Š²Š¾Š» ŠæŠµŃŠµŠ½Š¾ŃŠ° ŃŃŃŠ¾ŠŗŠø - Š“Š»Ń ŠŗŃŠ°ŃŠøŠ²Š¾Š³Š¾ Š²ŃŠ²Š¾Š“Š°
            print(i[:len(i)-1])


class CustomException(Exception):
    def __init__(self, text):
        self.txt = text


class AddressBook(UserDict):

    def get_values_list(self):
        if self.data:
            return self.data.values()
        else:
            raise CustomException('Address book is empty.')

    def get_record(self, name):
        if self.data.get(name):
            return self.data.get(name)
        else:
            raise CustomException(
                'Such contacts doesn\'t exist.')

    def remove(self, name):
        if self.data.get(name):
            self.data.pop(name)
        else:
            raise CustomException(
                'Such contact  doesn\'t exist.')

    def load_from_file(self, file_name):
        if os.path.exists(file_name):
            with open(file_name, 'rb') as fh:
                self.data = pickle.load(fh)
                if len(self.data):
                    return f'The contacts book is loaded from the file "{file_name}".'
                else:
                    return "This is empty contacts book. Add contacts to it using the command 'add < NAME > '."
        else:
            return "This is empty contacts book. Add contacts into it using the command 'add <NAME>'."

    def save_to_file(self, file_name):
        with open(file_name, 'wb') as fh:
            pickle.dump(self.data, fh)
        return f'The contacts book is saved in the file "{file_name}".'

    def search(self, query):
        result = AddressBook()
        for key in self.data.keys():
            if query.lower() in str(self.get_record(key)).lower():
                match = self.get_record(key)
                result[key] = match
        if len(result) > 0:
            return f'{len(result)} records found:\n {result}'
        else:
            return f'No records found.'

    def __repr__(self):
        result = ""
        for key in self.data.keys():
            result += str(self.data.get(key))
        return result


contacts = AddressBook()


class Record:

    def __init__(self, name, address=None, phones_list=None, email=None, birthday=None):
        self.name = name
        self._address = address
        self._phones_list = []
        self._email = email
        self._birthday = birthday

    def append_phone(self, phone):
        if re.search('\(0\d{2}\)\d{3}-\d{2}-\d{2}', phone):
            self._phones_list.append(phone)
        else:
            raise CustomException(
                'Wrong phone number format! Use (0XX)XXX-XX-XX format!')

    @property
    def address(self):
        return self._address

    @address.setter
    def address(self, address):
        self._address = address

    def delete_address(self):
        self._address = None

    @property
    def phones_list(self):
        return self._phones_list

    @property
    def email(self):
        return self._email

    @email.setter
    def email(self, email):
        if re.search('[a-zA-Z][\w.]+@[a-zA-z]+\.[a-zA-Z]{2,}', email):
            self._email = email
        else:
            raise CustomException(
                'Wrong email format! Correct format is aaaa@ddd.cc')

    def delete_email(self):
        self._email = None

    @property
    def birthday(self):
        return self._birthday

    @birthday.setter
    def birthday(self, birthday):
        if re.search('\d{2}\.\d{2}.\d{4}', birthday) and datetime.strptime(birthday, '%d.%m.%Y'):
            self._birthday = birthday
        else:
            raise CustomException(
                'Wrong date format! Correct format is DD.MM.YYYY')

    def delete_birthday(self):
        self._birthday = None

    def __repr__(self):
        return OutputToTerminal().output_record(self)


def input_error(func):

    def inner(command_line):

        try:
            result = func(command_line)

        except CustomException as warning_text:
            result = warning_text

        except Exception as exc:

            if func.__name__ == 'save_func':
                result = f'Error while saving.'
            elif func.__name__ == 'add_birthday':
                result = "Day out of range for this month."
            elif func.__name__ == 'coming_birthday' and exc.__class__.__name__ == "ValueError":
                result = "Use a number for getting list of birthdays more than next 7 days."
            elif func.__name__ == 'remove':
                result = f'Error while removing record.'
            elif func.__name__ == 'change_address':
                result = f'Error while changing address.'
            elif func.__name__ == 'change_birthday':
                result = f'Error while changing birthday.'
            elif func.__name__ == 'change_email':
                result = f'Error while changing email.'
            elif func.__name__ == 'change_phone':
                result = f'Error while changing phone.'
            elif func.__name__ == 'delete_address':
                result = f'Error while deleting address.'
            elif func.__name__ == 'delete_birthday':
                result = f'Error while deleting birthday.'
            elif func.__name__ == 'delete_email':
                result = f'Error while deleting email.'
            elif func.__name__ == 'delete_phone':
                result = f'Error while deleting phone.'
            elif func.__name__ == 'search':
                result = f'Error while searching.'
            elif func.__name__ == 'clean_func':
                result = f'Error while cleaning the folder.'

        return result

    return inner


@input_error
def exit_func(command_line):

    return 'Good bye!'


@input_error
def save_func(command_line):

    return contacts.save_to_file('contacts.bin')


def prepare_value(command_line):
    if command_line:
        value = command_line.pop(-1)
        key = ' '.join(command_line)
        return key, value
    else:
        raise CustomException(
            'The command must be with INFORMATION you want to add or change (Format: <command> <name> <information>).')


def prepare_value_3(command_line):
    if command_line:
        key = ' '.join(command_line)
        value = input('Enter the address >>> ')
        return key, value
    else:
        raise CustomException(
            'The command must be in the format: <command> <name>.')


@input_error
def add_name(command_line):
    if command_line:
        name = ' '.join(command_line)
        if name in contacts.keys():
            raise CustomException(
                f'Contact with name "{name}" has been already added!')
        else:
            record = Record(name)
            contacts[name] = record
            return f'Contact with the name "{name}" has been successfully added.'
    else:
        raise CustomException(
            'The command must be with a NAME you want to add (Format: <add> <name>).')


@input_error
def add_address(command_line):
    key, address = prepare_value_3(command_line)
    contacts.get_record(key).address = address
    return f'Address {address} for the contact "{key}" has been successfully added.'


@input_error
def add_birthday(command_line):
    key, birthday = prepare_value(command_line)
    contacts.get_record(key).birthday = birthday
    return f'Date of birth {birthday} for the contact "{key}" has been successfully added.'


@input_error
def add_email(command_line):
    key, email = prepare_value(command_line)
    contacts.get_record(key).email = email
    return f'Email {email} for the contact "{key}" has been successfully added.'


@input_error
def add_phone(command_line):
    key, phone = prepare_value(command_line)
    if not phone in contacts.get_record(key).phones_list:
        contacts.get_record(key).append_phone(phone)
        return f'Phone number {phone} for the contact "{key}" has been successfully added.'
    else:
        raise CustomException('Such phone number has been already added!')


def create_for_print(birthdays_dict):
    to_show = []
    for date, names in list(birthdays_dict.items()):
        to_show.append(
            f'{date.strftime("%A")}({date.strftime("%d.%m.%Y")}): {", ".join(names)}')
    if len(to_show) == 0:
        return f'There are no birthdays coming within this period.'
    else:
        return "\n".join(to_show)


@input_error
# Š¼Š¾Š¶Š½Š¾ Š·Š°Š“Š°ŃŃ Š“ŃŃŠ³Š¾Š¹ Š“ŠøŠ°ŠæŠ°Š·Š¾Š½ Š²ŃŠ²Š¾Š“Š° Š“Š½ŠµŠ¹, ŠæŠ¾ ŃŠ¼Š¾Š»ŃŠ°Š½ŠøŃ 7
def coming_birthday(command_line):
    range_days = 7
    birthdays_dict = defaultdict(list)
    if command_line:
        range_days = int(command_line[0])
    current_date = datetime.now().date()
    timedelta_filter = timedelta(days=range_days)
    for name, birthday in [(i.name, i.birthday) for i in contacts.get_values_list()]:
        if name and birthday:  # ŠæŃŠ¾Š²ŠµŃŠŗŠ° Š½Š° None
            birthday_date = datetime.strptime(birthday, '%d.%m.%Y').date()
            current_birthday = birthday_date.replace(year=current_date.year)
            if current_date <= current_birthday <= current_date + timedelta_filter:
                birthdays_dict[current_birthday].append(name)
    return create_for_print(birthdays_dict)


@input_error
def search(command_line):
    if command_line:
        return contacts.search(' '.join(command_line).strip())
    else:
        return 'Specify the search string.'


@input_error
def remove(command_line):
    key = ' '.join(command_line).strip()
    if contacts.get_record(key):
        contacts.remove(key)
        return f'Contact "{key}" has been successfully removed.'
    else:
        raise CustomException('Such contact does not exist!!!')


@input_error
def delete_address(command_line):
    key = ' '.join(command_line).strip()
    if key in contacts.keys():
        address = contacts.get_record(key).address
        contacts.get_record(key).delete_address()
        return f'Address "{address}" for the contact "{key}" has been successfully deleted.'
    else:
        raise CustomException('Such contact does not exist!!!')


@input_error
def delete_birthday(command_line):
    key = ' '.join(command_line).strip()
    if key in contacts.keys():
        birthday = contacts.get_record(key).birthday
        contacts.get_record(key).delete_birthday()
        return f'Date of birth {birthday} for the contact "{key}" has been successfully deleted.'
    else:
        raise CustomException('Such contact does not exist!!!')


@input_error
def delete_email(command_line):
    key = ' '.join(command_line).strip()
    if key in contacts.keys():
        email = contacts.get_record(key).email
        contacts.get_record(key).delete_email()
        return f'Email {email} for the contact "{key}" has been successfully deleted.'
    else:
        raise CustomException('Such contact does not exist!!!')


@input_error
def delete_phone(command_line):
    key, phone = prepare_value(command_line)
    if phone in contacts.get_record(key).phones_list:
        ix = contacts.get_record(key).phones_list.index(phone)
        if ix >= 0:
            contacts.get_record(key).phones_list.pop(ix)
        return f'Phone number {phone} for the contact "{key}" has been successfully deleted.'
    else:
        raise CustomException('Such phone number does not exist!!!')


@input_error
def change_email(command_line):
    key, email = prepare_value(command_line)
    if key in contacts.keys():
        contacts.get_record(key).email = email
        return f'Email for "{key}" has been successfully changed to {email}.'
    else:
        raise CustomException(
            f'Contact "{key}" does not exist or you have not specified new email!!!')


@input_error
def change_birthday(command_line):
    key, birthday = prepare_value(command_line)
    if key in contacts.keys():
        contacts.get_record(key).birthday = birthday
        return f'Date of birth for "{key}" has been successfully changed to {birthday}.'
    else:
        raise CustomException(
            f'Contact "{key}" does not exist or you have not specified new date of birth!!!')


@input_error
def change_address(command_line):
    key, address = prepare_value_3(command_line)
    if key in contacts.keys():
        contacts.get_record(key).address = address
        return f'Address for the contact "{key}" has been successfully changed to "{address}".'
    else:
        raise CustomException(
            f'Contact "{key}" does not exist!')


@input_error
def change_phone(command_line):
    phones = [command_line.pop(-1)]
    phones.insert(0, command_line.pop(-1))
    key = ' '.join(command_line).strip()
    if key not in contacts.keys():
        return f'Wrong name "{key}" or you have not specified the new phone number.'
    if len(phones) != 2:
        raise CustomException(
            '''The command must be with a NAME and 2 phones you want to change 
            (Format: <change> <name> <old phone> <new phone>)''')
    if re.search('\(0\d{2}\)\d{3}-\d{2}-\d{2}', phones[1]):
        if phones[0] in contacts.get_record(key).phones_list:
            ix = contacts.get_record(key).phones_list.index(phones[0])
            if ix >= 0:
                contacts.get_record(key).phones_list[ix] = phones[1]
            return f'Phone number for "{key}" has been successfully changed to {phones[1]}.'
        else:
            raise CustomException(
                f'Phone number {phones[0]} does not exist!!!')
    else:
        raise CustomException(
            'Wrong phone number format. Use (0XX)XXX-XX-XX format!')

 # Š±Š»Š¾Šŗ ŠŗŠ¾Š“Š° ŠŗŠ°ŃŠ°ŃŃŠøŠ¹ŃŃ Š·Š°Š¼ŠµŃŠ¾Šŗ###########


@input_error
def add_note(command_line):
    """ Š”Š°Š¼Š° ŃŃŃŃŠŗŃŃŃŠ° Š·Š°Š¼ŠµŃŠ¾Šŗ ŃŃŠ¾ Š¾Š±ŃŃŠ½ŃŠ¹ ŃŠµŠŗŃŃŠ¾Š²ŃŠ¹ ŃŠ°Š¹Š», ŠŗŠ°Š¶Š“Š°Ń ŃŃŃŠ¾ŠŗŠ°
        ŠŗŠ¾ŃŠ¾ŃŠ¾Š³Š¾ ŃŃŠ¾ ŠµŃŃŃ Š¾Š“Š½Š° Š·Š°Š¼ŠµŃŠŗŠ°
        Š ŠŗŠ°ŃŠµŃŃŠ²Šµ ŠøŠ“ŠµŠ½ŃŠøŃŠøŠŗŠ°ŃŠ¾ŃŠ° Š²ŃŃŃŃŠæŠµŃ Š“Š°ŃŠ° Šø Š²ŃŠµŠ¼Ń ŃŠ¾Š·Š“Š°Š½ŠøŃ Š·Š°Š¼ŠµŃŠŗŠø,
        ŠæŃŠøŠ²ŠµŠ“ŠµŠ½Š½ŃŠµ Šŗ ŃŃŃŠ¾ŠŗŠ¾Š²Š¾Š¼Ń Š²ŠøŠ“Ń - ŃŃŠ¾Š±Ń ŃŠ°Š¹Š» Š¼Š¾Š¶Š½Š¾ Š±ŃŠ»Š¾ Š¾ŃŠŗŃŃŠ²Š°ŃŃ
        Š¾Š±ŃŃŠ½ŃŠ¼ ŃŠµŠŗŃŃŠ¾Š²ŃŠ¼ ŃŠµŠ“Š°ŠŗŃŠ¾ŃŠ¾Š¼. ŠŠ°Š»ŠµŠµ ŃŃŠ¾Ń ŠøŠ“ŠµŠ½ŃŠøŃŠøŠŗŠ°ŃŠ¾Ń ŠøŃŠæŠ¾Š»ŃŠ·ŃŠµŃŃŃ
        Š“Š»Ń ŠøŠ½Š“ŠµŠŗŃŠ°ŃŠøŠø ŠæŠ¾ Š·Š°Š¼ŠµŃŠŗŠ°Š¼ (ŃŠµŠ“Š°ŠŗŃŠøŃŠ¾Š²Š°Š½ŠøŠµ, ŃŠ“Š°Š»ŠµŠ½ŠøŠµ, ŠæŠ¾ŠøŃŠŗ)
    """
    note = ' '.join(command_line)
    current_id = datetime.now()
    # ŠæŃŠµŠ¾Š±ŃŠ°Š·Š¾Š²Š°Š»Šø Š² ŃŃŃŠ¾ŠŗŃ Š“Š°ŃŃ Š²ŃŠµŠ¼Ń ŃŠ¾Š·Š“Š°Š½ŠøŃ
    crt = current_id.strftime("%d.%m.%Y - %H:%M:%S")
    with open(f"{os.path.dirname(os.path.abspath(__file__))}/note.txt", "a+") as file:
        file.write(crt+" :: "+note+"\n")  # ŠæŠµŃŠ²ŃŠµ 21 ŃŠøŠ¼Š²Š¾Š» - ŃŃŃŠ¾ŠŗŠ°
    return "The note is added."


@input_error
def find_note(command_line):
    """ ŠŠ¾ŠøŃŠŗ Š·Š°Š“Š°ŠµŃŃŃ ŠæŠ¾ ŃŃŠµŠ¼ ŠæŠµŃŠµŠ¼ŠµŠ½Š½ŃŠ¼
        ŠŗŠ»ŃŃŠµŠ²Š¾Šµ ŃŠ»Š¾Š²Š¾ - Š±ŠµŠ· ŃŃŠ¾Š³Š¾ ŃŠ»Š¾Š²Š° Š·Š°Š¼ŠµŃŠŗŠ° Š½Šµ ŠøŠ½ŃŠµŃŠµŃŃŠµŃ
        Š“Š°ŃŠ° ŃŃŠ°ŃŃŠ° - ŃŠ°Š½ŠµŠµ ŃŃŠ¾Š¹ Š“Š°ŃŃ Š·Š°Š¼ŠµŃŠŗŠø Š½Šµ ŠøŠ½ŃŠµŃŠµŃŃŃŃ
        Š“Š°ŃŠ° ŠŗŠ¾Š½ŃŠ° - ŠæŠ¾Š·Š¶Šµ ŃŃŠ¾Š¹ Š“Š°ŃŃ Š·Š°Š¼ŠµŃŠŗŠø Š½Šµ ŠøŠ½ŃŠµŃŠµŃŃŃŃ

        ŃŠµŠ¹ŃŠ°Ń Š¾Š³ŃŠ°Š½ŠøŃŠøŠ²Š°ŠµŠ¼ ŠæŠ¾ŠøŃŠŗ Š“Š°ŃŠ°Š¼Šø, Š½Š¾ Š½Šµ Š²ŃŠµŠ¼ŠµŠ½ŠµŠ¼. ŠŃŠŗŠ»ŃŃŠøŃŠµŠ»ŃŠ½Š¾ Š“Š»Ń ŃŠ“Š¾Š±ŃŃŠ²Š° ŠæŠ¾Š»ŃŠ·Š¾Š²Š°ŃŠµŠ»Ń
        ŠæŠ¾ŃŠ»Šµ Š²ŃŠ²Š¾Š“Š° Š¼Š°ŃŃŠøŠ²Š° Š·Š°Š¼ŠµŃŠ¾Šŗ Š¾Š½ Š½Š°Š¹Š“ŠµŃ ŠøŠ½ŃŠµŃŠµŃŃŃŃŃŃ, ŃŠŗŠ¾ŠæŠøŃŃŠµŃ ŠµŠµ ŠæŠ¾Š»Š½ŃŠ¹ ŠøŠ“ŠµŠ½ŃŠøŃŠøŠŗŠ°ŃŠ¾Ń Šø ŠæŠµŃŠµŠ¹Š“ŠµŃ Šŗ Š½ŠµŠ¹
        Š½ŠµŠæŠ¾ŃŃŠµŠ“ŃŃŠ²ŠµŠ½Š½Š¾, ŠµŃŠ»Šø Š½ŃŠ¶Š½Š¾
    """
    # ŃŠ°Š·Š±ŠøŃŠ°ŠµŠ¼ ŠŗŠ¾Š¼Š°Š½Š“Ń Š² ŃŠ¾ŃŠ¼Š°Ń (keyword:str, start:'start date' = '', end:'end_date' = ''):
    if len(command_line) >= 3:
        keyword = command_line[0].lower()
        start = command_line[1]
        end = command_line[2]
    elif len(command_line) == 2:
        keyword = command_line[0].lower()
        start = command_line[1]
        end = ''
    elif len(command_line) == 1:
        keyword = command_line[0].lower()
        start = ''
        end = ''
    else:
        keyword = ''
        start = ''
        end = ''

    try:
        start_date = datetime.strptime(start, "%d.%m.%Y")
    except:
        print("Search start date is not stated in the DD.MM.YYYY format. The search will be performed from the first note.")
        # Š½Š°ŃŠ°Š»Š¾ ŠæŠ¾ŠøŃŠŗŠ° Ń Š“Š°ŃŃ Š½Š°ŃŠ°Š»Š° Š­ŠæŠ¾ŃŠø
        start_date = datetime.strptime("01.01.1970", "%d.%m.%Y")

    try:
        end_date = datetime.strptime(end, "%d.%m.%Y")
    except:
        print("Search end date is not stated in the DD.MM.YYYY format. The search will be performed till the last note.")
        end_date = datetime.now()   # ŠŗŠ¾Š½ŠµŃ ŠæŠ¾ŠøŃŠŗŠ° Š“Š¾ ŃŠµŠŗŃŃŠµŠ³Š¾ Š¼Š¾Š¼ŠµŠ½ŃŠ°

    if (type(keyword) == str) and (keyword != ''):
        pass
    else:
        print("The keyword is not stated. The search will be performed for all notes.")

    with open(f"{os.path.dirname(os.path.abspath(__file__))}/note.txt", "r+") as file:
        lines = file.readlines()  # ŃŠæŠøŃŠ¾Šŗ ŃŃŃŠ¾Šŗ ŠøŠ· ŃŠ°Š¹Š»Š° Š·Š°Š¼ŠµŃŠ¾Šŗ

    msg = "No one note is found."
    for i in lines:
        date_id = i[:10]  # Š²ŃŃŠµŠ·Š°Š»Šø ŠŗŃŃŠ¾Šŗ ŃŃŃŠ¾ŠŗŠø - Š“Š°ŃŠ° ŃŠ¾Š·Š“Š°Š½ŠøŠµ Š·Š°Š¼ŠµŃŠŗŠø
        # ŠŗŠ¾Š½Š²ŠµŃŃ Š² Š¾Š±ŃŠµŠŗŃ, ŃŃŠ¾Š±Ń ŃŃŠ°Š²Š½ŠøŠ²Š°ŃŃ
        n_id = datetime.strptime(date_id, "%d.%m.%Y")
        if (n_id >= start_date) and (n_id <= end_date):
            if (type(keyword) == str) and (keyword != ''):
                j = i.lower()      # ŠæŃŠøŠ²Š¾Š“ŠøŠ¼ Š¾ŃŠøŠ³ŠøŠ½Š°Š»ŃŠ½ŃŃ ŃŃŃŠ¾ŠŗŃ Šŗ Š½ŠøŠ¶Š½ŠµŠµŠ¼Ń ŃŠµŠ³ŠøŃŃŃŃ
                # ŠµŃŠ»Šø ŠµŃŃŃ ŠŗŠ»ŃŃ(Š½ŠøŠ¶Š½ŠøŠ¹ ŃŠµŠ³ŠøŃŃŃ) Š² ŃŃŃŠ¾ŠŗŠµ (Š½ŠøŠ¶Š½ŠøŠ¹ ŃŠµŠ³ŠøŃŃŃ ) Š²ŃŠ²Š¾Š“ŠøŠ¼ Š¾ŃŠøŠ³ŠøŠ½Š°Š»ŃŠ½ŃŃ
                if keyword in j:
                    # Š·Š°Š±ŠøŠ»Šø ŠæŠ¾ŃŠ»ŠµŠ“Š½ŠøŠ¹ ŃŠøŠ¼Š²Š¾Š» ŠæŠµŃŠµŠ½Š¾ŃŠ° ŃŃŃŠ¾ŠŗŠø - Š“Š»Ń ŠŗŃŠ°ŃŠøŠ²Š¾Š³Š¾ Š²ŃŠ²Š¾Š“Š°
                    print(OutputToTerminal().output_note(i))
                    msg = "Notes are found."
            else:
                # Š²ŃŠ²Š¾Š“ŠøŠ¼ Š²ŃŠµ ŃŃŃŠ¾ŠŗŠø - Š½ŠµŃ ŠŗŠ»ŃŃŠ°
                print(OutputToTerminal().output_note(i))
                msg = "Notes are found."
    return msg


@input_error
def change_note(command_line):
    """ŠŠ»Ń ŠøŠ·Š¼ŠµŠ½ŠµŠ½ŠøŃ Š·Š°Š¼ŠµŃŠŗŠø Š½ŃŠ¶Š½Š¾ Š“Š°ŃŃ Š°ŃŠ³ŃŠ¼ŠµŠ½ŃŠ¾Š¼ ŠµŠµ ŠæŠ¾Š»Š½ŃŠ¹ ŠøŠ“ŠµŠ½ŃŠøŃŠøŠŗŠ°ŃŠ¾Ń ŃŠ¾ Š²ŃŠµŠ¼ŠµŠ½ŠµŠ¼,
       ŠµŠ³Š¾ ŃŠ“Š¾Š±Š½Š¾ ŃŠŗŠ¾ŠæŠøŃŠ¾Š²Š°ŃŃ ŠæŠ¾ŃŠ»Šµ Š¾Š±ŃŠµŠ³Š¾ ŠæŠ¾ŠøŃŠŗŠ°
       Š° ŃŠ°ŠŗŠ¶Šµ Š“Š°Š½Š½ŃŠµ ŠŗŠ¾ŃŠ¾ŃŃŠµ Š“Š¾Š»Š¶Š½Ń Š±ŃŃŃ Š·Š°ŠæŠøŃŠ°Š½Ń Š² ŃŃŃ Š·Š°Š¼ŠµŃŠŗŃ Ń ŃŃŠøŠ¼ Š¶Šµ ŠøŠ“ŠµŠ½ŃŠøŃŠøŠŗŠ°ŃŠ¾ŃŠ¾Š¼

    """
    # ŃŠ°Š·Š±ŠøŃŠ°ŠµŠ¼ ŠŗŠ¾Š¼Š°Š½Š“Ń Š² ŃŠ¾ŃŠ¼Š°Ń (dt_id:"%d.%m.%Y - %H:%M:%S" = '', data:str = '')
    if len(command_line) >= 4:
        dt_id = command_line[0]+' '+command_line[1]+' '+command_line[2]
        command_line.pop(0)
        command_line.pop(0)
        command_line.pop(0)
        data = ' '.join(command_line)
    elif len(command_line) == 3:
        dt_id = command_line[0]+command_line[1]+command_line[2]
        data = ''
    else:
        dt_id = ''
        data = ''

    msg = "No one note is changed."
    try:
        # ŠæŃŠ¾Š²ŠµŃŠŗŠ° ŃŃŠ¾ ŠøŠ“ŠµŠ½ŃŠøŃŠøŠŗŠ°ŃŠ¾Ń Š·Š°Š“Š°Š½ Š² ŃŠ¾ŃŠ¼Š°ŃŠµ
        loc_id = datetime.strptime(dt_id, "%d.%m.%Y - %H:%M:%S")
        try:
            with open(f"{os.path.dirname(os.path.abspath(__file__))}/note.txt", "r") as file:
                buffer = file.readlines()
            for i in range(len(buffer)):
                d_id = buffer[i][:21]  # ŠæŠ¾Š»Š½ŃŠ¹ ŠøŠ“ŠµŠ½ŃŠøŃŠøŠŗŠ°ŃŠ¾Ń
                n_id = datetime.strptime(d_id, "%d.%m.%Y - %H:%M:%S")
                if n_id == loc_id:  # ŃŠ¾Š²ŠæŠ°Š“ŠµŠ½ŠøŠµ ŃŠµŠŗŃŃŠµŠ³Š¾ ŠøŠ“ Ń Š·Š°Š“Š°Š½Š½ŃŠ¼
                    if data != '':
                        # Š·Š°Š¼ŠµŠ½Š° ŃŃŃŠ¾ŠŗŠø, ŠøŠ“ŠµŠ½ŃŠøŃŠøŠŗŠ°ŃŠ¾Ń Š¾ŃŃŠ°ŠµŃŃŃ
                        buffer[i] = d_id+" :: "+data+"\n"
                        msg = "The note is changed"
                        break
                    else:
                        in_q = input(
                            "The field for change is empty. Are you sure? y or n")
                        if in_q == 'y':
                            # Š·Š°Š¼ŠµŠ½Š° ŃŃŃŠ¾ŠŗŠø, ŠøŠ“ŠµŠ½ŃŠøŃŠøŠŗŠ°ŃŠ¾Ń Š¾ŃŃŠ°ŠµŃŃŃ
                            buffer[i] = d_id+" :: "+data+"\n"
                            msg = "The note is changed"
                        break
            # ŃŠ“Š°Š»ŃŠµŠ¼ ŃŠ¾Š“ŠµŃŠ¶ŠøŠ¼Š¾Šµ ŃŃŠ°ŃŠ¾Š³Š¾ ŃŠ°Š¹Š»Š°, ŠæŠøŃŠµŠ¼ Š·Š°Š½Š¾Š²Š¾
            with open(f"{os.path.dirname(os.path.abspath(__file__))}/note.txt", "w") as file:
                file.writelines(buffer)  # ŠæŠøŃŠµŠ¼ ŠæŠ¾ŃŃŃŠ¾ŃŠ½Š¾ ŠøŠ· Š±ŃŃŠµŃŠ°
        except:
            print("ID selection error. Maybe the reason is manual file editing.")

    except:
        print("The ID is not in the DD.MM.YYYY - hh.mm.ss format. Copy ID from the search results.")
    return msg


@input_error
def delete_note(command_line):
    """ŠŠ»Ń ŃŠ“Š°Š»ŠµŠ½ŠøŃ Š·Š°Š¼ŠµŃŠŗŠø Š½ŃŠ¶Š½Š¾ Š“Š°ŃŃ Š°ŃŠ³ŃŠ¼ŠµŠ½ŃŠ¾Š¼ ŠµŠµ ŠæŠ¾Š»Š½ŃŠ¹ ŠøŠ“ŠµŠ½ŃŠøŃŠøŠŗŠ°ŃŠ¾Ń ŃŠ¾ Š²ŃŠµŠ¼ŠµŠ½ŠµŠ¼,
       ŠµŠ³Š¾ ŃŠ“Š¾Š±Š½Š¾ ŃŠŗŠ¾ŠæŠøŃŠ¾Š²Š°ŃŃ ŠæŠ¾ŃŠ»Šµ Š¾Š±ŃŠµŠ³Š¾ ŠæŠ¾ŠøŃŠŗŠ° - Š²Š¼ŠµŃŃŠµ Ń ŠŗŠ°Š²ŃŃŠŗŠ°Š¼Šø
    """
    # ŃŠ°Š·Š±ŠøŃŠ°ŠµŠ¼ ŠŗŠ¾Š¼Š°Š½Š“Ń Š² ŃŠ¾ŃŠ¼Š°Ń (dt_id:"%d.%m.%Y - %H:%M:%S" = '')
    if len(command_line) == 3:
        dt_id = command_line[0]+' '+command_line[1]+' '+command_line[2]
    else:
        dt_id = ''

    msg = "No one note is deleted"
    try:
        # ŠæŃŠ¾Š²ŠµŃŠŗŠ° ŃŃŠ¾ ŠøŠ“ŠµŠ½ŃŠøŃŠøŠŗŠ°ŃŠ¾Ń Š·Š°Š“Š°Š½ Š² ŃŠ¾ŃŠ¼Š°ŃŠµ
        loc_id = datetime.strptime(dt_id, "%d.%m.%Y - %H:%M:%S")
        try:
            with open(f"{os.path.dirname(os.path.abspath(__file__))}/note.txt", "r") as file:
                buffer = file.readlines()
            for i in range(len(buffer)):
                d_id = buffer[i][:21]  # ŠæŠ¾Š»Š½ŃŠ¹ ŠøŠ“ŠµŠ½ŃŠøŃŠøŠŗŠ°ŃŠ¾Ń
                n_id = datetime.strptime(d_id, "%d.%m.%Y - %H:%M:%S")
                if n_id == loc_id:  # ŃŠ¾Š²ŠæŠ°Š“ŠµŠ½ŠøŠµ ŃŠµŠŗŃŃŠµŠ³Š¾ ŠøŠ“ Ń Š·Š°Š“Š°Š½Š½ŃŠ¼
                    buffer.pop(i)
                    msg = "The note is deleted"
                    break
            # ŃŠ“Š°Š»ŃŠµŠ¼ ŃŠ¾Š“ŠµŃŠ¶ŠøŠ¼Š¾Šµ ŃŃŠ°ŃŠ¾Š³Š¾ ŃŠ°Š¹Š»Š°, ŠæŠøŃŠµŠ¼ Š·Š°Š½Š¾Š²Š¾
            with open(f"{os.path.dirname(os.path.abspath(__file__))}/note.txt", "w") as file:
                file.writelines(buffer)  # ŠæŠøŃŠµŠ¼ ŠæŠ¾ŃŃŃŠ¾ŃŠ½Š¾ ŠøŠ· Š±ŃŃŠµŃŠ°
        except:
            print("ID selection error. Maybe the reason is manual file editing.")

    except:
        print("The ID is not in the DD.MM.YYYY - hh.mm.ss format. Copy ID from the search results.")
    return msg


@input_error
def tag_note(command_line):
    """ŠŃŠøŠ²ŃŠ·ŠŗŠ° ŃŠµŠ³Š° Šŗ Š·Š°Š¼ŠµŃŠŗŠµ, Š“Š°Š»ŠµŠµ ŠæŠ¾ŠøŃŠŗ Ń ŃŠµŃŃŠµŠ³Š¾Š¼ Š¾ŃŃŃŠµŃŃŠ²Š»ŃŠµŃŃŃ
       Š¾Š±ŃŃŠ½Š¾Š¹ ŠŗŠ¾Š¼Š°Š½Š“Š¾Š¹ find note #....
    """
    # ŃŠ°Š·Š±ŠøŃŠ°ŠµŠ¼ ŠŗŠ¾Š¼Š°Š½Š“Ń Š² ŃŠ¾ŃŠ¼Š°Ń (dt_id:"%d.%m.%Y - %H:%M:%S" = '', tag:str = '')
    if len(command_line) >= 4:
        dt_id = command_line[0] + ' ' + command_line[1] + ' ' + command_line[2]
        tag = command_line[3]
    elif len(command_line) == 3:
        dt_id = command_line[0] + command_line[1] + command_line[2]
        tag = ''
    else:
        dt_id = ''
        tag = ''

    msg = "The hashtag is not acceptable."
    try:
        # ŠæŃŠ¾Š²ŠµŃŠŗŠ° ŃŃŠ¾ ŠøŠ“ŠµŠ½ŃŠøŃŠøŠŗŠ°ŃŠ¾Ń Š·Š°Š“Š°Š½ Š² ŃŠ¾ŃŠ¼Š°ŃŠµ
        loc_id = datetime.strptime(dt_id, "%d.%m.%Y - %H:%M:%S")
        try:
            with open(f"{os.path.dirname(os.path.abspath(__file__))}/note.txt", "r") as file:
                buffer = file.readlines()
            for i in range(len(buffer)):
                d_id = buffer[i][:21]  # ŠæŠ¾Š»Š½ŃŠ¹ ŠøŠ“ŠµŠ½ŃŠøŃŠøŠŗŠ°ŃŠ¾Ń
                n_id = datetime.strptime(d_id, "%d.%m.%Y - %H:%M:%S")
                if n_id == loc_id:  # ŃŠ¾Š²ŠæŠ°Š“ŠµŠ½ŠøŠµ ŃŠµŠŗŃŃŠµŠ³Š¾ ŠøŠ“ Ń Š·Š°Š“Š°Š½Š½ŃŠ¼
                    if tag != '':
                        # Š·Š°Š±ŠøŠ»Šø ŠæŠµŃŠµŠ½Š¾Ń ŃŃŃŠ¾ŠŗŠø, Š“Š¾Š±Š°Š²ŠøŠ»Šø ŃŠµŃŃŠµŠ³ Šø ŠæŠµŃŠµŠ½Š¾Ń
                        j = buffer[i][:len(buffer[i])-1] + '  #' + tag + '\n'
                        # ŃŃŃŠ¾ŠŗŠ° Š½ŠµŠøŠ·Š¼ŠµŠ½ŃŠµŠ¼Š°, Š½ŠµŠ»ŃŠ·Ń ŃŃŠ°Š·Ń ŠæŠøŃŠ°ŃŃ buffer[i] = buffer[i] + tag
                        buffer[i] = j
                        msg = "The hashtag is accepted."
                        break
                    else:
                        in_q = input("The tag is empty. Are you sure? y or n")
                        if in_q == 'y':
                            # Š·Š°Š±ŠøŠ»Šø ŠæŠµŃŠµŠ½Š¾Ń ŃŃŃŠ¾ŠŗŠø, Š“Š¾Š±Š°Š²ŠøŠ»Šø ŃŠµŃŃŠµŠ³ Šø ŠæŠµŃŠµŠ½Š¾Ń
                            j = buffer[i][:len(buffer[i])-1] + \
                                '  #' + tag + '\n'
                            # ŃŃŃŠ¾ŠŗŠ° Š½ŠµŠøŠ·Š¼ŠµŠ½ŃŠµŠ¼Š°, Š½ŠµŠ»ŃŠ·Ń ŃŃŠ°Š·Ń ŠæŠøŃŠ°ŃŃ buffer[i] = buffer[i] + tag
                            buffer[i] = j
                            msg = "The hashtag is accepted."
                        break
            # ŃŠ“Š°Š»ŃŠµŠ¼ ŃŠ¾Š“ŠµŃŠ¶ŠøŠ¼Š¾Šµ ŃŃŠ°ŃŠ¾Š³Š¾ ŃŠ°Š¹Š»Š°, ŠæŠøŃŠµŠ¼ Š·Š°Š½Š¾Š²Š¾
            with open(f"{os.path.dirname(os.path.abspath(__file__))}/note.txt", "w") as file:
                file.writelines(buffer)  # ŠæŠøŃŠµŠ¼ ŠæŠ¾ŃŃŃŠ¾ŃŠ½Š¾ ŠøŠ· Š±ŃŃŠµŃŠ°
        except:
            print("ID selection error. Maybe the reason is manual file editing.")

    except:
        print("The ID is not in the DD.MM.YYYY - hh.mm.ss format. Copy ID from the search results.")
    return msg


@input_error
def help_common(command_line):

    try:
        file = open(
            f"{os.path.dirname(os.path.abspath(__file__))}/help.txt", 'r')
        OutputToTerminal().output_help(file.readlines())
        file.close()
        msg = "The end of the help."
    except:
        msg = "File help.txt is not found."
    return msg


def start_note():  # ŠæŃŠ¾Š²ŠµŃŠŗŠ° ŃŃŠ¾ ŃŠ°Š¹Š» ŃŃŃŠµŃŃŠ²ŃŠµŃ ŠøŠ»Šø ŠµŠ³Š¾ ŃŠ¾Š·Š“Š°Š½ŠøŠµ

    try:
        file = open(
            f"{os.path.dirname(os.path.abspath(__file__))}/note.txt", 'r')
        print("File note.txt with notes is loaded.")
    except:
        # ŃŠ¾Š·Š“Š°ŠµŠ¼ Š½Š¾Š²ŃŠ¹
        file = open(
            f"{os.path.dirname(os.path.abspath(__file__))}/note.txt", 'w')
        print("File note.txt with notes is created.")
    finally:
        file.close()


@input_error
def show_all(command_line):

    if len(contacts.items()) > 0:
        return str(contacts)
    else:
        return 'There are no contacts in the book.'


@input_error
def clean_func(command_line):
    return clean.start_cleaning(command_line)


COMMANDS = {
    'close': exit_func,
    'exit': exit_func,
    'good bye': exit_func,
    'save': save_func,
    'add': add_name,
    'add address': add_address,
    'add birthday': add_birthday,
    'add email': add_email,
    'add phone': add_phone,
    'remove': remove,
    'delete address': delete_address,
    'delete birthday': delete_birthday,
    'delete email': delete_email,
    'delete phone': delete_phone,
    'change email': change_email,
    'change birthday': change_birthday,
    'change address': change_address,
    'change phone': change_phone,
    'coming birthday': coming_birthday,
    "add note": add_note,
    "find note": find_note,
    "change note": change_note,
    "delete note": delete_note,
    "tag note": tag_note,
    "help": help_common,
    'show all': show_all,
    'search': search,
    'clean': clean_func
}

ONE_WORD_COMMANDS = ['add', 'clean', 'close', "help",
                     'exit', 'save', 'remove', 'search']
TWO_WORDS_COMMANDS = ['add address', 'add birthday', 'add email', 'add phone',
                      'delete address', 'delete birthday', 'delete email', 'delete phone',
                      'change email', 'change birthday', 'change address', 'change phone',
                      'coming birthday', 'good bye', "add note", "find note", "change note",
                      "delete note", "tag note", 'show all']


def get_handler(command):
    return COMMANDS[command]


def main():

    print("Enter 'help' command to see all the commands available.")
    start_note()
    print(contacts.load_from_file(
        f"{os.path.dirname(os.path.abspath(__file__))}/contacts.bin"))

    while True:
        command_line = []
        while not command_line:
            command_line = prompt('>>> ',
                                  history=FileHistory('history'),
                                  auto_suggest=AutoSuggestFromHistory(),
                                  completer=SqlCompleter,
                                  style=style
                                  ).split()

        right_command = False

        if len(command_line) > 1 and \
           f'{command_line[0].lower()} {command_line[1].lower()}' in TWO_WORDS_COMMANDS:
            command = f'{command_line.pop(0).lower()} {command_line.pop(0).lower()}'
            right_command = True

        if not right_command:
            command = command_line.pop(0).lower()
            right_command = command in ONE_WORD_COMMANDS

        if not right_command:
            print(
                f'The "{command}" command is wrong! The allowable commands are {", ".join(ONE_WORD_COMMANDS + TWO_WORDS_COMMANDS)}.')
            continue

        handler = get_handler(command)
        print(handler(command_line))
        if handler is exit_func:
            print(contacts.save_to_file(
                f"{os.path.dirname(os.path.abspath(__file__))}/contacts.bin"))
            break


if __name__ == '__main__':
    main()
