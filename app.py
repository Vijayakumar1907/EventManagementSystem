from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import re
import datetime
import pandas as pd

# global length
app = Flask(__name__,template_folder='template')

app.secret_key = 'k'
 
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'function_system'

#jinja extension for loop control
app.jinja_env.add_extension('jinja2.ext.loopcontrols')


mysql = MySQL(app)

date = datetime.datetime.now()
date_str = date.strftime("%Y-%m-%d")
date_only = pd.to_datetime(date_str).date()
print(date_str)
print(type(date_str))


def convertToBinaryData(filename):
    binarydata = filename.read()
    return binarydata


@app.route('/')
def home():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM admin")
    fetchdata = cur.fetchall()
    cur.close()
    return render_template('index.html', data = fetchdata)




@app.route('/login', methods =['GET','POST'])
def login():
    global dept_id
    msg = ''
    
    
    #Data in drop down menu
    cur = mysql.connection.cursor()
    cur.execute("SELECT department_name FROM admin")
    login_data = cur.fetchall()
    print(login_data)
    cur.close()
    
    #login user and create session
    if request.method == 'POST':
        department = request.form['department']
        password = request.form['password']
        
        
        print(department , password)
        
        # checking for existing account using cursor
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM admin WHERE department_name = %s AND password = %s" , (department,password,))
        account = cursor.fetchone()
        print("account")
        print(account)
        cursor.close()
        
       
        # if account exists crate a session data
        if account:
            session['loggedin'] = True
            session['id'] = account[0]
            dept_id = account[0]
            msg = 'Logged in successfully !'
            
            #cursor for checking user data availablity
            user_id = session['id']
            # events_account=''
            up_events_cursor = mysql.connection.cursor()
            up_events_cursor.execute("SELECT * FROM events WHERE dept_id = {0} AND event_date > '{1}' LIMIT 4".format(user_id,date_str))
            up_events_account = up_events_cursor.fetchall()
            up_events_length = len(up_events_account)
            print("upcomming user account")
            print(up_events_account)
            print(up_events_length)
            up_events_cursor.close()
            
            #cursor of completed events
            completed_cursor = mysql.connection.cursor()
            completed_cursor.execute("SELECT * FROM events WHERE dept_id = {0} AND event_date < '{1}' LIMIT 4".format(user_id,date))
            completed_account = completed_cursor.fetchall()
            
            
            
            #code for admin
            
            
            #cursor for selecting all the user form the staff table
            admin_cursor = mysql.connection.cursor()
            admin_cursor.execute("SELECT * FROM admin WHERE NOT dept_id = 2001")
            admin_accounts = admin_cursor.fetchall()
            admin_cursor.close()
            
            #getting length of the departments for iteration purpose
            admins_length = len(admin_accounts)
            
            #printing the details
            print(admin_accounts)
            print(admins_length)
            
            
            if(user_id != 2001):
                return render_template('dashboard.html', length = up_events_length, event_data = up_events_account, account = account,comp_data = completed_account)
            else:
                return render_template('admin.html',admin_account = admin_accounts, ad_length = admins_length)
        
        else:
            msg = 'Incorrect password !'
        
    return render_template('login.html', msg = msg, data = login_data)

    
    
    
    
@app.route('/dashboard')
def dashboard():
    user_id = session['id']

    events_cursor = mysql.connection.cursor()
    events_cursor.execute("SELECT * FROM events WHERE dept_id = {0} AND event_date > '{1}' LIMIT 4".format(user_id,date_str))
    events_account = events_cursor.fetchall()
    events_length = len(events_account)
    print("user account")
    print(events_account)
    print(events_length)
    events_cursor.close()

    #cursor for selecting a department
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM admin")
    account = cursor.fetchone()
    
    #cursor of completed events
    completed_cursor = mysql.connection.cursor()
    completed_cursor.execute("SELECT * FROM events WHERE dept_id = {0} AND event_date < '{1}' LIMIT 4".format(user_id,date))
    completed_account = completed_cursor.fetchall()
    
    #cursor for selecting the upcomming event
    return render_template('dashboard.html', length=events_length, event_data = events_account,account=account,comp_data = completed_account)





@app.route('/view_events/<int:id>')
def view_event(id):
    uid = id
    
    #cursor for selecting department name
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM admin")
    des_dept_account = cursor.fetchone()
    
    #cursor for selecting specific item
    des_cursor = mysql.connection.cursor()
    des_cursor.execute("SELECT * FROM events WHERE id = {} AND dept_id = {}".format(uid,session['id']))
    des_account = des_cursor.fetchone()
    print(des_account)
    
    return render_template('event_des.html',d_msg = uid, d_account = des_account, admin_acc = des_dept_account)
  
  


@app.route('/edit_events/<int:id>')
def edit_event(id):
    uid = id
    
    #cursor for selecting specific item
    upd_cursor = mysql.connection.cursor()
    upd_cursor.execute("SELECT * FROM events WHERE id = {} AND dept_id = {}".format(uid,session['id']))
    upd_account = upd_cursor.fetchone()

    #printing account in terminal
    print(upd_account)
    
    #returning the edit_details.html page
    return render_template('edit_details.html',upd_acc = upd_account)


@app.route('/update_event/<int:id>', methods=['GET','POST'])
def update_events(id):
    uid = id
    if request.method == 'POST':
        
        #Details for updating the event
        event_name = request.form['event_name']
        event_type = request.form['event_type']
        org_dept = request.form['org_dept']
        hod_name = request.form['hod_name']
        part_dept = request.form['part_dept']
        part_clg = request.form['part_clg']
        event_mode = request.form['event_mode']
        guest_details = request.form['guest_details']
        al_batch_yrs = request.form['al_batch_yrs']
        al_clg_name = request.form['al_clg_name']
        staff_cord = request.form['staff_cord']
        student_cord = request.form['student_cord']
        staff_rapp = request.form['staff_rapp']
        studnet_rapp = request.form['studnet_rapp']
        fun_level = request.form['fun_level']
        partici_type = request.form['partici_type']
        partici_no = request.form['no_partici'] 
        no_days = request.form['no_days']
        
        
        #date and time
        time = request.form['event_time']
        date = request.form['event_date']
        
        #cursor for updating the data
        update_cursor = mysql.connection.cursor()
        update_cursor.execute("UPDATE events SET event_name='{0}',event_type='{1}',organizing_dept='{2}',hod_name='{3}',participating_clg='{4}',participating_dept='{5}',event_mode='{6}',guest_details='{7}',alumni_batch_yr='{8}',alumni_clg_name='{9}',staff_coordinator='{10}',student_coordinator='{11}',staff_rapportuer='{12}',student_rapportuer='{13}',function_level='{14}',participation_type='{15}',no_participants='{16}',no_days='{17}',event_time='{18}',event_date='{19}' WHERE id='{20}'"
                              .format(event_name,event_type,org_dept,hod_name,part_clg,part_dept,event_mode,guest_details,al_batch_yrs,al_clg_name,staff_cord,student_cord,staff_rapp,studnet_rapp,fun_level,partici_type,partici_no,no_days,time,date,uid))
        mysql.connection.commit()
        update_cursor.close()
        
        #code for displaying event tables
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM admin")
        account = cursor.fetchone()
        
        #cursor for dusplaying all events in speecific department
        cursor_table = mysql.connection.cursor()
        cursor_table.execute("SELECT * FROM events WHERE dept_id = {}".format(session['id']))
        event_table = cursor_table.fetchall()
        print(event_table)
        
        
        return render_template('event_details.html',account = account,event_table = event_table,t_date = date_only)
    

@app.route('/event')
def event():
    
    #cursor for selecting a department
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM admin")
    account = cursor.fetchone()
    
    #cursor for dusplaying all events in speecific department
    cursor_table = mysql.connection.cursor()
    cursor_table.execute("SELECT * FROM events WHERE dept_id = {}".format(session['id']))
    event_table = cursor_table.fetchall()
    print(event_table)
    
    return render_template('event_details.html', account = account,event_table = event_table,t_date = date_only)






@app.route('/create_event', methods = ['GET','POST'])
def add_events():
    msg = ''
    dep_id = session['id']
    if request.method == 'POST':
        
        #details to insert a data in the database
        event_name = request.form['event_name']
        event_type = request.form['event_type']
        org_dept = request.form['org_dept']
        hod_name = request.form['hod_name']
        part_dept = request.form['part_dept']
        part_clg = request.form['part_clg']
        event_mode = request.form['event_mode']
        guest_details = request.form['guest_details']
        al_batch_yrs = request.form['al_batch_yrs']
        al_clg_name = request.form['al_clg_name']
        staff_cord = request.form['staff_cord']
        student_cord = request.form['student_cord']
        staff_rapp = request.form['staff_rapp']
        studnet_rapp = request.form['studnet_rapp']
        fun_level = request.form['fun_level']
        partici_type = request.form['partici_type']
        partici_no = request.form['no_partici'] 
        no_days = request.form['no_days']
        
        
        #date and time
        time = request.form['event_time']
        date = request.form['event_date']
        
        #image upload
        photo = request.files['image_file']
        
        #change to binary format
        img_bin = convertToBinaryData(photo)
        
        
        
        print("dfds",type(date))
        
        
        
        #cursor for inserting a data
        ins_cursor = mysql.connection.cursor()
        ins_cursor.execute("INSERT INTO events (dept_id,event_name,event_type,organizing_dept,hod_name, participating_dept,participating_clg,event_mode,guest_details,alumni_batch_yr,alumni_clg_name,staff_coordinator,student_coordinator,staff_rapportuer,student_rapportuer,function_level,participation_type,no_participants,no_days,event_time,event_date) VALUES('{0}','{1}','{2}','{3}','{4}','{5}','{6}','{7}','{8}','{9}','{10}','{11}','{12}','{13}','{14}','{15}','{16}','{17}','{18}','{19}', '{20}')"
                           .format(dep_id,event_name,event_type,org_dept,hod_name,part_dept,part_clg,event_mode,guest_details,al_batch_yrs,al_clg_name,staff_cord,
                            student_cord,staff_rapp,studnet_rapp,fun_level,partici_type,partici_no,no_days,time,date))
        mysql.connection.commit()
        ins_cursor.close()
        
        #message to indicate registration successfull
        msg = 'registered successfully'
        session['loggedin'] = True
    elif request.method == 'POST':
        msg = 'Please fill out the form'
    
    return render_template('add_event.html',msg = msg)





@app.route('/add_event_close')
def add_eve_close():
    user_id = session['id']

    #cursor for display the department name
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM admin")
    account = cursor.fetchone()

    #cursor of upcomming events
    events_cursor = mysql.connection.cursor()
    events_cursor.execute("SELECT * FROM events WHERE dept_id = {0} AND event_date > '{1}' LIMIT 4".format(user_id,date_str))
    events_account = events_cursor.fetchall()
    events_length = len(events_account)
    events_cursor.close()
    
    #cursor of completed events
    completed_cursor = mysql.connection.cursor()
    completed_cursor.execute("SELECT * FROM events WHERE dept_id = {0} AND event_date < '{1}' LIMIT 4".format(user_id,date))
    completed_account = completed_cursor.fetchall()
    
    
    #testing elements 
    print("---------------->>>>>user account<<<<<<----------------")
    print(events_account)
    print(events_length)
    
    #returning values with the possibly obained value from the query
    return render_template('dashboard.html',length=events_length, event_data = events_account,account=account,comp_data = completed_account)


@app.route('/print_table/<int:ids>')
def print_tables(ids):
    
    uid = ids
    #cursor for selecting the department
    print_cursor = mysql.connection.cursor()
    print_cursor.execute("SELECT * FROM admin WHERE dept_id = {}".format(session['id']))
    print_cursor_acc = print_cursor.fetchone()
    print_cursor.close()
    
    
    #cursor for selecting the event name
    print_event_cursor = mysql.connection.cursor()
    print_event_cursor.execute("SELECT * FROM events WHERE id = {} AND dept_id = {}".format(uid,session['id']))
    print_event_acc = print_event_cursor.fetchone()
    print_event_cursor.close()
    
    return render_template('vijaydoc.html', print_account = print_event_acc)

@app.route('/close_table')
def close_table():
    user_id = session['id']

    #cursor for display the department name
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM admin")
    account = cursor.fetchone()

    #cursor of upcomming events
    events_cursor = mysql.connection.cursor()
    events_cursor.execute("SELECT * FROM events WHERE dept_id = {0} AND event_date > '{1}' LIMIT 4".format(user_id,date_str))
    events_account = events_cursor.fetchall()
    events_length = len(events_account)
    events_cursor.close()
    
    #cursor of completed events
    completed_cursor = mysql.connection.cursor()
    completed_cursor.execute("SELECT * FROM events WHERE dept_id = {0} AND event_date < '{1}' LIMIT 4".format(user_id,date))
    completed_account = completed_cursor.fetchall()
    completed_cursor.close()
    
    
    #testing elements 
    print("---------------->>>>>user account<<<<<<----------------")
    print(events_account)
    print(events_length)
    
    #returning values with the possibly obained value from the query
    return render_template('dashboard.html',length=events_length, event_data = events_account,account=account,comp_data = completed_account)



@app.route('/viewall_comp')
def viewall_complete():
    
    user_id = session['id']
    
    #cursor for selecting all completed events from the database
    completed_cursor_v = mysql.connection.cursor()
    completed_cursor_v.execute("SELECT * FROM events WHERE dept_id = {0} AND event_date < '{1}'".format(user_id,date))
    completed_var = completed_cursor_v.fetchall()
    completed_cursor_v.close()
    
    #length of the number of events
    completed_length = len(completed_var)
    
    #testing elements
    print("------------------>>>>all completed events<<<<<---------------")
    print(completed_var)
    print(completed_length)
    
    #returning with possible values
    return render_template('view_all_complete_staff.html',length=completed_length, completed_data = completed_var)
        
    
@app.route('/viewall_notComp')
def viewall_notComplete():
    
    user_id = session['id']
    
    #cursor for selecting all not completed events from the database
    not_completed_v = mysql.connection.cursor()
    not_completed_v.execute("SELECT * FROM events WHERE dept_id = {0} AND event_date > '{1}'".format(user_id,date_str))
    not_completed_var = not_completed_v.fetchall()
    not_completed_v.close()
    
    #length of number of not completed events
    not_completed_length = len(not_completed_var)
    
    
    #returning with possible values
    return render_template('view_all_notComp_staff.html',not_comp_data = not_completed_var,nc_length = not_completed_length)


@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id',None)
    return render_template('index.html')




# Code for admin panel











if __name__ == '__main__':
   app.run(host='0.0.0.0')