###############################################################################################
# app_flask_session.py 1.0 08/20/2018                                     				      #
# Created By Puneeth Prashanth G To Perform and Full fill all the Requerments                 #
# which are mentioned Below                                                                   #
# 1)1.	Develop a REST API for representing Meta-Data with end points (GET,                   #
# POST, PUT, DELETE etc.                                                                      #
# For example, GET on /api/v1/location returns all location objects                           #
#   a.	/api/v1/location,                                                                     #
#   b.	/api/v1/location/{location_id}/department                                             #
#   c.	/api/v1/location/{location_id}/department/{department_id}/category                    #
#   d.	/api/v1/location/{location_id}/department/{department_id}/category/                   #
#   {category_id}/subcategory                                                                 #
#   e.	/api/v1/location/{location_id}/department/{department_id}/category/                   #
#   {category_id}/subcategory/{subcategory_id}                                                #
#                                                                                             #
#  2)Implement an authentication mechanism for the UI (username/password)                     #
#    and API (Basic Auth) - Bonus points if you can                                           #
#     demonstrate OpenIDConnect, JWT, OAuth2 can demonstrate OpenIDConnect,                   #
#      JWT, OAuth2                                                                            #
#                                                                                             #
#  3)Persist the data in your favorite DB - relational or non-relational                      #
#   (You are expected to install, configure,                                                  #
#    populate the DB). You may feel free to qualify object representations                    #
#   with additional attributes to enhance                                                     #
#    modeling (For e.g. Location object attributes = locationid, location description)        #
#                                                                                             #
#  4)In your chosen web front-end framework, develop a web-based UI, that                     #
#   the user can interact with and perform                                                    #
#   CRUD (create, read, update, delete)  operations on the data (The calls                    #
#   should go through API layer built in step 1).                                             #
###############################################################################################
from flask import Flask, request, session, render_template, redirect, g, url_for
import os
import re
import psycopg2


app=Flask(__name__)
path = os.path.abspath(os.path.join(os.path.dirname(__file__)))
app.config.from_pyfile(os.path.join(path, 'config.py'))
app.secret_key=os.urandom(24)

# configuration initialization
get_locatoin_url = app.config["GETDOCS_LOCATION_URL"]
get_locatoin_department_url = app.config["GETDOCS_LOCATION_DEPARTMENT_URL"]
get_locatoin_department_category_url = app.config["GETDOCS_LOCATION_DEPARTM" \
                                                  "ENT_CATEGORY_URL"]
get_locatoin_department_category_subcategory_url = app.config["GETDOCS_LOCAT" \
                                   "ION_DEPARTMENT_CATEGORY_SUBCATEGORY_URL"]
create_url=app.config["CREATE_VALUES_LDCS"]
delete_url=app.config["DELETE_VALUES_LDCS"]
update_url=app.config["UPDATE_VALUES_LDCS"]
compare_url=app.config["COMPARE_META_SLDCS"]

# Establishing the connection_parameters to connect to DB.
connection_parameters = { 'user ': app.config["USER"],
                          'password': app.config["PASSWORD"],
                          'host': app.config["HOST"],
                          'database' : app.config["DATABASE"] }

# This method is the called in all the Read functionality’s of
def single_db_connection(*args):
    """
    This Method will connect to DB and retrive all the data from LSCS table using
    location as the query parameter.
    and loads the data to Dictionary and returns it back
    :param args: Location(string)
    :return: LDCS_list (Dictionary)
    """
    location=args[0]

    # Establising DB connection
    connection= psycopg2.connect(**connection_parameters)

    # query to get all teh detailes with location
    select_all_LDCS_statment=f'select seq_no,location_disc, department,' \
                             f'category ,subcategory from ldcs where ' \
         f'lower(location_disc) = lower(\'{location}\') ;'
    cursor = connection.cursor()

    # connect to DB and executes the above sql
    try:
               cursor.execute(select_all_LDCS_statment)
               location_department_category_subcategorys = cursor.fetchall()
               location_department_category_subcategorys_select_dict={}
               j=1
               for x in range(len(location_department_category_subcategorys)):
                  ldcs_list=[]
                  for i in location_department_category_subcategorys[x]:
                      ldcs_list.append(i)
                  j+=1
                  load_dict={j:ldcs_list}
                  location_department_category_subcategorys_select_dict.update(load_dict)
               print(location_department_category_subcategorys_select_dict)
               return location_department_category_subcategorys_select_dict

    # Any exception will be loaded to e.
    except Exception as e:
               print (f'Error while select Data from ldcs table:{e}')
               print(f'failed in executing {select_all_LDCS_statment}')
               return ["Error",e]

    # This block will make process to disconnect from DB.
    finally:
               if(connection):
                 connection.commit()
                 cursor.close()
                 connection.close()

# This will build the query for deletion of values from data
def query_builder(*args):
    """
    This Method will take the take the parameters Dictionary as the input
    parameter and builds up final query based on the list of parameters
    in parameter dict.
    :param args:(parameters) its a Dictionary Argument which holdes all
    the 'L','D','C','S' values
    :return:query(string) final query.
    """
    parameters={}
    parameters=args[0]
    query=f''
    if parameters['location'] !='':
        location=parameters['location']
        query=query+f'location_disc=\'{location}\''
    if parameters['department'] !='' and parameters['location'] !='' :
        department=parameters['department']
        query=query+f'and department=\'{department}\''
    elif parameters['department'] !='' :
        department=parameters['department']
        query=query+f'department=\'{department}\''
    if parameters['category'] !=''  and (parameters['department'] !=''  or
                                         parameters['location'] !=''):
        category=parameters['category']
        query=query+f'and category=\'{category}\''
    elif parameters['category'] !='' :
        department=parameters['category']
        query=query+f'category=\'{category}\''
    if parameters['subcategory'] !=''  and (parameters['category'] !=''  or
                                            parameters['department'] !=''  or
                                            parameters['location'] !='' ):
        subcategory=parameters['subcategory']
        query=query+f'and subcategory=\'{subcategory}\''
    elif parameters['subcategory'] !='' :
        department=parameters['subcategory']
        query=query+f'subcategory=\'{subcategory}\''
    return query

##############################FLASK CONNECTIONS STARTS HERE #######################

# this method is to root to home page.
@app.route('/', methods=['POST','GET'])
def index() :
    """
       This method will establish a (/) end point and when ever '/'  is called it
       will perform what ever defined in the below method. Basicaly if the user
       is loged in this method will redirect to '/protected' else back to  '/home'
    :return: redirects to home or protected
    """

    if g.user:
        return redirect(url_for ('protected'))

    return render_template('home.html')

@app.route('/login', methods=['POST','GET'])
def login() :
    """
        This method will establish a (/login) end point and when ever '/login'
        is called it will perform what ever defined in the below method.
        Basicaly this will redirect to login page takes the username and password
        as connect to DB abd validates the user detailes and redirects to /protected
        else back to /login page.
    :return: redirect to both /login and /protected based on sityation
    """
    if request.method == 'POST':
        session.pop('user',None)
        connection= psycopg2.connect(**connection_parameters)
        user=request.form['username']
        password=request.form['password']

        # this statement will validate the user who tries to login to site.
        select_user_statment=f'select username from users where username = \'{user}\' and ' \
                        f'password =crypt( \'{password}\',password)'
        cursor = connection.cursor()

        #Connect to DB and executes the above sql
        try:
            cursor.execute(select_user_statment)
            record = cursor.fetchone()

        #Any exception will be loaded to e.
        except:
            print (f'Error while select  Data to users table')
            print(f'failed in executing {select_user_statment}')
            return render_template('home.html')

        # This block will make process to disconnect from DB.
        finally:
               if(connection):
                    connection.commit()
                    cursor.close()
                    connection.close()

        # condition to validate the select_user_statment
        if request.form['username']==record[0]:
            session['user']=request.form['username']
            return redirect(url_for ('protected'))
    return render_template('/Login_temp/login.html')

@app.route('/register', methods=['POST','GET'])
def register() :
    """
    This method will establish a (/register) end point and when ever '/register'
    is called it will perform what ever defined in the below method. Basically
    this will Create a New user by taking all the required detailes and make an
    entry in DB. after successfull registeration user will redirect to /protected
    :return: registration template / protected template
    """
    if request.method == 'POST':
        session.pop('user',None)
        connection= psycopg2.connect(**connection_parameters)
        if request.form['password']== request.form['password2']:
            user=request.form['username']
            password=request.form['password']
            #this insert statement is to create an user
            insert_statment=f'insert into users (username, password) values' \
                            f'(\'{user}\',crypt(\'{password}\',gen_salt(\'bf\', 8)))'

            # the below try will connect to DB.
            try:
                cursor = connection.cursor()
                cursor.execute(insert_statment)
                connection.commit()
                cursor.close()

            # any exceptions in the above will be captured here
            except:
                print (f'Error while Inserting Data to users table')
                print(f'failed in executing {insert_statment}')
                return render_template('home.html')
            connection.close()
            session['user']=request.form['username']
            return redirect(url_for ('protected'))

    # initial render and is non of the above works again render the same
    return render_template('/Login_temp/Register.html')


# this is the protected page where every successfull login or registration will be
# rooted to
@app.route('/protected')
def protected():
    """
    This method will establish a (/protected) end point and when ever
    '/protected'  is called it will perform what ever defined in the
    below method. This is a redirect method, every success full login
    or registration and home will be redirected to this page from this
    page User will Have access to all the CRUD operations and compare meta too.
    :return: home page
    """
    if g.user:
        return render_template('protected.html')
    return render_template('home.html')

# this methos is to update the data to DB according to sequence no.
@app.route( update_url, methods=['PUT','GET'])
def update():
    """
    This method will establish a (/api/v1/update) end point and when
    ever '/api/v1/update'  is called it will perform what ever defined
    in the below method. The Update method will Accept Both "PUT" (update
    the record LDCS table) and "GET" {to Render teh update form} Methods. This
    method will Display the Update result
    :return: Renders update template
    """

    # loads all the requested data to parameters in a dict format.
    parameters=request.args.to_dict()
    if len(parameters)== 0:
        return render_template('Data/update.html')
    else:
        seq_no=parameters['seq_no']

        # Calling the query_builder method to build the where clause
        query=query_builder(parameters)
        query=re.sub(r'and',r',',query)
        print(query)
        connection= psycopg2.connect(**connection_parameters)
        update_statment=f''
        if query != '':

              # update statment is getting build accoring to query.
              update_statment=f'UPDATE public.ldcs SET {query} where seq_no={seq_no};'
              cursor = connection.cursor()
        else:
              error=f'There is an issue values which you have entered please check'
              return render_template('Data/update.html',error=error )

        # the below try will connect to DB.
        try:
               cursor.execute(update_statment)
               connection.commit()
               message=f'Updated the {query} data Successfully '
               return render_template('Data/update.html',message=message)

        # any exception of above will be routed  to below exception.
        except Exception as e:
               print (f'Error while updating  Data to ldcs table:{e}')
               print(f'failed in executing {update_statment}')
               return render_template('Data/update.html',error=f'Please check the '
                              f'location and Department category and subcategory ' )
        # Disconnection from DB
        finally:
               if(connection):
                 cursor.close()
                 connection.close()

    # initial render and is non of the above works again render the same
    return render_template('Data/update.html')

# this method Delete the data from DB
@app.route( delete_url, methods=['DELETE','GET'])
def delete():
    """
        This method will establish a (/api/v1/delete) end point and when ever
        '/api/v1/delete'  is called it will perform what ever defined in the
        below method. The delete method will Accept Both "DELETE" (to Delete
        the record LDCS table) and "GET" {to Render the delete form} Methods. This
        method will Display the Delete query

    :return: renders delete template
    """

    # loads all the requested data to parameters in a dict format.
    parameters=request.args.to_dict()
    if len(parameters)== 0:
        return render_template('Data/delete.html')
    else:
        query=query_builder(parameters)
        print(f'query:{query} ')
        connection= psycopg2.connect(**connection_parameters)
        if query !=''  :

              # query to delete data from DB
              delete_statment=f'DELETE FROM public.ldcs WHERE {query}'
              cursor = connection.cursor()
              print(f'delete_statment : {delete_statment}')
        else:
              error=f'There is an issue deletion records patter entered Please ' \
                    f'see the give example '
              return render_template('Data/delete.html',error=error )

        # the below try will connect to DB and execute the delete_statment.
        try:
               cursor.execute(delete_statment)
               connection.commit()
               print(f'Deleted rows {cursor.rowcount} ')
               if (cursor.rowcount == 0):
                   return render_template('Data/delete.html',inval_message=f'Values '
                   f'of {query} are not valid, Please Check ')
               return render_template('Data/delete.html',message=f'Deleted the {query} '
                                                                 f'data successfully ')

        # any exception of above will be routed  to below exception.
        except Exception as e:
               print (f'Error while Deleting  Data to ldcs table:{e}')
               print(f'failed in executing {delete_statment}')
               return render_template('Data/delete.html',error=f'Please check pattern once,'
                                                    f' kindly see the give example ' )

        # Disconnection from DB
        finally:
               if(connection):
                 cursor.close()
                 connection.close()
    # initial render and is non of the above works again render the same
    return render_template('Data/delete.html')



# this method is to create the
@app.route( create_url, methods=['POST','GET'])
def create():
    """
    This method will establish a (/api/v1/create) end point and when ever '/api/
    v1/create'  is called it will perform what ever defined in the below method.
    The dreate method will Accept Both "POST" (to insert  the record LDCS table)
    and "GET" {to Render the create form} Methods. This method will Display the
    inserted  records.

    :return: renders the create template
    """
    if request.method == 'POST':
        # takes the request form as input value
        vals=request.form.to_dict()
        location=vals['location']
        department=vals['department']
        category=vals['category']
        subcategory=vals['subcategory']
        print(f'location:{location} and department:{department} and category:'
              f'{category} and  subcategory:{subcategory}')
        connection= psycopg2.connect(**connection_parameters)
        insert_statment=f''
        if location !='' or department !='' or category !='' or subcategory !='':
              # this is the insert statement to create data into DB
              insert_statment=f'INSERT INTO public.ldcs (location_disc,department,' \
                              f'category,subcategory) ' \
                              f'VALUES (\'{location}\',\'{department}\',\'{category}\',' \
                              f'\'{subcategory}\');'
              cursor = connection.cursor()
        else:
              error=f'There is an issue in the location and departmrnt and ' \
                    f'category and subcategory one of them or both are null'
              return render_template('Data/create.html',error=error )

        # the below try will connect to DB and execute the insert_statement.
        try:
               cursor.execute(insert_statment)
               connection.commit()
               filtered_dict={1:[location,department,category,subcategory]}
               return render_template('Data/create.html',inserted_data=filtered_dict)

        # any exception of above will be routed  to below exception.
        except Exception as e:
               print (f'Error while inserting Data to ldcs table:{e}')
               print(f'failed in executing {insert_statment}')
               return render_template('Data/create.html',error=f'Please check '
               f'the location and Department category and subcategory ' )

        # Disconnection from DB
        finally:
               if(connection):
                 cursor.close()
                 connection.close()

    # initial render and is non of the above works again render the same
    return render_template('Data/create.html')


#####################All Below are Read End Points###########

#this method will return all the details of LDCS accordingly.
@app.route( get_locatoin_department_category_subcategory_url ,
            methods=['POST','GET'])
def Subcategory() :
    """
    This method will establish a (/api/v1/location/department/category/subcategory)
    end point and when ever '//api/v1/location/department/category/subcategory' is
    called it will perform what ever defined in the below method. Subcategory Methods
    will take all the 4 'L','D','C','S'  values and will query the out the data and
    Display the data set in a table format
    :return: subcategory.html
    """
    if request.method == 'GET':

           # loads all the requested data to parameters in a dict format.
           parameters=request.args.to_dict()
           print(parameters)

           # if there are zero parameters are passed in then it will return back to subcategory
           if len(parameters)== 0:
               return render_template('Data/subcategory.html')
           location=parameters['location']
           department=parameters['department']
           category=parameters['category']
           subcategory=parameters['subcategory']

           if location is not None and department is not None and \
                   category is not None and subcategory is not None:
              print(f'location:{location} & {department} & {category}'
                    f' & {subcategory}')
              location_department_category_subcategorys_dict=\
                  single_db_connection(location)
              print(type(location_department_category_subcategorys_dict))
              if type(location_department_category_subcategorys_dict) is dict:
                  filtered_dict={}
                  i=0
                  print(f'{location_department_category_subcategorys_dict}')
                  for key,value in location_department_category_subcategorys_dict.items():
                      print(f'{value[1]}=={location} and {value[2]}=={department}'
                            f' and {value[3]}=={category} '
                            f'and {value[4]}=={subcategory}')
                      if value[1]==location and value[2]==department and \
                              value[3]==category and value[4]==subcategory:
                          filtered_dict={i:value}
                          i+=1
                      else:
                          pass

                  print(filtered_dict)
                  if filtered_dict:
                      pass

                  # if there is invalid data sent to this method then it will raise a
                  # warning back to subcategory.html
                  else:
                      return render_template('Data/subcategory.html',inval_message=
                      f'Please check the values you have passed they seems invalied' )
                  try:
                    return render_template('Data/subcategory.html',
                        location_department_category_subcategorys=filtered_dict)
                  except Exception as e:
                    print (f'Error while Rendering page:{e}')
                    return render_template('Data/subcategory.html',error=f'Please check '
                    f'the location and Department or category seems worng {location} and '
                    f'{department}' )
              else:
                  print (f'Error while selecting data from LDCS:'
                         f'{location_department_category_subcategorys_dict[1]}')
                  return render_template('Data/subcategory.html',error=f'Please check the'
                  f' location and Department or category seems worng {location} and '
                                                                       f'{department}' )

    # initial render and is non of the above works again render the same
    return render_template('Data/subcategory.html')




# this method will return all the details of LDC accordingly.
@app.route( get_locatoin_department_category_url , methods=['POST','GET'])
def Category() :
    """
    This method will establish a (/api/v1/location/department/category/) end
    point and when ever '/api/v1/location/department/category/' is called it
    will perform what ever defined in the below method. Category Methods will
    take all the 4 'L','D','C'  values and will query the out the data and
    Display the data set in a table format

    :return:renders category templete
    """
    if request.method == 'GET':
           # loads all the requested data to parameters in a dict format.
           parameters=request.args.to_dict()

           # if there are zero parameters are passed in then it will return back to subcategory
           if len(parameters)== 0:
               return render_template('Data/category.html')

           location=parameters['location']
           department=parameters['department']
           category=parameters['category']
           print(f'location:{location} and department:{department} and  '
                 f'category :{category}')
           if location is not None and department is not None and category is not None :
              location_department_categorys_dict=single_db_connection(location)
              print(type(location_department_categorys_dict))
              if type(location_department_categorys_dict) is dict:
                  filtered_dict={}
                  i=0
                  print(f'{location_department_categorys_dict}')
                  for key,value in location_department_categorys_dict.items():
                      print(f'{value[1]}=={location} and {value[2]}=={department} '
                            f'and {value[3]}=={category} ')
                      if value[1]==location and value[2]==department and \
                              value[3]==category :
                          filtered_dict={i:value}
                          i+=1
                      else:
                          pass
                  print(filtered_dict)

                  if filtered_dict:
                      pass
                  else:

                  # if there is invalid data sent to this method then it will raise a
                  # warning back to category.html
                      return render_template('Data/category.html',inval_message=
                      f'Please check the values you have passed they seems invalied' )
                  try:
                    return render_template('Data/category.html',
                                         location_department_categorys=filtered_dict)
                  except Exception as e:
                    print (f'Error while Rendering page:{e}')
                    return render_template('Data/category.html',error=f'Please check '
                    f'the location and Department or category seems worng {location}'
                    f' and {department}' )
              else:
                  print (f'Error while selecting data from '
                         f'LDCS:{location_department_categorys_dict[1]}')
                  return render_template('Data/category.html',error=f'Please check the'
                  f' location and Department or category seems worng {location} and '
                                                                    f'{department}' )

    # initial render and is non of the above works again render the same
    return render_template('Data/category.html')



# this method will return all the details of LD accordingly.
@app.route('/api/v1/location/department' , methods=['POST','GET'])
def Department() :
    """
    This method will establish a (/api/v1/location/department//) end point and when
    ever '/api/v1/location/department/' is called it will perform what ever defined
    in the below method. Department Methods will take all the 4 'L','D' values and
    will "GET" query the out the data and Display the data set in a table format

    :return:renders department templete

    """
    if request.method == 'GET':

        # loads all the requested data to parameters in a dict format.
           parameters=request.args.to_dict()

         # if there are zero parameters are passed in then it will return back to department
           if len(parameters)== 0:
               return render_template('Data/department.html')

           location=parameters['location']
           department=parameters['department']
           print(f'location:{location} and department:{department} ')
           connection= psycopg2.connect(**connection_parameters)
           if location is not None and department is not None:
              print(f'location:{location} & {department} ')
              location_department_dict=single_db_connection(location)
              print(type(location_department_dict))
              if type(location_department_dict) is dict:
                  filtered_dict={}
                  i=0
                  print(f'{location_department_dict}')
                  for key,value in location_department_dict.items():
                      print(f'{value[1]}=={location} and {value[2]}=={department}')
                      if value[1]==location and value[2]==department :
                          filtered_dict={i:value}
                          #i+=1
                          break
                      else:
                          pass

                  print(filtered_dict)
                  if filtered_dict:
                      pass
                  else:
                      # if there is invalid data sent to this method then it will raise a
                      # warning back to category.html
                      return render_template('Data/department.html',inval_message=
                      f'Please check the values you have passed they seems invalied' )

                  try:
                    return render_template('Data/department.html',
                                           location_departments=filtered_dict)
                  except Exception as e:
                    print (f'Error while Rendering page:{e}')
                    return render_template('Data/department.html',error=f'Please check'
                f' the location and Department seems worng {location} and {department}' )
              else:
                  print (f'Error while selecting data from LDCS:{location_department_dict[1]}')
                  return render_template('Data/category.html',error=f'Please check the '
                                                                    f'location and Department '
                                                                    f'or categor seems worng ')

    # initial render and is non of the above works again render the same
    return render_template('Data/department.html')

# this method will return all the details of L accordingly.
@app.route(get_locatoin_url , methods=['POST','GET'])
def location() :
    """
    This method will establish a (/api/v1/location/) end point and when ever
    '/api/v1/location/' is called it will perform what ever defined in the
    below method. Department Methods will take omly one  'L' values and will
    "GET" query the out the data and Display the data set in a table format

    :return:renders location templete

    """
    if request.method == 'GET':

        # loads all the requested data to parameters in a dict format.
        parameters=request.args.to_dict()

        # if there are zero parameters are passed in then it will return back to location
        if len(parameters)== 0:
            return render_template('Data/location.html')

        connection= psycopg2.connect(**connection_parameters)
        location_select_statment=f''
        location=parameters['location']
        print(f'location:{location}')
        if location is not None:
            print(f'location:{location}  ')
            location_dict=single_db_connection(location)
            print(type(location_dict))
            if type(location_dict) is dict:
                  filtered_dict={}
                  i=1
                  print(f'{location_dict}')
                  for key,value in location_dict.items():
                      print(f'{value[1]}=={location}  ')
                      if value[1]==location :
                          filtered_dict={i:value}
                          #i+=1
                      else:
                          pass
                  print(filtered_dict)
                  if filtered_dict:
                      pass
                  else:

                      # if there is invalid data sent to this method then it will raise a
                      # warning back to category.html
                      return render_template('Data/location.html',inval_message=
                      f'Please check the values you have passed they seems invalied' )

                  try:
                    return render_template('Data/location.html',locations=filtered_dict)
                  except Exception as e:
                    print (f'Error while Rendering page:{e}')
                    return render_template('Data/location.html',error=
                    f'Please check the location seems worng {location} ' )
            else:
                  print (f'Error while selecting data from LDCS:{location_dict[1]}')
                  return render_template('Data/location.html',error=
                  f'Please check the location seems worng {location} ' )

    # initial render and is non of the above works again render the same
    return render_template('Data/location.html')


# this method will take the set of (meta)data from compare page and
# will segregate them and process.
@app.route(compare_url , methods=['POST','GET'])
def Compare() :
    """
    This method will establish a (/api/v1/compare_meta) end point
    and when ever '/api/v1/compare_meta/' is called it will perform
    what ever defined in the below method. Compare Methods will take
    1 or multiple meta values and compare the data with sku_ldcs table
    and will match results data set will be displayed

    :return:renders compare_meta template
    """
    print(request.form)
    if request.method == "POST":

        # loads all the requested data to parameters in a dict format.
        parameters=request.form.to_dict()

        # empty list which will loaded with all the set of metas to compare.
        ldcs_list=[]
        for key,value in parameters.items():
            replace_str=re.sub(r"\r\n", r",", value)
            print(replace_str)
            ldcs_list=list(replace_str.split(","))
            print(ldcs_list)
        j=0
        k=1
        parameters={}
        ldcs_splited_list=[]

        # this condition is to conform the each single meta contains 4 vales
        if len(ldcs_list)%4 == 0:
            for i in ldcs_list:
                ldcs_splited_list.append(i)
                j+=1
                if j==4:
                    parameters1={k:ldcs_splited_list}
                    parameters.update(parameters1)
                    j=0;k+=1
                    ldcs_splited_list=[]
        else:
            print (f'Error in No of inpuits please check')
            return render_template('Data/compare_meta.html',error=f'Error in '
                                             f'No of inpuits please check' )

        connection= psycopg2.connect(**connection_parameters)
        compare_statment=f''
        location=f'';department=f'';category=f'';subcategory=f''

        # building up the all set of metas to a single query.
        for key,value in parameters.items():
                if key > 1:
                    location=location + f'\', \'{value[0]}'
                    department=department + f'\', \'{value[1]}'
                    category=category + f'\', \'{value[2]}'
                    subcategory=subcategory + f'\', \'{value[3]}'
                if key == 1:
                    location = f'{value[0]}'
                    location=location.strip()
                    department = f'{value[1]}'
                    department=department.strip()
                    category = f'{value[2]}'
                    category=category.strip()
                    subcategory = f'{value[3]}'
                    subcategory=subcategory.strip()

        print(f'location={location}department={department}category={category}'
              f'subcategory={subcategory}')
        compare_statmen=f'select a.* from sku_ldcs a , ldcs b ' \
                        f'where a.location_disc=b.location_disc and ' \
                        f'a.department=b.department and ' \
                        f'a.category=b.category and ' \
                        f'a.subcategory=b.subcategory and ' \
                        f'a.location_disc in(\'{location}\')' \
                        f' and a.department in(\'{department}\') ' \
                        f'and a.category in(\'{category}\')' \
                        f'and a.subcategory in(\'{subcategory}\');'
        print(f'compare_statmen:{compare_statmen}')
        cursor = connection.cursor()

        # the below try will connect to DB and execute the compare_statmen.
        try:
            cursor.execute(compare_statmen)
            compare_result = cursor.fetchall()
            compare_result_dict={}
            j=1
            for x in range(len(compare_result)):
                  skldcs_list=[]
                  for i in compare_result[x]:
                      skldcs_list.append(i)
                  j+=1
                  load_dict={j:skldcs_list}
                  compare_result_dict.update(load_dict)
            print(f'compare_result_dict:{compare_result_dict}')
            return render_template('Data/compare_meta.html',compare_results=
            compare_result_dict)

        # any exception of above will be routed  to below exception.
        except Exception as e:
            print (f'Error while select Data from skldcs table:{e}')
            print(f'failed in executing {compare_statmen}')
            return render_template('Data/compare_meta.html',error=
            f'Please check the Detailes again ' )

        # Closing all the connections
        finally:
            if(connection):
                connection.commit()
                cursor.close()
                connection.close()

    return render_template('Data/compare_meta.html')




# this method gets executed before every request.
@app.before_request
def before_request():
    """
    This is a predefined request which invokes  before any request to
    validate the session user login status.
    :return:
    """
    g.user=None
    if 'user' in session:
        g.user=session['user']


@app.route('/checksession')
def checksession():
    """
    This method will establish a (/checksession) end point and when ever
    '/checksession'
    is called it will perform what ever defined in the below method.
     This method for developer use to check the session status.
    :return:
    """
    if 'user' in session:
        return session['user']

    return 'No a valied Session'

# this method is a logout method.
@app.route('/logout')
def dropsession():
    """
    This method will establish a (/logout) end point and when ever '/logout'
    is called it will perform what ever defined in the below method.
     This method will root to logout page and will remove the user from session .
    :return:
    """
    session.pop('user',None)

    return render_template('/Login_temp/logout.html')

######MAIN Starts here#############

if __name__ == '__main__':

    app.run(debug=True)

