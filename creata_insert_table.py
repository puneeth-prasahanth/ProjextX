#####create_insert_table.py##########################################
# This script will create and insert the data taking from text file.#
#####################################################################

import psycopg2
import re

# These are the which need to be updated by RM team.
connection = psycopg2.connect(user = "postgres",
                                  password = "Puneeth@1",
                                  host = "localhost",
                                  database = "projectx")

try:
    cursor = connection.cursor()
    # Print PostgreSQL Connection properties
    print ( connection.get_dsn_parameters(),"\n")
    # Print PostgreSQL version
    cursor.execute("SELECT version();")
    record = cursor.fetchone()
    print("You are connected to - ", record,"\n")
    Table_statment="CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username varchar(255) unique,password varchar(255))"
    try :
        cursor.execute(Table_statment)
        connection.commit()
        print(f'Created users Table')
    except:
        print (f'Error while creating the users')

    Table_statment2="CREATE TABLE IF NOT EXISTS public.ldcs (seq_no serial NOT NULL, location_disc varchar(355) NOT NULL,	department varchar(355) NOT NULL,	category varchar(355) NOT NULL,	subcategory varchar(355) NOT NULL,	CONSTRAINT ldcs_pkey PRIMARY KEY (seq_no));"
    try:
        cursor.execute(Table_statment2)
        connection.commit()
        print(f'Created ldcs Table')
    except:
        print (f'Error while creating the ldcs')

    Table_statment3="CREATE TABLE IF NOT EXISTS public.sku_ldcs (sku_seq_no serial NOT NULL,sku_name varchar(355) NOT NULL, location_disc varchar(355) NOT NULL,	department varchar(355) NOT NULL,	category varchar(355) NOT NULL,	subcategory varchar(355) NOT NULL,	CONSTRAINT sku_ldcs_pkey PRIMARY KEY (sku_seq_no));"
    try:
        cursor.execute(Table_statment3)
        connection.commit()
        print(f'Created sku_ldcs  Table')
    except:
        print (f'Error while creating the sku_ldcs ')

    cursor.close()
    #connection.close()
    print("PostgreSQL connection is closed")


except (Exception, psycopg2.Error) as error :
    print ("Error while connecting to PostgreSQL", error)




#
#connection.close()
#
#Table_statment2="CREATE TABLE public.ldcs (seq_no serial NOT NULL, location_disc varchar(355) NOT NULL,	department varchar(355) NOT NULL,	category varchar(355) NOT NULL,	subcategory varchar(355) NOT NULL,	CONSTRAINT ldcs_pkey PRIMARY KEY (seq_no));"
##Inserting Data to tables

query=f''
with open('./LDCS.txt', 'r') as fh:
    for i in fh.readlines():
      i=re.sub(r"\n",r"'),",i)
      i=re.sub(r"^",r"('",i)
      query=query+i
    query=query[0:-1]



###########This may or May not work some time it throw DB related errors regarding DB locks
LDCS_insert_statment=f'INSERT INTO public.ldcs (location_disc, department, category, subcategory) ' \
                     f'VALUES {query}'
print(f'LDCS_insert_statment:{LDCS_insert_statment}')
try:
    cursor = connection.cursor()
    cursor.execute(LDCS_insert_statment)
    #connection.commit()
except Exception as e:
    print(f'Failed becouse of {e}')
finally:
    if(connection):
        cursor.close()
        #connection.close()


sku_query=f''
with open('./SKU_LDCS.txt', 'r') as fh:
    for i in fh.readlines():
      i=re.sub(r"\n",r"'),",i)
      i=re.sub(r"^",r"('",i)
      sku_query=sku_query+i
    sku_query=sku_query[0:-1]

SKU_LDCS_insert_statment=f'INSERT INTO public.sku_ldcs (sku_seq_no, sku_name, location_disc, department, category, subcategory) ' \
                     f'VALUES {sku_query}'
print(f'LDCS_insert_statment:{SKU_LDCS_insert_statment}')
try:
    cursor = connection.cursor()
    cursor.execute(SKU_LDCS_insert_statment)
    connection.commit()
except Exception as e:
    print(f'Failed becouse of {e}')
finally:
    if(connection):
        cursor.close()
        connection.close()





