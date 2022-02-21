from collections import UserDict


class AddressBook(UserDict):

    def add_record(self, record):
        self.data[record.name.value] = record

    def remove_record(self, name):
        self.data.pop(name)
        
    def get_record(self, name):
        return self.data.get(name)
        
    def has_record(self, name):
        return name in self.data.keys()


contacts = AddressBook()


class Field:

    def __init__(self, value=None):
        self.value = value


class Name(Field):

    pass


class Phone(Field):

    pass


class Record:

    def __init__(self, name, phones_list=[]):
        self.name = name
        self.phones_list = phones_list

    def add_phone(self, phone):
        self.phones_list.append(phone)

    def change_phone(self, old_phone, new_phone):
        if self.has_phone(old_phone):
            if self.has_phone(new_phone):
                result = 0
            else:
                self.get_phone(old_phone).value = new_phone
                result = 1
        else:
            result = 2
        return result

    def delete_phone(self, phone):
        for phone_obj in self.phones_list:
            if phone_obj.value == phone: 
                self.phones_list.remove(phone_obj)
                return True
        return False
        
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
        except:
            if func.__name__ == 'add_func':
                result = f'Give me the name, please, or the name and the phone number separated with the space symbol.'
            if func.__name__ == 'change_func':
                result = f'Give me the name, the old phone number and a new phone number, please. Separate them with the space symbol.'
            if func.__name__ == 'delete_func':
                result = f'Give me the name and the phone number separated with the space symbol, please.'
            if func.__name__ == 'phone_func':
                result = 'Enter the name of an existing contact, please.'
                
        return result
    
    return inner


@input_error
def add_func(command_line):

    name, phone, dummy = get_name_phone(command_line)
        
    if contacts.has_record(name):
        record = contacts.get_record(name)
        if phone in [i.value for i in record.phones_list]: 
            result = f'The phone number {phone} for the name "{name}" exists already.'
        else:
            record.add_phone(Phone(phone))
            result = f'The phone number {phone} for the name "{name}" is added.'
    else:
        if phone:
            contacts.add_record(Record(Name(name), [Phone(phone)]))
            result = f'Record for "{name}" with the phone number {phone} is added.'
        else:
            contacts.add_record(Record(Name(name), []))
            result = f'Record for "{name}" without a phone number is added.'

    return result


@input_error
def change_func(command_line):

    name, new_phone, old_phone = get_name_phone(command_line, True)
    
    if name == '' or old_phone == '':
        result = f'Give me the name, the old phone number and a new phone number, please. Separate them with the space symbol.'
    elif contacts.has_record(name):
        result = [f'The phone number {new_phone} exists for the "{name}" already. The phone number {old_phone} was not changed.',
                  f'Record for "{name}" is updated. The phone number {old_phone} is replaced with {new_phone}.',
                  f'The phone number {old_phone} does not exist for the "{name}".']\
                 [contacts.get_record(name).change_phone(old_phone, new_phone)]
    else:
        result = f'Record for the name "{name}" does not exist. Enter the correct name, please.'

    return result


@input_error
def delete_func(command_line):

    name, phone, dummy = get_name_phone(command_line)
        
    if contacts.has_record(name):
        if phone:
            if contacts.get_record(name).delete_phone(phone):
                result = f'The phone number {phone} was deleted from the record for "{name}".'
            else:
                result = f'The phone number {phone} was not found for the name "{name}".'
        else:
            result = f'To delete a record use the "remove" command.'
    else:
        result = f'Record for "{name}" does not exist.'

    return result


@input_error
def exit_func(command_line):

    return 'Good bye!'


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
        result = f'The record for "{name}" was deleted.'
    else:
        result = f'Record for "{name}" does not exist.'

    return result


@input_error
def show_func(command_line):
    result = ''
    for name, record in contacts.items():
        phones = record.get_phones_list()
        if phones:
            result += f'{name} {phones}\n'
        else:
            result += f'{name} <HAS NO PHONE NUMBERS>\n'
    if result:
        return result[:-1]
    else:
        return 'The dict is empty.'


COMMANDS = {
    'add': add_func,
    'change': change_func,
    'close': exit_func,
    'delete': delete_func,
    'exit': exit_func,
    'good bye': exit_func,
    'hello': hello_func,
    'phone': phone_func,
    'remove': remove_func,
    'show all': show_func
}


ONE_WORD_COMMANDS = ('add', 'change', 'close', 'delete', 'exit', 'hello', 'phone', 'remove')
TWO_WORDS_COMMANDS = ('good bye', 'show all')


def get_handler(command):
    return COMMANDS[command]


def main():

    while True:
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
            print(f'The "{command}" command is wrong! The allowable commands are {", ".join(ONE_WORD_COMMANDS)}.')
            continue
        
        handler = get_handler(command)
        print(handler(command_line))
        if handler is exit_func:
            break

if __name__ == '__main__':
    main()
