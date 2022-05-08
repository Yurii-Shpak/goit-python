from abc import abstractmethod, ABC
import json
import pickle


class SerializationInterface(ABC):

    @abstractmethod
    def save_to_json_file(self, data, file):
        pass

    @abstractmethod
    def load_from_json_file(self, file):
        pass


class Serialize(SerializationInterface):

    def save_to_json_file(self, data, file):
        data = json.dumps(data).encode('utf-8')
        with open(file, 'wb') as fh:
            pickle.dump(data, fh)

    def load_from_json_file(self, file):
        with open(file, 'rb') as fh:
            return pickle.load(fh).decode('utf-8')


class_counter = 0


class Meta(type):

    def __init__(cls, name, bases, attrs):
        global class_counter
        super().__init__(name, bases, attrs)
        cls.class_number = class_counter
        class_counter += 1


class Cls1(metaclass=Meta):

    def __init__(self, data):

        self.data = data


class Cls2(metaclass=Meta):

    def __init__(self, data):

        self.data = data


s = Serialize()
s.save_to_json_file({'Name': 'Yurii Shpak', 'Age': 47}, 'dict.bin')
print(s.load_from_json_file('dict.bin'))
s.save_to_json_file('Name: Yurii Shpak, Age: 47', 'str.bin')
print(s.load_from_json_file('str.bin'))
s.save_to_json_file([1, 2, 3, 4, 5], 'list.bin')
print(s.load_from_json_file('list.bin'))

assert (Cls1.class_number, Cls2.class_number) == (0, 1)
a, b = Cls1(''), Cls2('')
assert (a.class_number, b.class_number) == (0, 1)
