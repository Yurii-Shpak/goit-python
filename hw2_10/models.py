from mongoengine import Document
from mongoengine.fields import ListField, StringField, SequenceField


class Contact(Document):
    id = SequenceField(primary_key=True)
    name = StringField(required=True)
    address = StringField(required=False)
    email = StringField(required=False)
    birthday = StringField(required=False)
    phones = ListField(required=False)
