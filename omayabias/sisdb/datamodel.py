import datetime
import os
from peewee import *

if os.environ.get('OMAYA_DEBUG'):
    db = SqliteDatabase('omayasis_test.db')
else:
    db = PostgresqlDatabase(os.environ.get('OMAYA_DBNAME', 'omayasisdb'),
            user = os.environ.get('OMAYA_DBUSER', 'omayasis'),
            password = os.environ.get('OMAYA_PASSWORD', 'password'),
            host = os.environ.get('OMAYA_HOST', 'localhost'),
            port = int(os.environ.get('OMAYA_PORT', '5432')),
            )

class BaseModel(Model):
    class Meta:
        database = db

def connect():
    if db.is_closed():
        db.connect()

def close():
    if not db.is_closed():
        db.close()

class GelPack(BaseModel):
    description = CharField()
    height = FloatField(null=True)

class SISDimensions(BaseModel):
    gelpack = ForeignKeyField(GelPack)
    sis2letter = CharField()
    sisrowcol = CharField()
    gelpack_label = CharField() # like A1a
    width1 = FloatField()
    width2 = FloatField()
    
def create_tables():
    db.create_tables([GelPack,
                      SISDimensions,
                      ])

def drop_tables():
    db.drop_tables([GelPack,
                    SISDimensions,
                    ])


                    