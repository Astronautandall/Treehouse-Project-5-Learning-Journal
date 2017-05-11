import datetime

from flask_bcrypt import generate_password_hash, check_password_hash
from flask_login import UserMixin
from slugify import slugify
from peewee import *


DATABASE = SqliteDatabase('lj.db')


class BaseModel(Model):
    class Meta:
        database = DATABASE


class User(UserMixin, BaseModel):
    email = CharField(unique=True)
    password = CharField(max_length=100)

    @classmethod
    def create_user(cls, email, password):

        try:
            with DATABASE.transaction():
                cls.create(
                    email=email,
                    password=generate_password_hash(password)
                )
        except IntegrityError:
            raise ValueError("User already exists")


class Entry(BaseModel):
    title = CharField()
    slug = CharField()
    date = DateTimeField(default=datetime.datetime.now)
    time_spent = CharField()
    what_i_learned = TextField()
    sources_to_remember = TextField()

    @classmethod
    def create_entry(cls, **kwargs):

        new_entry = cls.create(
            title=kwargs['title'],
            slug=slugify(kwargs['title']),
            date=kwargs['date'],
            time_spent=kwargs['time_spent'],
            what_i_learned=kwargs['what_i_learned'],
            sources_to_remember=kwargs['sources_to_remember']
        )

        for tag in kwargs['tags'].split(','):
            tag, created = Tag.get_or_create(tag=tag.strip())
            EntryTag.get_or_create(id_entry=new_entry.id, id_tag=tag.id)

    class Meta:
        database = DATABASE


class Tag(BaseModel):
    tag = CharField()


class EntryTag(BaseModel):
    id_entry = ForeignKeyField(Entry)
    id_tag = ForeignKeyField(Tag)

    @classmethod
    def get_entry_tags(cls, id_entry):
        return (
            Tag
            .select(Tag)
            .join(cls)
            .where(
                cls.id_entry == id_entry
            )
        )


def initialize():
    DATABASE.connect()
    DATABASE.create_tables([User, Entry, Tag, EntryTag], safe=True)
    DATABASE.close()
