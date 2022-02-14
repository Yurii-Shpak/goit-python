contacts = {}

def input_error(func):

    def inner(command_line):
        
        try:
            result = func(command_line)
        except:
            if func.__name__ in ('add_func', 'change_func'):
                result = f'Give me name and phone, please. Separate them with the space symbol.'
            if func.__name__ == 'phone_func':
                result = 'Enter the name of an existing contact, please.'
                
        return result
    
    return inner


@input_error
def add_func(command_line):

    name, phone = get_name_phone(command_line)
        
    if contacts.get(name):
        result = f'Record for the name "{name}" exists already. Use some other name, please.'
    else:
        contacts[name] = phone
        result = f'Record for {name} {phone} is added.'

    return result


@input_error
def change_func(command_line):

    name, phone = get_name_phone(command_line)
    
    if contacts.get(name):
        contacts[name] = phone
        result = f'Record for "{name}" is updated with the phone number {phone}.'
    else:
        result = f'Record for the name "{name}" does not exists. Enter the correct name, please.'

    return result


@input_error
def exit_func(command_line):

    return 'Good bye!'


def get_name_phone(command_line):
    
    # Имя может состоять из нескольких слов
    if len(command_line) > 1:
        phone = command_line.pop(len(command_line) - 1).strip()  # Выкусываем номер телефона
        name = ' '.join(command_line).strip()

    return name, phone


@input_error
def hello_func(command_line):

    return 'How can I help you?'


@input_error
def phone_func(command_line):

    name = ' '.join(command_line).strip()
    if name:
        return contacts[name]
    else:
        return 'Give me the name of a contact, please.'


@input_error
def show_func(command_line):
    result = ''
    for key, value in contacts.items():
        result += f'{key} {value}\n'
    return result


COMMANDS = {
    'add': add_func,
    'change': change_func,
    'close': exit_func,
    'exit': exit_func,
    'good bye': exit_func,
    'hello': hello_func,
    'phone': phone_func,
    'show all': show_func
}

ONE_WORD_COMMANDS = ('hello', 'exit', 'close', 'add', 'change', 'phone')

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
            print(f'The "{command}" command is wrong! The allowable commands are hello, add, change, phone, show all, good bye, close, exit.')
            continue
        
        handler = get_handler(command)
        print(handler(command_line))
        if handler is exit_func:
            break

if __name__ == '__main__':
    main()
