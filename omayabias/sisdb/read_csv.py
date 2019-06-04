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


                             
