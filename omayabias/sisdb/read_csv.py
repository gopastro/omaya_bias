import pandas as pd
from datamodel import GelPack, SISDimensions

def load_csv(filename):
    df = pd.read_csv(filename)
    for i, row in df.iterrows():
        row = row.where((pd.notnull(row)), None)
        gpquery = GelPack.select().where(GelPack.description==row['GelPak'])
        if gpquery.exists():
            gp = gpquery.get()
        else:
            gp = GelPack(description=row['GelPak'])
            gp.save()
        sisd = SISDimensions(gelpack=gp,
                             sis2letter=row['SIS2Letter'],
                             sisrowcol=row['SISRowCol'],
                             gelpack_label=row['GelPak RowColID'],
                             width1=row['width1'],
                             width2=row['width2'],
                             leftheight=row['leftheight'],
                             middleheight=row['middleheight'],
                             rightheight=row['rightheight'])
        sisd.save()
        print "Done with %d rows" % i

def update_from_csv(filename):
    df = pd.read_csv(filename)
    for i, row in df.iterrows():
        row = row.where((pd.notnull(row)), None)
        gpquery = GelPack.select().where(GelPack.description==row['GelPak'])
        if gpquery.exists():
            gp = gpquery.get()
        else:
            gp = GelPack(description=row['GelPak'])
            gp.save()
        query = SISDimensions.select().where(SISDimensions.gelpack==gp,
                                             SISDimensions.sis2letter==row['SIS2Letter'],
                                             SISDimensions.sisrowcol==row['SISRowCol'],
                                             SISDimensions.gelpack_label==row['GelPak RowColID'])
        if query.exists():
            sisd = query.get()
            sisd.width1 = row['width1']
            sisd.width2 = row['width2']
            if row['leftheight'] is not None:
                sisd.leftheight = row['leftheight']
            if row['middleheight'] is not None:                
                sisd.middleheight = row['middleheight']
            if row['rightheight'] is not None:                                
                sisd.rightheight = row['rightheight']
            sisd.save()
            print "Updating existing SISDimensions: %s" % sisd.id
        else:
            sisd = SISDimensions(gelpack=gp,
                                 sis2letter=row['SIS2Letter'],
                                 sisrowcol=row['SISRowCol'],
                                 gelpack_label=row['GelPak RowColID'],
                                 width1=row['width1'],
                                 width2=row['width2'],
                                 leftheight=row['leftheight'],
                                 middleheight=row['middleheight'],
                                 rightheight=row['rightheight'])
            sisd.save()
            print "Created new SISDimensions: %s" % sisd.id
        print "Done with %d rows" % i
        

                             
