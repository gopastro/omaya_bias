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
    width1 = FloatField(null=True)
    width2 = FloatField(null=True)
    leftheight = FloatField(null=True)
    middleheight = FloatField(null=True)
    rightheight = FloatField(null=True)
    create_time = DateTimeField(default=datetime.datetime.now)    

    class Meta:
        indexes = (
            # creates a unique on the 3 items
            (('gelpack', 'sis2letter', 'sisrowcol', 'gelpack_label'), True),
            )
        

class IVCurveFile(BaseModel):
    sis = ForeignKeyField(SISDimensions)
    filename = CharField()
    measured_time = DateTimeField()
    create_time = DateTimeField(default=datetime.datetime.now)    
    resistance = FloatField(null=True)
    resistance_error = FloatField(null=True)
    slope = FloatField(null=True)
    slope_error = FloatField(null=True)
    intercept = FloatField(null=True)
    intercept_error = FloatField(null=True)
    
    
class Temperature(BaseModel):
    temp1 = FloatField(null=True)
    temp2 = FloatField(null=True)
    temp3 = FloatField(null=True)
    temp4 = FloatField(null=True)
    temp5 = FloatField(null=True)
    temp6 = FloatField(null=True)
    temp7 = FloatField(null=True)
    temp8 = FloatField(null=True)
    create_time = DateTimeField(default=datetime.datetime.now)        
    
def create_tables():
    db.create_tables([GelPack,
                      SISDimensions,
                      IVCurveFile,
                      Temperature,
                      ])

def drop_tables():
    db.drop_tables([GelPack,
                    SISDimensions,
                    IVCurveFile,
                    Temperature
                    ])


                    
