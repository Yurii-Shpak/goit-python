from collections import UserDict
from datetime import datetime
import os.path
import pickle
import re


class AddressBook(UserDict):

    def add_record(self, record):
        self.data[record.name.value] = record

    def remove_record(self, name):
        self.data.pop(name)
        
    def get_record(self, name):
        return self.data.get(name)
        
    def has_record(self, name):
        return name in self.data.keys()

    def iterator(self, records_per_page=20):
        dict_length = len(contacts)
        pages = dict_length // records_per_page
        if dict_length % records_per_page > 0:
            pages += 1
        contacts_list = [[name, record] for name, record in contacts.items()]
        counter = 0
        limit = records_per_page
        page_counter = 1
        while True:
            print('\n' + '-' * 15)
            print(f'Page #{page_counter} of {pages}')
            print('-' * 40)
            yield page_counter == pages, '\n'.join([form_record(item[0], item[1], '')[:-1] for item in contacts_list[counter:limit]])
            counter += records_per_page
            limit += records_per_page
            if counter >= dict_length:
                break
            page_counter += 1

    def load_from_file(self, file_name):
        if os.path.exists(file_name):
            with open(file_name, 'rb') as fh:
                self.data = pickle.load(fh)
                if len(self.data):
                    return f'The contacts book is loaded from the file "{file_name}".'
                else:
                    return 'This is empty contacts book. Add contacts to it.'
        else:
            return 'This is empty contacts book. Add contacts into it.'

    def save_to_file(self, file_name):
        with open(file_name, 'wb') as fh:
            pickle.dump(self.data, fh)
        return f'The contacts book is saved in the file "{file_name}".'


contacts = AddressBook()


class Field:

    def __init__(self, value=None):
        self.__value = value

    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, new_value):
        self.__value = new_value


class Birthday(Field):

    CHECK_DATE_RE = '(0?[1-9]|[12][0-9]|3[01])\.(0?[1-9]|1[012])\.((19|20)\d\d)'
    
    def __init__(self, value=None):
        if re.match(self.CHECK_DATE_RE, value):
            self.__value = value
        else:
            raise Exception

    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, new_value):
        if re.match(self.CHECK_DATE_RE, new_value):
            self.__value = new_value
        else:
            raise Exception

    
class Name(Field):

    pass


class Phone(Field):

    CHECK_PHONE_RE = '\(0\d{2}\)\d{3}-\d{2}-\d{2}'
    
    def __init__(self, value=None):
        if re.match(self.CHECK_PHONE_RE, value):
            self.__value = value
        else:
            raise PhoneException

    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, new_value):
        if re.match(self.CHECK_PHONE_RE, new_value):
            self.__value = new_value
        else:
            raise PhoneException


class PhoneException(Exception):
    pass


class Record:

    def __init__(self, name, phones_list=[], birthday=None):
        self.name = name
        self.phones_list = phones_list
        self.birthday = birthday

    def add_birthday(self, birthday):
        self.birthday = birthday

    def add_phone(self, phone):
        self.phones_list.append(phone)

    def change_birthday(self, birthday):
        self.birthday.value = birthday

    def change_phone(self, old_phone, new_phone):
        if self.has_phone(old_phone):
            if self.has_phone(new_phone):
                return 0
            else:
                self.get_phone(old_phone).value = new_phone
                return 1
        else:
            return 2

    def days_to_birthday(self):
        if self.birthday:
            birthday = datetime.strptime(self.birthday.value, '%d.%m.%Y').date()
            today = datetime.now().date()
            delta = datetime(today.year, birthday.month, birthday.day).date() - today
            if delta.days >= 0:
                return delta.days
            else:
                return (datetime(today.year + 1, birthday.month, birthday.day).date() - today).days
        else:
            return -1

    def delete_phone(self, phone):
        for phone_obj in self.phones_list:
            if phone_obj.value == phone: 
                self.phones_list.remove(phone_obj)
                return True
        return False
        
    def get_birthday(self):
        return self.birthday.value
        
    def get_phone(self, phone):
        for phone_obj in self.phones_list:
            if phone_obj.value == phone:
                return phone_obj
        
    def get_phones_list(self, delimiter=', '):
        return delimiter.join([i.value for i in self.phones_list])

    def has_phone(self, phone):
        return phone in [i.value for i in self.phones_list]
    
    
def input_error(func):

    def inner(command_line):
        
        try:
            result = func(command_line)
        except PhoneException:
            result = 'The phone number is wrong! Use (0XX)XXX-XX-XX format!'
        except:
            if func.__name__ == 'add_func':
                result = f'Give me the name, please, or the name and the phone number separated with the space symbol.'
            if func.__name__ == 'change_func':
                result = f'Give me the name, the old phone number and a new phone number, please. Separate them with the space symbol.'
            if func.__name__ == 'delete_func':
                result = f'Give me the name and the phone number separated with the space symbol, please.'
            if func.__name__ == 'phone_func':
                result = 'Enter the name of an existing contact, please.'
            if func.__name__ == 'set_birthday_func':
                result = f'The birthday is not set! Wrong date or format of the date! Use DD.MM.YYYY format.'
        return result
    
    return inner


@input_error
def add_func(command_line):

    name, phone, dummy = get_name_phone(command_line)
        
    if contacts.has_record(name):
        record = contacts.get_record(name)
        if phone in [i.value for i in record.phones_list]: 
            return f'The phone number {phone} for the name "{name}" exists already.'
        else:
            record.add_phone(Phone(phone))
            return f'The phone number {phone} for the name "{name}" is added.'
    else:
        if phone:
            contacts.add_record(Record(Name(name), [Phone(phone)]))
            return f'Record for "{name}" with the phone number {phone} is added.'
        else:
            contacts.add_record(Record(Name(name), []))
            return f'Record for "{name}" without a phone number is added.'


@input_error
def birthday_func(command_line):

    name = ' '.join(command_line).strip()
    if name:
        if contacts.has_record(name):
            record = contacts.get_record(name)
            if record.birthday:
                return f'{record.get_birthday()}. Days to the next birthday: {record.days_to_birthday()}'
            else:
                return f'There no birthday set for the name "{name}".'
        else:
            return f'The contact with the name "{name}" is not found.'
    else:
        return 'Give me the name of a contact, please.'


@input_error
def change_func(command_line):

    name, new_phone, old_phone = get_name_phone(command_line, True)
    
    if name == '' or old_phone == '':
        return f'Give me the name, the old phone number and a new phone number, please. Separate them with the space symbol.'
    elif contacts.has_record(name):
        return [f'The phone number {new_phone} exists for the "{name}" already. The phone number {old_phone} was not changed.',
                f'Record for "{name}" is updated. The phone number {old_phone} is replaced with {new_phone}.',
                f'The phone number {old_phone} does not exist for the "{name}".']\
               [contacts.get_record(name).change_phone(old_phone, new_phone)]
    else:
        return f'Record for the name "{name}" does not exist. Enter the correct name, please.'


@input_error
def delete_func(command_line):

    name, phone, dummy = get_name_phone(command_line)
        
    if contacts.has_record(name):
        if phone:
            if contacts.get_record(name).delete_phone(phone):
                return f'The phone number {phone} was deleted from the record for "{name}".'
            else:
                return f'The phone number {phone} was not found for the name "{name}".'
        else:
            return f'To delete a record use the "remove" command.'
    else:
        return f'Record for "{name}" does not exist.'


@input_error
def exit_func(command_line):

    return 'Good bye!'


@input_error
def find_func(command_line):

    search = ' '.join(command_line).strip().lower()
    if search:
        
        result = ''
        for name, record in contacts.items():
            if name.lower().find(search) > -1 or record.get_phones_list().find(search) > -1:
                result = form_record(name, record, result)

        if result:
            return result[:-1]
        else:
            return f'There are no results for the search string "{search}".'
    else:
        return 'Give me the search string, please.'


def get_name_phone(command_line, two_phones=False):

    # Имя может состоять из нескольких слов
    if len(command_line) > 1:
        phones = ['', '']
        for i in range(int(two_phones) + 1):
            phones[i] = command_line.pop(len(command_line) - 1).strip()  # Выкусываем номер телефона
        name = ' '.join(command_line).strip()

        return name, phones[0], phones[1]
    else:
        return command_line[0], '', ''


@input_error
def hello_func(command_line):

    return 'How can I help you?'


@input_error
def phone_func(command_line):

    name = ' '.join(command_line).strip()
    if name:
        if contacts.has_record(name):
            phones = contacts.get_record(name).get_phones_list()
            if phones == '':
                return f'There are no phone numbers for "{name}"'
            else:
                return phones
        else:
            return f'The contact with the name "{name}" is not found.'
    else:
        return 'Give me the name of a contact, please.'


@input_error
def remove_func(command_line):

    name = ' '.join(command_line).strip()
        
    if contacts.has_record(name):
        contacts.remove_record(name)
        return f'The record for "{name}" was deleted.'
    else:
        return f'Record for "{name}" does not exist.'


@input_error
def save_func(command_line):

    return contacts.save_to_file('contacts.bin')


@input_error
def set_birthday_func(command_line):

    if command_line:    

        name, birthday, dummy = get_name_phone(command_line)
   
        if contacts.has_record(name):
            record = contacts.get_record(name)
            if birthday:
                if record.birthday:
                    record.change_birthday(birthday)
                    return f'Birthday {birthday} is set for the name "{name}".'
                else:
                    record.add_birthday(Birthday(birthday))
                    return f'Birthday {birthday} is added for the name "{name}".'
            else:
                return 'Give me the name and the birthday in DD.MM.YYYY format separated with the space symbol.'
        else:
            return f'There is no record for the name "{name}".'
    else:
        return 'Give me the name and the birthday in DD.MM.YYYY format separated with the space symbol.'


def is_integer(s):
    try:
        float(s)
    except ValueError:
        return False
    else:
        return float(s).is_integer()


def form_record(name, record, result):
    
    phones = record.get_phones_list()
    if phones:
        result += f'{name} - Phones: {phones}.'
    else:
        result += f'{name} - <HAS NO PHONE NUMBERS>'
    if record.birthday:
        result += f' Date of birth: {record.get_birthday()}. Days to the next birthday: {record.days_to_birthday()}'
    result += '\n'
    
    return result


@input_error
def show_func(command_line):

    result = ''
    if command_line:                        # Если указано что-то после show all (пагинация)
        if is_integer(command_line[-1]):    # Если последним указано целое число (записей на страницу)
            if len(contacts) > 0:
                for is_last_page, page in contacts.iterator(int(command_line[-1])):
                    print(page)
                    if not is_last_page:
                        print('-' * 40)
                        input(f'Press [ENTER] to view next {command_line[-1]} records.')
                return '-' * 40 + '\nThe end of the dict.'
            else:
                return 'The contacts book is empty.'
        else:
            return 'State number of records per page. For example, "show all by 10" or "show all 10".'
    else:
        # Обычный вывод всех записей, без пагинации
        for name, record in contacts.items():
            result = form_record(name, record, result)

        if result:
            return result[:-1]
        else:
            return 'The dict is empty.'


COMMANDS = {
    'add': add_func,
    'birthday': birthday_func,
    'change': change_func,
    'close': exit_func,
    'delete': delete_func,
    'exit': exit_func,
    'find': find_func,
    'good bye': exit_func,
    'hello': hello_func,
    'phone': phone_func,
    'remove': remove_func,
    'save': save_func,
    'set birthday': set_birthday_func,
    'show all': show_func
}


ONE_WORD_COMMANDS = ('add', 'birthday', 'change', 'close', 'delete', 'exit', 'find', 'hello', 'phone', 'remove', 'save')
TWO_WORDS_COMMANDS = ('good bye', 'set birthday', 'show all')


def get_handler(command):
    return COMMANDS[command]


def main():

    print(contacts.load_from_file('contacts.bin'))

    while True:
        command_line = []
        while not command_line:
            command_line = input('>>> ').split()

        right_command = False
        
        if len(command_line) > 1 and \
           f'{command_line[0].lower()} {command_line[1].lower()}' in TWO_WORDS_COMMANDS:
            command = f'{command_line.pop(0).lower()} {command_line.pop(0).lower()}'
            right_command = True

        if not right_command:
            command = command_line.pop(0).lower()
            right_command = command in ONE_WORD_COMMANDS
            
        if not right_command:
            print(f'The "{command}" command is wrong! The allowable commands are {", ".join(ONE_WORD_COMMANDS + TWO_WORDS_COMMANDS)}.')
            continue
        
        handler = get_handler(command)
        print(handler(command_line))
        if handler is exit_func:
            print(contacts.save_to_file('contacts.bin'))
            break

if __name__ == '__main__':
    main()
