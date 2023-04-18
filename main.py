from flask import Flask, redirect, url_for, render_template, request, flash, session
from flask_mysqldb import MySQL
from flask_mail import Mail, Message


import json

app = Flask(__name__)

#Secret key for session data encryption
app.secret_key = 'comrade' 
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Aspire@123'
app.config['MYSQL_DB'] = 'bus_db'

mysql = MySQL(app)

@app.route('/')
def Initial():
    return redirect(url_for('HomePage'))

@app.route('/home')
def HomePage():
    return render_template('homepage.html')

@app.route('/login', methods = ['GET','POST'])
def LoginPage():
    if request.method == 'POST':
        LoginDetails = request.form
        username = LoginDetails['username']
        password = LoginDetails['password']
        mycursor = mysql.connection.cursor()
        mycursor.execute('SELECT USER_ID, USER_POWER, USER_STATUS FROM USER_CREDENTIALS WHERE USERNAME=%s AND PASSWORD=%s',(username,password))
        result = mycursor.fetchall()
        if result:
            for row in result:
                user_id = row[0]
                user_power = row[1]
                user_status = row[2]
                if user_status == 'Active':
                    session['user_id'] = user_id
                    session['user_power'] = user_power
                    session['user_status'] = user_status
                    mycursor.close()
                    print(f'Login successful User ID: {user_id}, User Power: {user_power}')
                    return redirect(url_for('Initial'))
                else:
                    print(f'User Status: Disabled')
                    return render_template('register.html')
        else:
            print("Login failed!")
            mycursor.close()
            return render_template('login.html')
    else:
        return render_template('login.html')
    
@app.route('/register', methods = ['GET','POST'])
def RegisterPage():
    if request.method == 'POST':
        RegisterDetails = request.form.to_dict()
        first_name = RegisterDetails['first_name']
        last_name = RegisterDetails['last_name']
        dob = RegisterDetails['dob']
        email = RegisterDetails['email']
        phone_number = RegisterDetails['phone_number']
        username = RegisterDetails['username']
        password = RegisterDetails['password']
        mycursor = mysql.connection.cursor()
        mycursor.execute('SELECT * FROM USER_CREDENTIALS WHERE USERNAME=%s',(username,))
        value = mycursor.fetchall()
        if value:
            return render_template('register.html', value = True)
        else:
            result = mycursor.execute('INSERT INTO USER_CREDENTIALS (USERNAME,PASSWORD,FIRST_NAME,LAST_NAME,DOB,EMAIL,PHONE_NUMBER) VALUES (%s,%s,%s,%s,%s,%s,%s)',(username,password,first_name,last_name,dob,email,phone_number))
            mysql.connection.commit()
            if result==1:
                print("User registered successfully!")
                mycursor.close()
                return redirect(url_for('LoginPage'))
            else:
                print("Failed to register user!")
                mycursor.close()
                return render_template('register.html')
    else:
        return render_template('register.html')
    
@app.route('/logout')
def LogoutPage():
    [session.pop(i, None) for i in ['user_id', 'user_power', 'travel_id']]
    return redirect(url_for('LoginPage'))
    
@app.route('/profile', methods = ['GET','POST'])
def ViewProfile():
    if request.method == 'POST':
        action = request.form['action']
        if action == 'DisableAccount':
            user_id = session['user_id']
            user_status = 'Disabled'
            mycursor = mysql.connection.cursor()
            mycursor.execute('UPDATE USER_CREDENTIALS SET USER_STATUS = %s WHERE USER_ID = %s',(user_status,user_id))
            mysql.connection.commit()
            return render_template('login.html')

        else:
            return render_template('profile.html')
        
    else:
        if 'user_id' in session:
            user_id = session['user_id']
            mycursor = mysql.connection.cursor()
            mycursor.execute('SELECT FIRST_NAME,LAST_NAME,DOB,EMAIL,PHONE_NUMBER FROM USER_CREDENTIALS WHERE USER_ID=%s',(user_id,))
            result = mycursor.fetchall()
            if result:
                for row in result:
                    first_name = row[0]
                    last_name = row[1]
                    dob = row[2]
                    email = row[3]
                    phone_number = row[4]
                    return render_template('profile.html', first_name=first_name, last_name=last_name, dob=dob, email=email, phone_number=phone_number)
            else:
                print("Failed to fetch user details!")
                return render_template('profile.html')
        else:
            return redirect(url_for('LoginPage'))

@app.route('/payments')
def FetchCard():
    if 'user_id' in session:
        card_balance = request.args.get('card_balance')
        card_number = request.args.get('card_number')
        user_id = session['user_id']
        session['card_number'] = card_number
        mycursor = mysql.connection.cursor()
        mycursor.execute("SELECT WALLET FROM USER_CREDENTIALS WHERE USER_ID = %s",(user_id,))
        result1 = mycursor.fetchall()
        wallet_balance = result1[0][0]
        mycursor.execute('SELECT CARD_NUMBER, CARDHOLDER_NAME, CARD_EXPIRY, CARD_BALANCE, CARD_TYPE FROM CARD_DETAILS WHERE USER_ID = %s',(user_id,))
        result2 = mycursor.fetchall()
        mycursor.close()
        if result2:
            return render_template('payments.html', wallet_balance = wallet_balance, carddetails = result2, value=True, card_balance = card_balance, card_number = card_number)
        else:
            return render_template('payments.html', wallet_balance = wallet_balance, value=False)
    else:
        return redirect(url_for('LoginPage'))
    
@app.route('/payments', methods=['GET','POST'])
def PaymentFunctions():
    if 'user_id' in session:
        user_id = session['user_id']
        if request.method == 'POST':
            action = request.form['action']
            if action == 'AddCard':
                card_type = request.form['card_type']
                card_number = request.form['card_number']
                cardholder_name = request.form['cardholder_name']
                card_expiry = request.form['card_expiry']
                card_cvv = request.form['card_cvv']
                mycursor = mysql.connection.cursor()
                mycursor.execute('INSERT INTO CARD_DETAILS (USER_ID, CARD_TYPE, CARD_NUMBER, CARDHOLDER_NAME, CARD_EXPIRY, CARD_CVV) VALUES (%s,%s,%s,%s,%s,%s)',(user_id,card_type,card_number,cardholder_name,card_expiry,card_cvv))
                mysql.connection.commit()
                mycursor.close()
                return redirect(url_for('FetchCard'))
            
            if len(action) == 19:
                mycursor = mysql.connection.cursor()
                mycursor.execute('SELECT CARD_BALANCE FROM CARD_DETAILS WHERE CARD_NUMBER = %s',(action,))
                result = mycursor.fetchall()
                balance = result[0][0]
                return redirect(url_for('FetchCard', card_balance = balance, card_number = action))
            
            if action == 'AddWallet':
                amount = request.form['amount']
                amount = int(amount)
                user_id = session['user_id']
                card_number = session['card_number']
                mycursor = mysql.connection.cursor()
                mycursor.execute('SELECT WALLET FROM USER_CREDENTIALS WHERE USER_ID = %s',(user_id,))
                wallet_balance_result = mycursor.fetchall()
                wallet_balance = wallet_balance_result[0][0]
                mycursor.execute('SELECT CARD_BALANCE FROM CARD_DETAILS WHERE CARD_NUMBER = %s',(card_number,))
                card_balance_result = mycursor.fetchall()
                card_balance = card_balance_result[0][0]
                if card_balance < amount:
                    print('Insufficient funds')
                    return redirect(url_for('FetchCard', card_balance = card_balance, card_number = card_number))
                else:
                    wallet_balance = wallet_balance + amount
                    card_balance = card_balance - amount
                    mycursor.execute('UPDATE CARD_DETAILS SET CARD_BALANCE = %s WHERE CARD_NUMBER = %s',(card_balance,card_number))
                    mysql.connection.commit()
                    mycursor.execute('UPDATE USER_CREDENTIALS SET WALLET = %s WHERE USER_ID = %s',(wallet_balance,user_id))
                    mysql.connection.commit()
                    action = 'Credit'
                    description = 'Added money to wallet from card'
                    mycursor.execute('INSERT INTO TRANSACTION_DETAILS (USER_ID, AMOUNT, ACTION, BALANCE, DESCRIPTION) VALUES (%s,%s,%s,%s,%s)',(user_id,amount,action,wallet_balance,description))
                    mysql.connection.commit()
                    mycursor.close()
                    return redirect(url_for('FetchCard', card_balance = card_balance, card_number = card_number))
            
            else:
                return redirect(url_for('LoginPage'))
        else:
            return redirect(url_for('FetchCard'))

    else:
        return redirect(url_for('LoginPage'))


@app.route('/users-list', methods=['GET', 'POST'])
def UsersList():
    if session['user_power'] != 'Admin':
        return redirect(url_for('HomePage'))

    if request.method == 'POST':
        user_id = request.form['user_id']
        action = request.form['action']
        if session['user_id'] == user_id:
            print("You cannot perform this admin action on yourself!")
            return redirect(url_for('UsersList'))
        else:
            mycursor = mysql.connection.cursor()
            if action == 'AddAdmin':
                mycursor.execute('UPDATE USER_CREDENTIALS SET USER_POWER=%s WHERE USER_ID=%s', ('Admin', user_id))
            elif action == 'RemoveAdmin':
                mycursor.execute('UPDATE USER_CREDENTIALS SET USER_POWER=%s WHERE USER_ID=%s', ('User', user_id))
            elif action == 'KickUser':
                mycursor.execute('DELETE FROM USER_CREDENTIALS WHERE USER_ID=%s', (user_id,))
            mysql.connection.commit()
            mycursor.close()
        return redirect(url_for('UsersList'))

    else:
        mycursor = mysql.connection.cursor()
        mycursor.execute('SELECT USER_ID, FIRST_NAME, LAST_NAME, EMAIL, USER_POWER FROM USER_CREDENTIALS')
        result = mycursor.fetchall()
        mycursor.close()
        return render_template('users-list.html', users=result)
    
@app.route('/bus-management', methods = ['GET','POST'])
def BusManagement():
    if session['user_power'] != 'Admin':
        return redirect(url_for('HomePage'))

    if request.method == 'POST':
        action = request.form['action']
        if action == 'RemoveBus':
            bus_id = request.form['bus_id']
            mycursor = mysql.connection.cursor()
            mycursor.execute('DELETE FROM SEAT_DETAILS WHERE BUS_ID=%s',(bus_id,))
            mysql.connection.commit()
            mycursor.execute('DELETE FROM TRAVEL_DETAILS WHERE BUS_ID=%s',(bus_id,))
            mysql.connection.commit()
            mycursor.execute('DELETE FROM BUS_DETAILS WHERE BUS_ID = %s',(bus_id,))
        elif action == 'AddBus':
            bus_number = request.form['bus_number']
            operator_name = request.form['operator_name']
            operator_number = request.form['operator_number']
            total_seats = request.form['total_seats']
            base_fare = request.form['base_fare']
            bus_type = request.form['bus_type']
            reclining_seats = request.form['reclining_seats']
            charging_points = request.form['charging_points']
            wifi = request.form['wifi']
            blankets_pillows = request.form['blankets_pillows']
            snacks = request.form['snacks']
            movie = request.form['movie']
            reading_light = request.form['reading_light']
            track_my_bus = request.form['track_my_bus']
            m_ticket = request.form['m_ticket']
            mycursor = mysql.connection.cursor()
            mycursor.execute('INSERT INTO BUS_DETAILS (BUS_NUMBER,OPERATOR_NAME,OPERATOR_NUMBER,TOTAL_SEATS,BASE_FARE,BUS_TYPE,RECLINING_SEATS,CHARGING_POINTS,WIFI,BLANKETS_PILLOWS,SNACKS,MOVIE,READING_LIGHT,TRACK_MY_BUS,M_TICKET) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)',(bus_number,operator_name,operator_number,total_seats,base_fare,bus_type,reclining_seats,charging_points,wifi,blankets_pillows,snacks,movie,reading_light,track_my_bus,m_ticket))
        mysql.connection.commit()
        mycursor.close()
        return redirect(url_for('BusManagement'))

    else:
        mycursor = mysql.connection.cursor()
        mycursor.execute('SELECT * FROM BUS_DETAILS')
        result = mycursor.fetchall()
        mycursor.close()
        return render_template('bus-management.html', busdetails = result)
    
@app.route('/travel-management', methods=['GET','POST'])
def TravelManagement():
    if session['user_power'] != 'Admin':
        return redirect(url_for('HomePage'))
    
    if request.method == 'POST':
        action = request.form['action']
        if action == 'RemoveTravel':
            travel_id = request.form['travel_id']
            mycursor = mysql.connection.cursor()
            mycursor.execute('DELETE FROM BOOKING_DETAILS WHERE TRAVEL_ID = %s',(travel_id,))
            mycursor.execute('DELETE FROM SEAT_DETAILS WHERE TRAVEL_ID = %s',(travel_id,))
            mycursor.execute('DELETE FROM TRAVEL_DETAILS WHERE TRAVEL_ID = %s',(travel_id,))
        elif action == 'AddTravel':
            bus_id = request.form['bus_id']
            source_location = request.form['source_location']
            destination_location = request.form['destination_location']
            source_date = request.form['source_date']
            destination_date = request.form['destination_date']
            source_time = request.form['source_time']
            destination_time = request.form['destination_time']
            travel_distance = request.form['travel_distance']
            mycursor = mysql.connection.cursor()
            mycursor.execute('SELECT OPERATOR_NAME, TOTAL_SEATS, BASE_FARE FROM BUS_DETAILS WHERE BUS_ID=%s',(bus_id,))
            result = mycursor.fetchall()
            if result:
                for row in result:
                    operator_name = row[0]
                    total_seats = row[1]
                    base_fare = row[2]
                total_fare = int(base_fare) * int(travel_distance)
                mycursor.execute('INSERT INTO TRAVEL_DETAILS (BUS_ID,OPERATOR_NAME,SOURCE_LOCATION,DESTINATION_LOCATION,SOURCE_DATE,DESTINATION_DATE,SOURCE_TIME,DESTINATION_TIME,TRAVEL_DISTANCE,TOTAL_FARE,TOTAL_SEATS,AVAILABLE_SEATS,BOOKED_SEATS,TEMPORARY_SEATS) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)',(bus_id,operator_name,source_location,destination_location,source_date,destination_date,source_time,destination_time,travel_distance,total_fare,total_seats,total_seats,0,0))
                mysql.connection.commit()
                mycursor.execute('SELECT TRAVEL_ID FROM TRAVEL_DETAILS WHERE BUS_ID=%s AND SOURCE_LOCATION=%s AND DESTINATION_LOCATION=%s AND SOURCE_DATE=%s AND DESTINATION_DATE=%s AND SOURCE_TIME=%s AND DESTINATION_TIME=%s',(bus_id,source_location,destination_location,source_date,destination_date,source_time,destination_time))
                result = mycursor.fetchall()
                if result:
                    for row in result:
                        travel_id = row[0]
                for seat_number in range(1, int(total_seats)+1):
                    mycursor.execute('INSERT INTO SEAT_DETAILS (TRAVEL_ID,BUS_ID,SEAT_NUMBER) VALUES (%s,%s,%s)', (travel_id, bus_id, seat_number))
            else:
                print("Failed to fetch bus details!")
                return redirect(url_for('TravelManagement'))
        mysql.connection.commit()
        mycursor.close()
        return redirect(url_for('TravelManagement'))

    else:
        mycursor = mysql.connection.cursor()
        mycursor.execute('SELECT TRAVEL_ID,BUS_ID,OPERATOR_NAME,SOURCE_LOCATION,DESTINATION_LOCATION,SOURCE_DATE,DESTINATION_DATE,SOURCE_TIME,DESTINATION_TIME,TRAVEL_DISTANCE,TOTAL_FARE FROM TRAVEL_DETAILS')
        result = mycursor.fetchall()
        mycursor.close()
        return render_template('travel-management.html', traveldetails = result)
    
@app.route('/seat-management', methods=['GET','POST'])
def SeatManagement():
    if session['user_power'] != 'Admin':
        return redirect(url_for('HomePage'))
    
    if request.method == 'POST':
        action = request.form['action']
        if action == 'FetchSeats':
            travel_id = request.form['travel_id']
            session['admin_travel_id'] = travel_id
            mycursor = mysql.connection.cursor()
            mycursor.execute("SELECT TRAVEL_ID, SEAT_ID, USER_ID, SEAT_NUMBER, SEAT_STATUS FROM SEAT_DETAILS WHERE TRAVEL_ID=%s",(travel_id,))
            result = mycursor.fetchall()
            mycursor.close()
            return render_template('seat-management.html', seatdetails = result, travel_id=travel_id)
        
        if action == 'Available':
            seat_number = request.form['seat_number']
            travel_id = session['admin_travel_id']
            mycursor = mysql.connection.cursor()
            seat_status = 'Available'
            user_id = 0
            mycursor.execute('UPDATE SEAT_DETAILS SET SEAT_STATUS=%s, USER_ID=%s WHERE TRAVEL_ID=%s AND SEAT_NUMBER=%s',(seat_status,user_id,travel_id,seat_number))
            mysql.connection.commit()
            mycursor.execute('SELECT AVAILABLE_SEATS, TEMPORARY_SEATS FROM TRAVEL_DETAILS WHERE TRAVEL_ID=%s',(travel_id,))
            result = mycursor.fetchall()
            i=1
            for row in result:
                available_seats_db = row[0]
                temporary_seats_db = row[1]
            available_seats_db = available_seats_db + i
            temporary_seats_db = temporary_seats_db - i
            mycursor.execute('UPDATE TRAVEL_DETAILS SET AVAILABLE_SEATS=%s, TEMPORARY_SEATS=%s WHERE TRAVEL_ID=%s',(available_seats_db,temporary_seats_db,travel_id))
            mysql.connection.commit()
            mycursor.close()
            return redirect(url_for('SeatManagement'))
            
    else:
            if 'admin_travel_id' in session:
                travel_id = session['admin_travel_id']
                mycursor = mysql.connection.cursor()
                mycursor.execute("SELECT TRAVEL_ID, SEAT_ID, USER_ID, SEAT_NUMBER, SEAT_STATUS FROM SEAT_DETAILS WHERE TRAVEL_ID=%s",(travel_id,))
                result = mycursor.fetchall()
                mycursor.close()
                return render_template('seat-management.html', seatdetails = result, travel_id=travel_id)
            else:
                mycursor = mysql.connection.cursor()
                mycursor.execute("SELECT TRAVEL_ID, SEAT_ID, USER_ID, SEAT_NUMBER, SEAT_STATUS FROM SEAT_DETAILS",())
                result = mycursor.fetchall()
                mycursor.close()
                return render_template('seat-management.html', seatdetails = result)
            
@app.route('/booking-management', methods = ['GET','POST'])
def BookingManagement():
    if session['user_power'] != 'Admin':
        return redirect(url_for('HomePage'))
    
    if request.method == 'POST':
        action = request.form['action']
        if action == 'CancelTicket':
            booking_id = request.form['booking_id']
            mycursor = mysql.connection.cursor()
            mycursor.execute('SELECT TOTAL_FARE, PASSENGERS, TRAVEL_ID, USER_ID FROM BOOKING_DETAILS WHERE BOOKING_ID=%s',(booking_id,))
            result = mycursor.fetchall()
            total_fare = result[0][0]
            passengers_count = result[0][1]
            travel_id = result[0][2]
            user_id = result[0][3]
            mycursor.execute('SELECT SEAT_NUMBER FROM PASSENGER_DETAILS WHERE BOOKING_ID=%s',(booking_id))
            result = mycursor.fetchall()
            seats = []
            for i in range(passengers_count):
                seats.append(result[i][0])
            seat_status = 'Available'
            update_user_id = 0
            for i in range(passengers_count):
                seat_number = seats[i]
                mycursor.execute('UPDATE SEAT_DETAILS SET SEAT_STATUS=%s, USER_ID=%s WHERE SEAT_NUMBER=%s AND TRAVEL_ID=%s',(seat_status,update_user_id,seat_number,travel_id))
                mysql.connection.commit()
            mycursor.execute('SELECT AVAILABLE_SEATS, BOOKED_SEATS FROM TRAVEL_DETAILS WHERE TRAVEL_ID=%s',(travel_id,))
            result = mycursor.fetchall()
            available_seats_db = result[0][0]
            booked_seats_db = result[0][1]
            available_seats_db = available_seats_db + passengers_count
            booked_seats_db = booked_seats_db - passengers_count
            mycursor.execute('UPDATE TRAVEL_DETAILS SET AVAILABLE_SEATS=%s, BOOKED_SEATS=%s WHERE TRAVEL_ID=%s',(available_seats_db,booked_seats_db,travel_id,))
            mysql.connection.commit()
            mycursor.execute('UPDATE USER_CREDENTIALS SET WALLET=WALLET+%s WHERE USER_ID=%s',(total_fare,user_id))
            mysql.connection.commit()
            mycursor.execute('SELECT WALLET FROM USER_CREDENTIALS WHERE USER_ID=%s',(user_id,))
            result = mycursor.fetchall()
            balance = result[0][0]
            action = 'Credit'
            description = 'Crediting cancelled ticket fare'
            mycursor.execute("INSERT INTO TRANSACTION_DETAILS (USER_ID, AMOUNT, ACTION, BALANCE, DESCRIPTION) VALUES (%s,%s,%s,%s,%s)",(user_id,total_fare,action,balance,description))
            mysql.connection.commit()
            payment_status = 'Refunded'
            booking_status = 'Cancelled'
            mycursor.execute("UPDATE BOOKING_DETAILS SET PAYMENT_STATUS=%s, BOOKING_STATUS=%s WHERE BOOKING_ID=%s AND USER_ID=%s",(payment_status,booking_status,booking_id,user_id))
            mysql.connection.commit()
            return redirect(url_for('BookingManagement'))
        
        if action == 'ViewTicket':
            booking_id = request.form['booking_id']
            mycursor = mysql.connection.cursor()
            mycursor.execute('SELECT TRAVEL_ID FROM BOOKING_DETAILS WHERE BOOKING_ID=%s',(booking_id,))
            result = mycursor.fetchall()
            travel_id = result[0][0]
            mycursor = mysql.connection.cursor()
            mycursor.execute('SELECT BD.OPERATOR_NAME,BD.BUS_NUMBER,TD.SOURCE_LOCATION,TD.DESTINATION_LOCATION,TD.SOURCE_DATE,TD.DESTINATION_DATE,TD.SOURCE_TIME,TD.DESTINATION_TIME,TD.TOTAL_FARE FROM BUS_DETAILS BD INNER JOIN TRAVEL_DETAILS TD ON BD.BUS_ID = TD.BUS_ID WHERE TD.TRAVEL_ID=%s',(travel_id,))
            result1 = mycursor.fetchall()
            mycursor.execute('SELECT TOTAL_FARE, PASSENGERS, PAYMENT_STATUS, BOOKING_STATUS FROM BOOKING_DETAILS WHERE BOOKING_ID=%s',(booking_id,))
            result2 = mycursor.fetchall()
            mycursor.execute('SELECT FIRST_NAME, LAST_NAME, AGE, GENDER FROM PASSENGER_DETAILS WHERE BOOKING_ID=%s AND TRAVEL_ID=%s',(booking_id,travel_id))
            result3 = mycursor.fetchall()
            mycursor.close()
            return render_template('ticket-view.html', booking_id = booking_id, details1 = result1, details2 = result2, details3 = result3)

    else:
        mycursor = mysql.connection.cursor()
        mycursor.execute('SELECT * FROM BOOKING_DETAILS')
        result = mycursor.fetchall()
        mycursor.close()
        return render_template('booking-management.html', booking_details = result)

  
@app.route('/search-bus', methods = ['GET','POST'])
def SearchBus():
    
    if request.method == 'POST':
        action = request.form['action']
        print(action)
        if action == 'SearchBus':
            user_id = session.get('user_id')
            source_location = request.form['source_location']
            destination_location = request.form['destination_location']
            source_date = request.form['source_date']
            session['source_location'] = source_location
            session['destination_location'] = destination_location
            session['source_date'] = source_date
            mycursor = mysql.connection.cursor()
            query = 'SELECT OPERATOR_NAME, SOURCE_LOCATION, DESTINATION_LOCATION, SOURCE_DATE, DESTINATION_DATE, SOURCE_TIME, DESTINATION_TIME, TOTAL_FARE, AVAILABLE_SEATS,  TRAVEL_ID, BUS_ID FROM TRAVEL_DETAILS WHERE SOURCE_LOCATION=%s AND DESTINATION_LOCATION=%s AND SOURCE_DATE=%s'
            values = (source_location,destination_location,source_date)
            mycursor.execute(query, values)
            result = mycursor.fetchall()
            if result:
                result_with_bus_details = []
                for row in result:
                    bus_id = row[10]
                    mycursor = mysql.connection.cursor()
                    mycursor.execute('SELECT BUS_TYPE, RECLINING_SEATS, CHARGING_POINTS, WIFI, BLANKETS_PILLOWS, SNACKS, MOVIE, READING_LIGHT, TRACK_MY_BUS, M_TICKET FROM BUS_DETAILS WHERE BUS_ID=%s',(bus_id,))
                    bus_details = mycursor.fetchall()
                    for bus in bus_details:
                        row = list(row)
                        row.append(bus[0])
                        row.append(bus[1])
                        row.append(bus[2])
                        row.append(bus[3])
                        row.append(bus[4])
                        row.append(bus[5])
                        row.append(bus[6])
                        row.append(bus[7])
                        row.append(bus[8])
                        row.append(bus[9])
                        mycursor.close()
                        tuple_row = tuple(row)
                        result_with_bus_details.append(tuple_row)
                mycursor.close()
                mycursor = mysql.connection.cursor()
                mycursor.execute('SELECT DISTINCT B.OPERATOR_NAME, B.BUS_NUMBER FROM BUS_DETAILS B INNER JOIN TRAVEL_DETAILS T ON B.BUS_ID = T.BUS_ID WHERE T.SOURCE_LOCATION=%s AND T.DESTINATION_LOCATION=%s AND T.SOURCE_DATE=%s',(source_location,destination_location,source_date))
                operator_result = mycursor.fetchall()
                count = len(result_with_bus_details)
                return render_template('search-bus.html', traveldetails = result_with_bus_details, operatordetails = operator_result, value = True, user_id = user_id, count=count, option=None)
            else:
                print('Nothing inside')
                return render_template('search-bus.html', value = False)
        
        if action == 'SelectSeat':
            travel_id = request.form['travel_id']
            session['booking_travel_id'] = travel_id
            return redirect(url_for('SeatSelection'))
        
        if action == 'Filters':
            options = request.form['selected_options']
            selected_option = options.split(",")
            source_location = session['source_location']
            destination_location = session['destination_location']
            source_date = session['source_date']
            mycursor = mysql.connection.cursor()
            query = 'SELECT OPERATOR_NAME, SOURCE_LOCATION, DESTINATION_LOCATION, SOURCE_DATE, DESTINATION_DATE, SOURCE_TIME, DESTINATION_TIME, TOTAL_FARE, AVAILABLE_SEATS,  TRAVEL_ID, BUS_ID FROM TRAVEL_DETAILS WHERE SOURCE_LOCATION=%s AND DESTINATION_LOCATION=%s AND SOURCE_DATE=%s'
            values = (source_location,destination_location,source_date)
            if 'dep_before_6am' in selected_option:
                query += ' AND SOURCE_TIME < "06:00:00"'
            if 'dep_6am_to_12pm' in selected_option:
                query += ' AND SOURCE_TIME >= "06:00:00" AND SOURCE_TIME <= "12:00:00"'
            if 'dep_12pm_to_6Pm' in selected_option:
                query += ' AND SOURCE_TIME >= "12:00:00" AND SOURCE_TIME <= "18:00:00"'
            if 'dep_after_6pm' in selected_option:
                query += ' AND SOURCE_TIME > "18:00:00"'
            print(query)
            mycursor.execute(query, values)
            result = mycursor.fetchall()
            if result:
                result_with_bus_details = []
                for row in result:
                    bus_id = row[10]
                    mycursor = mysql.connection.cursor()
                    mycursor.execute('SELECT BUS_TYPE, RECLINING_SEATS, CHARGING_POINTS, WIFI, BLANKETS_PILLOWS, SNACKS, MOVIE, READING_LIGHT, TRACK_MY_BUS, M_TICKET FROM BUS_DETAILS WHERE BUS_ID=%s',(bus_id,))
                    bus_details = mycursor.fetchall()
                    for bus in bus_details:
                        row = list(row)
                        row.append(bus[0])
                        row.append(bus[1])
                        row.append(bus[2])
                        row.append(bus[3])
                        row.append(bus[4])
                        row.append(bus[5])
                        row.append(bus[6])
                        row.append(bus[7])
                        row.append(bus[8])
                        row.append(bus[9])
                        mycursor.close()
                        tuple_row = tuple(row)
                        result_with_bus_details.append(tuple_row)
                mycursor.close()
                mycursor = mysql.connection.cursor()
                mycursor.execute('SELECT DISTINCT B.OPERATOR_NAME, B.BUS_NUMBER FROM BUS_DETAILS B INNER JOIN TRAVEL_DETAILS T ON B.BUS_ID = T.BUS_ID WHERE T.SOURCE_LOCATION=%s AND T.DESTINATION_LOCATION=%s AND T.SOURCE_DATE=%s',(source_location,destination_location,source_date))
                operator_result = mycursor.fetchall()
                print(result_with_bus_details[0][12])
                print(type(result_with_bus_details[0][12]))
                return render_template('search-bus.html', traveldetails = result_with_bus_details, operatordetails = operator_result, value = True)
            else:
                print('Nothing inside')
                return render_template('search-bus.html', value = False)
            
        if action == 'CompareNow':
            compare_option = request.form['CompareOptions']
            print(compare_option)
            compare_option = compare_option.replace('[','').replace(']','').replace('"','')
            print(compare_option)
            compare_travel_id = [int(i) for i in compare_option.split(",")]
            print(compare_travel_id)
            return redirect(url_for('Comparison', compare_travel_id = compare_travel_id))
        
        if action == 'EarlyDeparture':
            user_id = session.get('user_id')
            source_location = session['source_location']
            destination_location = session['destination_location']
            source_date = session['source_date']
            mycursor = mysql.connection.cursor()
            query = 'SELECT OPERATOR_NAME, SOURCE_LOCATION, DESTINATION_LOCATION, SOURCE_DATE, DESTINATION_DATE, SOURCE_TIME, DESTINATION_TIME, TOTAL_FARE, AVAILABLE_SEATS,  TRAVEL_ID, BUS_ID FROM TRAVEL_DETAILS WHERE SOURCE_LOCATION=%s AND DESTINATION_LOCATION=%s AND SOURCE_DATE=%s ORDER BY SOURCE_TIME ASC'
            values = (source_location,destination_location,source_date)
            mycursor.execute(query, values)
            result = mycursor.fetchall()
            if result:
                result_with_bus_details = []
                for row in result:
                    bus_id = row[10]
                    mycursor = mysql.connection.cursor()
                    mycursor.execute('SELECT BUS_TYPE, RECLINING_SEATS, CHARGING_POINTS, WIFI, BLANKETS_PILLOWS, SNACKS, MOVIE, READING_LIGHT, TRACK_MY_BUS, M_TICKET FROM BUS_DETAILS WHERE BUS_ID=%s',(bus_id,))
                    bus_details = mycursor.fetchall()
                    for bus in bus_details:
                        row = list(row)
                        row.append(bus[0])
                        row.append(bus[1])
                        row.append(bus[2])
                        row.append(bus[3])
                        row.append(bus[4])
                        row.append(bus[5])
                        row.append(bus[6])
                        row.append(bus[7])
                        row.append(bus[8])
                        row.append(bus[9])
                        mycursor.close()
                        tuple_row = tuple(row)
                        result_with_bus_details.append(tuple_row)
                mycursor.close()
                mycursor = mysql.connection.cursor()
                mycursor.execute('SELECT DISTINCT B.OPERATOR_NAME, B.BUS_NUMBER FROM BUS_DETAILS B INNER JOIN TRAVEL_DETAILS T ON B.BUS_ID = T.BUS_ID WHERE T.SOURCE_LOCATION=%s AND T.DESTINATION_LOCATION=%s AND T.SOURCE_DATE=%s',(source_location,destination_location,source_date))
                operator_result = mycursor.fetchall()
                count = len(result_with_bus_details)
                return render_template('search-bus.html', traveldetails = result_with_bus_details, operatordetails = operator_result, value = True, user_id = user_id, count=count, option=action)
            else:
                print('Nothing inside')
                return render_template('search-bus.html', value = False, option=action)
            
        if action == 'LateDeparture':
            user_id = session.get('user_id')
            source_location = session['source_location']
            destination_location = session['destination_location']
            source_date = session['source_date']
            mycursor = mysql.connection.cursor()
            query = 'SELECT OPERATOR_NAME, SOURCE_LOCATION, DESTINATION_LOCATION, SOURCE_DATE, DESTINATION_DATE, SOURCE_TIME, DESTINATION_TIME, TOTAL_FARE, AVAILABLE_SEATS,  TRAVEL_ID, BUS_ID FROM TRAVEL_DETAILS WHERE SOURCE_LOCATION=%s AND DESTINATION_LOCATION=%s AND SOURCE_DATE=%s ORDER BY SOURCE_TIME DESC'
            values = (source_location,destination_location,source_date)
            mycursor.execute(query, values)
            result = mycursor.fetchall()
            if result:
                result_with_bus_details = []
                for row in result:
                    bus_id = row[10]
                    mycursor = mysql.connection.cursor()
                    mycursor.execute('SELECT BUS_TYPE, RECLINING_SEATS, CHARGING_POINTS, WIFI, BLANKETS_PILLOWS, SNACKS, MOVIE, READING_LIGHT, TRACK_MY_BUS, M_TICKET FROM BUS_DETAILS WHERE BUS_ID=%s',(bus_id,))
                    bus_details = mycursor.fetchall()
                    for bus in bus_details:
                        row = list(row)
                        row.append(bus[0])
                        row.append(bus[1])
                        row.append(bus[2])
                        row.append(bus[3])
                        row.append(bus[4])
                        row.append(bus[5])
                        row.append(bus[6])
                        row.append(bus[7])
                        row.append(bus[8])
                        row.append(bus[9])
                        mycursor.close()
                        tuple_row = tuple(row)
                        result_with_bus_details.append(tuple_row)
                mycursor.close()
                mycursor = mysql.connection.cursor()
                mycursor.execute('SELECT DISTINCT B.OPERATOR_NAME, B.BUS_NUMBER FROM BUS_DETAILS B INNER JOIN TRAVEL_DETAILS T ON B.BUS_ID = T.BUS_ID WHERE T.SOURCE_LOCATION=%s AND T.DESTINATION_LOCATION=%s AND T.SOURCE_DATE=%s',(source_location,destination_location,source_date))
                operator_result = mycursor.fetchall()
                count = len(result_with_bus_details)
                return render_template('search-bus.html', traveldetails = result_with_bus_details, operatordetails = operator_result, value = True, user_id = user_id, count=count, option=action)
            else:
                print('Nothing inside')
                return render_template('search-bus.html', value = False, option=action)
            
        if action == 'EarlyArrival':
            user_id = session.get('user_id')
            source_location = session['source_location']
            destination_location = session['destination_location']
            source_date = session['source_date']
            mycursor = mysql.connection.cursor()
            query = 'SELECT OPERATOR_NAME, SOURCE_LOCATION, DESTINATION_LOCATION, SOURCE_DATE, DESTINATION_DATE, SOURCE_TIME, DESTINATION_TIME, TOTAL_FARE, AVAILABLE_SEATS,  TRAVEL_ID, BUS_ID FROM TRAVEL_DETAILS WHERE SOURCE_LOCATION=%s AND DESTINATION_LOCATION=%s AND SOURCE_DATE=%s ORDER BY DESTINATION_DATE ASC, DESTINATION_TIME ASC'
            values = (source_location,destination_location,source_date)
            mycursor.execute(query, values)
            result = mycursor.fetchall()
            if result:
                result_with_bus_details = []
                for row in result:
                    bus_id = row[10]
                    mycursor = mysql.connection.cursor()
                    mycursor.execute('SELECT BUS_TYPE, RECLINING_SEATS, CHARGING_POINTS, WIFI, BLANKETS_PILLOWS, SNACKS, MOVIE, READING_LIGHT, TRACK_MY_BUS, M_TICKET FROM BUS_DETAILS WHERE BUS_ID=%s',(bus_id,))
                    bus_details = mycursor.fetchall()
                    for bus in bus_details:
                        row = list(row)
                        row.append(bus[0])
                        row.append(bus[1])
                        row.append(bus[2])
                        row.append(bus[3])
                        row.append(bus[4])
                        row.append(bus[5])
                        row.append(bus[6])
                        row.append(bus[7])
                        row.append(bus[8])
                        row.append(bus[9])
                        mycursor.close()
                        tuple_row = tuple(row)
                        result_with_bus_details.append(tuple_row)
                mycursor.close()
                mycursor = mysql.connection.cursor()
                mycursor.execute('SELECT DISTINCT B.OPERATOR_NAME, B.BUS_NUMBER FROM BUS_DETAILS B INNER JOIN TRAVEL_DETAILS T ON B.BUS_ID = T.BUS_ID WHERE T.SOURCE_LOCATION=%s AND T.DESTINATION_LOCATION=%s AND T.SOURCE_DATE=%s',(source_location,destination_location,source_date))
                operator_result = mycursor.fetchall()
                count = len(result_with_bus_details)
                return render_template('search-bus.html', traveldetails = result_with_bus_details, operatordetails = operator_result, value = True, user_id = user_id, count=count, option=action)
            else:
                print('Nothing inside')
                return render_template('search-bus.html', value = False, option=action)
            
        if action == 'LateArrival':
            user_id = session.get('user_id')
            source_location = session['source_location']
            destination_location = session['destination_location']
            source_date = session['source_date']
            mycursor = mysql.connection.cursor()
            query = 'SELECT OPERATOR_NAME, SOURCE_LOCATION, DESTINATION_LOCATION, SOURCE_DATE, DESTINATION_DATE, SOURCE_TIME, DESTINATION_TIME, TOTAL_FARE, AVAILABLE_SEATS,  TRAVEL_ID, BUS_ID FROM TRAVEL_DETAILS WHERE SOURCE_LOCATION=%s AND DESTINATION_LOCATION=%s AND SOURCE_DATE=%s ORDER BY DESTINATION_DATE DESC, DESTINATION_TIME DESC'
            values = (source_location,destination_location,source_date)
            mycursor.execute(query, values)
            result = mycursor.fetchall()
            if result:
                result_with_bus_details = []
                for row in result:
                    bus_id = row[10]
                    mycursor = mysql.connection.cursor()
                    mycursor.execute('SELECT BUS_TYPE, RECLINING_SEATS, CHARGING_POINTS, WIFI, BLANKETS_PILLOWS, SNACKS, MOVIE, READING_LIGHT, TRACK_MY_BUS, M_TICKET FROM BUS_DETAILS WHERE BUS_ID=%s',(bus_id,))
                    bus_details = mycursor.fetchall()
                    for bus in bus_details:
                        row = list(row)
                        row.append(bus[0])
                        row.append(bus[1])
                        row.append(bus[2])
                        row.append(bus[3])
                        row.append(bus[4])
                        row.append(bus[5])
                        row.append(bus[6])
                        row.append(bus[7])
                        row.append(bus[8])
                        row.append(bus[9])
                        mycursor.close()
                        tuple_row = tuple(row)
                        result_with_bus_details.append(tuple_row)
                mycursor.close()
                mycursor = mysql.connection.cursor()
                mycursor.execute('SELECT DISTINCT B.OPERATOR_NAME, B.BUS_NUMBER FROM BUS_DETAILS B INNER JOIN TRAVEL_DETAILS T ON B.BUS_ID = T.BUS_ID WHERE T.SOURCE_LOCATION=%s AND T.DESTINATION_LOCATION=%s AND T.SOURCE_DATE=%s',(source_location,destination_location,source_date))
                operator_result = mycursor.fetchall()
                count = len(result_with_bus_details)
                return render_template('search-bus.html', traveldetails = result_with_bus_details, operatordetails = operator_result, value = True, user_id = user_id, count=count, option=action)
            else:
                print('Nothing inside')
                return render_template('search-bus.html', value = False, option=action)
            
        if action == 'CheapFare':
            user_id = session.get('user_id')
            source_location = session['source_location']
            destination_location = session['destination_location']
            source_date = session['source_date']
            mycursor = mysql.connection.cursor()
            query = 'SELECT OPERATOR_NAME, SOURCE_LOCATION, DESTINATION_LOCATION, SOURCE_DATE, DESTINATION_DATE, SOURCE_TIME, DESTINATION_TIME, TOTAL_FARE, AVAILABLE_SEATS,  TRAVEL_ID, BUS_ID FROM TRAVEL_DETAILS WHERE SOURCE_LOCATION=%s AND DESTINATION_LOCATION=%s AND SOURCE_DATE=%s ORDER BY TOTAL_FARE ASC'
            values = (source_location,destination_location,source_date)
            mycursor.execute(query, values)
            result = mycursor.fetchall()
            if result:
                result_with_bus_details = []
                for row in result:
                    bus_id = row[10]
                    mycursor = mysql.connection.cursor()
                    mycursor.execute('SELECT BUS_TYPE, RECLINING_SEATS, CHARGING_POINTS, WIFI, BLANKETS_PILLOWS, SNACKS, MOVIE, READING_LIGHT, TRACK_MY_BUS, M_TICKET FROM BUS_DETAILS WHERE BUS_ID=%s',(bus_id,))
                    bus_details = mycursor.fetchall()
                    for bus in bus_details:
                        row = list(row)
                        row.append(bus[0])
                        row.append(bus[1])
                        row.append(bus[2])
                        row.append(bus[3])
                        row.append(bus[4])
                        row.append(bus[5])
                        row.append(bus[6])
                        row.append(bus[7])
                        row.append(bus[8])
                        row.append(bus[9])
                        mycursor.close()
                        tuple_row = tuple(row)
                        result_with_bus_details.append(tuple_row)
                mycursor.close()
                mycursor = mysql.connection.cursor()
                mycursor.execute('SELECT DISTINCT B.OPERATOR_NAME, B.BUS_NUMBER FROM BUS_DETAILS B INNER JOIN TRAVEL_DETAILS T ON B.BUS_ID = T.BUS_ID WHERE T.SOURCE_LOCATION=%s AND T.DESTINATION_LOCATION=%s AND T.SOURCE_DATE=%s',(source_location,destination_location,source_date))
                operator_result = mycursor.fetchall()
                count = len(result_with_bus_details)
                return render_template('search-bus.html', traveldetails = result_with_bus_details, operatordetails = operator_result, value = True, user_id = user_id, count=count, option=action)
            else:
                print('Nothing inside')
                return render_template('search-bus.html', value = False, option=action)
            
        if action == 'ExpensiveFare':
            user_id = session.get('user_id')
            source_location = session['source_location']
            destination_location = session['destination_location']
            source_date = session['source_date']
            mycursor = mysql.connection.cursor()
            query = 'SELECT OPERATOR_NAME, SOURCE_LOCATION, DESTINATION_LOCATION, SOURCE_DATE, DESTINATION_DATE, SOURCE_TIME, DESTINATION_TIME, TOTAL_FARE, AVAILABLE_SEATS,  TRAVEL_ID, BUS_ID FROM TRAVEL_DETAILS WHERE SOURCE_LOCATION=%s AND DESTINATION_LOCATION=%s AND SOURCE_DATE=%s ORDER BY TOTAL_FARE DESC'
            values = (source_location,destination_location,source_date)
            mycursor.execute(query, values)
            result = mycursor.fetchall()
            if result:
                result_with_bus_details = []
                for row in result:
                    bus_id = row[10]
                    mycursor = mysql.connection.cursor()
                    mycursor.execute('SELECT BUS_TYPE, RECLINING_SEATS, CHARGING_POINTS, WIFI, BLANKETS_PILLOWS, SNACKS, MOVIE, READING_LIGHT, TRACK_MY_BUS, M_TICKET FROM BUS_DETAILS WHERE BUS_ID=%s',(bus_id,))
                    bus_details = mycursor.fetchall()
                    for bus in bus_details:
                        row = list(row)
                        row.append(bus[0])
                        row.append(bus[1])
                        row.append(bus[2])
                        row.append(bus[3])
                        row.append(bus[4])
                        row.append(bus[5])
                        row.append(bus[6])
                        row.append(bus[7])
                        row.append(bus[8])
                        row.append(bus[9])
                        mycursor.close()
                        tuple_row = tuple(row)
                        result_with_bus_details.append(tuple_row)
                mycursor.close()
                mycursor = mysql.connection.cursor()
                mycursor.execute('SELECT DISTINCT B.OPERATOR_NAME, B.BUS_NUMBER FROM BUS_DETAILS B INNER JOIN TRAVEL_DETAILS T ON B.BUS_ID = T.BUS_ID WHERE T.SOURCE_LOCATION=%s AND T.DESTINATION_LOCATION=%s AND T.SOURCE_DATE=%s',(source_location,destination_location,source_date))
                operator_result = mycursor.fetchall()
                count = len(result_with_bus_details)
                return render_template('search-bus.html', traveldetails = result_with_bus_details, operatordetails = operator_result, value = True, user_id = user_id, count=count, option=action)
            else:
                print('Nothing inside')
                return render_template('search-bus.html', value = False, option=action)
            
        if action == 'LowSeats':
            user_id = session.get('user_id')
            source_location = session['source_location']
            destination_location = session['destination_location']
            source_date = session['source_date']
            mycursor = mysql.connection.cursor()
            query = 'SELECT OPERATOR_NAME, SOURCE_LOCATION, DESTINATION_LOCATION, SOURCE_DATE, DESTINATION_DATE, SOURCE_TIME, DESTINATION_TIME, TOTAL_FARE, AVAILABLE_SEATS,  TRAVEL_ID, BUS_ID FROM TRAVEL_DETAILS WHERE SOURCE_LOCATION=%s AND DESTINATION_LOCATION=%s AND SOURCE_DATE=%s ORDER BY AVAILABLE_SEATS ASC'
            values = (source_location,destination_location,source_date)
            mycursor.execute(query, values)
            result = mycursor.fetchall()
            if result:
                result_with_bus_details = []
                for row in result:
                    bus_id = row[10]
                    mycursor = mysql.connection.cursor()
                    mycursor.execute('SELECT BUS_TYPE, RECLINING_SEATS, CHARGING_POINTS, WIFI, BLANKETS_PILLOWS, SNACKS, MOVIE, READING_LIGHT, TRACK_MY_BUS, M_TICKET FROM BUS_DETAILS WHERE BUS_ID=%s',(bus_id,))
                    bus_details = mycursor.fetchall()
                    for bus in bus_details:
                        row = list(row)
                        row.append(bus[0])
                        row.append(bus[1])
                        row.append(bus[2])
                        row.append(bus[3])
                        row.append(bus[4])
                        row.append(bus[5])
                        row.append(bus[6])
                        row.append(bus[7])
                        row.append(bus[8])
                        row.append(bus[9])
                        mycursor.close()
                        tuple_row = tuple(row)
                        result_with_bus_details.append(tuple_row)
                mycursor.close()
                mycursor = mysql.connection.cursor()
                mycursor.execute('SELECT DISTINCT B.OPERATOR_NAME, B.BUS_NUMBER FROM BUS_DETAILS B INNER JOIN TRAVEL_DETAILS T ON B.BUS_ID = T.BUS_ID WHERE T.SOURCE_LOCATION=%s AND T.DESTINATION_LOCATION=%s AND T.SOURCE_DATE=%s',(source_location,destination_location,source_date))
                operator_result = mycursor.fetchall()
                count = len(result_with_bus_details)
                return render_template('search-bus.html', traveldetails = result_with_bus_details, operatordetails = operator_result, value = True, user_id = user_id, count=count, option=action)
            else:
                print('Nothing inside')
                return render_template('search-bus.html', value = False, option=action)
            
        if action == 'HighSeats':
            user_id = session.get('user_id')
            source_location = session['source_location']
            destination_location = session['destination_location']
            source_date = session['source_date']
            mycursor = mysql.connection.cursor()
            query = 'SELECT OPERATOR_NAME, SOURCE_LOCATION, DESTINATION_LOCATION, SOURCE_DATE, DESTINATION_DATE, SOURCE_TIME, DESTINATION_TIME, TOTAL_FARE, AVAILABLE_SEATS,  TRAVEL_ID, BUS_ID FROM TRAVEL_DETAILS WHERE SOURCE_LOCATION=%s AND DESTINATION_LOCATION=%s AND SOURCE_DATE=%s ORDER BY AVAILABLE_SEATS DESC'
            values = (source_location,destination_location,source_date)
            mycursor.execute(query, values)
            result = mycursor.fetchall()
            if result:
                result_with_bus_details = []
                for row in result:
                    bus_id = row[10]
                    mycursor = mysql.connection.cursor()
                    mycursor.execute('SELECT BUS_TYPE, RECLINING_SEATS, CHARGING_POINTS, WIFI, BLANKETS_PILLOWS, SNACKS, MOVIE, READING_LIGHT, TRACK_MY_BUS, M_TICKET FROM BUS_DETAILS WHERE BUS_ID=%s',(bus_id,))
                    bus_details = mycursor.fetchall()
                    for bus in bus_details:
                        row = list(row)
                        row.append(bus[0])
                        row.append(bus[1])
                        row.append(bus[2])
                        row.append(bus[3])
                        row.append(bus[4])
                        row.append(bus[5])
                        row.append(bus[6])
                        row.append(bus[7])
                        row.append(bus[8])
                        row.append(bus[9])
                        mycursor.close()
                        tuple_row = tuple(row)
                        result_with_bus_details.append(tuple_row)
                mycursor.close()
                mycursor = mysql.connection.cursor()
                mycursor.execute('SELECT DISTINCT B.OPERATOR_NAME, B.BUS_NUMBER FROM BUS_DETAILS B INNER JOIN TRAVEL_DETAILS T ON B.BUS_ID = T.BUS_ID WHERE T.SOURCE_LOCATION=%s AND T.DESTINATION_LOCATION=%s AND T.SOURCE_DATE=%s',(source_location,destination_location,source_date))
                operator_result = mycursor.fetchall()
                count = len(result_with_bus_details)
                return render_template('search-bus.html', traveldetails = result_with_bus_details, operatordetails = operator_result, value = True, user_id = user_id, count=count, option=action)
            else:
                print('Nothing inside')
                return render_template('search-bus.html', value = False, option=action)
            
        if action == 'ResetSort':
            user_id = session.get('user_id')
            source_location = session['source_location']
            destination_location = session['destination_location']
            source_date = session['source_date']
            mycursor = mysql.connection.cursor()
            query = 'SELECT OPERATOR_NAME, SOURCE_LOCATION, DESTINATION_LOCATION, SOURCE_DATE, DESTINATION_DATE, SOURCE_TIME, DESTINATION_TIME, TOTAL_FARE, AVAILABLE_SEATS,  TRAVEL_ID, BUS_ID FROM TRAVEL_DETAILS WHERE SOURCE_LOCATION=%s AND DESTINATION_LOCATION=%s AND SOURCE_DATE=%s'
            values = (source_location,destination_location,source_date)
            mycursor.execute(query, values)
            result = mycursor.fetchall()
            if result:
                result_with_bus_details = []
                for row in result:
                    bus_id = row[10]
                    mycursor = mysql.connection.cursor()
                    mycursor.execute('SELECT BUS_TYPE, RECLINING_SEATS, CHARGING_POINTS, WIFI, BLANKETS_PILLOWS, SNACKS, MOVIE, READING_LIGHT, TRACK_MY_BUS, M_TICKET FROM BUS_DETAILS WHERE BUS_ID=%s',(bus_id,))
                    bus_details = mycursor.fetchall()
                    for bus in bus_details:
                        row = list(row)
                        row.append(bus[0])
                        row.append(bus[1])
                        row.append(bus[2])
                        row.append(bus[3])
                        row.append(bus[4])
                        row.append(bus[5])
                        row.append(bus[6])
                        row.append(bus[7])
                        row.append(bus[8])
                        row.append(bus[9])
                        mycursor.close()
                        tuple_row = tuple(row)
                        result_with_bus_details.append(tuple_row)
                mycursor.close()
                mycursor = mysql.connection.cursor()
                mycursor.execute('SELECT DISTINCT B.OPERATOR_NAME, B.BUS_NUMBER FROM BUS_DETAILS B INNER JOIN TRAVEL_DETAILS T ON B.BUS_ID = T.BUS_ID WHERE T.SOURCE_LOCATION=%s AND T.DESTINATION_LOCATION=%s AND T.SOURCE_DATE=%s',(source_location,destination_location,source_date))
                operator_result = mycursor.fetchall()
                count = len(result_with_bus_details)
                return render_template('search-bus.html', traveldetails = result_with_bus_details, operatordetails = operator_result, value = True, user_id = user_id, count=count, option=action)
            else:
                print('Nothing inside')
                return render_template('search-bus.html', value = False, option=None)
        
        else:
            return render_template('search-bus.html')
        
    else:
        return render_template('search-bus.html')
    
@app.route('/bus-comparison', methods = ['GET', 'POST'])
def Comparison():
    compare_travel_id = request.args.getlist('compare_travel_id')
    comparison_count = len(compare_travel_id)
    if (comparison_count == 3):
        result_with_bus_details = []
        for travel_id in compare_travel_id:
            mycursor = mysql.connection.cursor()
            query = 'SELECT OPERATOR_NAME, SOURCE_LOCATION, DESTINATION_LOCATION, SOURCE_DATE, DESTINATION_DATE, SOURCE_TIME, DESTINATION_TIME, TOTAL_FARE, AVAILABLE_SEATS,  TRAVEL_ID, BUS_ID FROM TRAVEL_DETAILS WHERE TRAVEL_ID=%s'
            values = (travel_id,)
            mycursor.execute(query,values)
            result = mycursor.fetchall()
            bus_id = result[0][10]
            mycursor = mysql.connection.cursor()
            mycursor.execute('SELECT BUS_TYPE, RECLINING_SEATS, CHARGING_POINTS, WIFI, BLANKETS_PILLOWS, SNACKS, MOVIE, READING_LIGHT, TRACK_MY_BUS, M_TICKET FROM BUS_DETAILS WHERE BUS_ID=%s',(bus_id,))
            bus_details = mycursor.fetchall()
            result = list(result)
            result.append(bus_details[0][0])
            result.append(bus_details[0][1])
            result.append(bus_details[0][2])
            result.append(bus_details[0][3])
            result.append(bus_details[0][4])
            result.append(bus_details[0][5])
            result.append(bus_details[0][6])
            result.append(bus_details[0][7])
            result.append(bus_details[0][8])
            result.append(bus_details[0][9])
            mycursor.close()
            tuple_row = tuple(result)
            result_with_bus_details.append(tuple_row)
            mycursor.close()
        print(result_with_bus_details[0])
        print(result_with_bus_details[1])
        print(result_with_bus_details[2])
        return render_template('comparison(3).html', bus_details = result_with_bus_details)
    
    elif (comparison_count == 2):
        result_with_bus_details = []
        for travel_id in compare_travel_id:
            mycursor = mysql.connection.cursor()
            query = 'SELECT OPERATOR_NAME, SOURCE_LOCATION, DESTINATION_LOCATION, SOURCE_DATE, DESTINATION_DATE, SOURCE_TIME, DESTINATION_TIME, TOTAL_FARE, AVAILABLE_SEATS,  TRAVEL_ID, BUS_ID FROM TRAVEL_DETAILS WHERE TRAVEL_ID=%s'
            values = (travel_id,)
            mycursor.execute(query,values)
            result = mycursor.fetchall()
            bus_id = result[0][10]
            mycursor = mysql.connection.cursor()
            mycursor.execute('SELECT BUS_TYPE, RECLINING_SEATS, CHARGING_POINTS, WIFI, BLANKETS_PILLOWS, SNACKS, MOVIE, READING_LIGHT, TRACK_MY_BUS, M_TICKET FROM BUS_DETAILS WHERE BUS_ID=%s',(bus_id,))
            bus_details = mycursor.fetchall()
            result = list(result)
            result.append(bus_details[0][0])
            result.append(bus_details[0][1])
            result.append(bus_details[0][2])
            result.append(bus_details[0][3])
            result.append(bus_details[0][4])
            result.append(bus_details[0][5])
            result.append(bus_details[0][6])
            result.append(bus_details[0][7])
            result.append(bus_details[0][8])
            result.append(bus_details[0][9])
            mycursor.close()
            tuple_row = tuple(result)
            result_with_bus_details.append(tuple_row)
            mycursor.close()
        print(result_with_bus_details[0])
        print(result_with_bus_details[1])
        return render_template('comparison(2).html', bus_details = result_with_bus_details)
    else:
        return 'More than 3 buses have been selected. Check JavaScript!'
    
@app.route('/comparison')
def Comparison3():
    bus_details = request.args.getlist('bus_details')
    # print(bus_details)
    return render_template('comparison(3).html', bus_details = bus_details)
    
@app.route('/transaction-history', methods = ['GET','POST'])
def TransactionHistory():
    user_id = session['user_id']
    mycursor = mysql.connection.cursor()
    mycursor.execute('SELECT TRANSACTION_ID, AMOUNT, ACTION, BALANCE, DESCRIPTION, TRANSACTION_TIME FROM TRANSACTION_DETAILS WHERE USER_ID=%s ORDER BY TRANSACTION_TIME DESC',(user_id,))
    result = mycursor.fetchall()
    mycursor.close()
    return render_template('transaction-history.html', transactiondetails = result)

@app.route('/seat-selection', methods = ['GET','POST'])
def SeatSelection():
    travel_id = session['booking_travel_id']
    mycursor = mysql.connection.cursor()
    mycursor.execute("SELECT SEAT_NUMBER, SEAT_STATUS FROM SEAT_DETAILS WHERE TRAVEL_ID = %s",(travel_id,))
    result = mycursor.fetchall()
    mycursor.execute("SELECT SOURCE_LOCATION, DESTINATION_LOCATION, SOURCE_DATE, OPERATOR_NAME, TOTAL_FARE FROM TRAVEL_DETAILS WHERE TRAVEL_ID =%s",(travel_id,))
    result2 = mycursor.fetchall()
    return render_template("seat-selection.html", seatdetails = result, traveldetails = result2)
    
@app.route('/passenger-details', methods = ['GET','POST'])
def PassengerDetails():
    user_id = session['user_id']
    travel_id = session['booking_travel_id']
    if request.method == 'POST':
        action = request.form['action']
        if action == 'SeatSelection':
            selected_seats = request.form.get('selectedseats')
            selected_seats_parsed = json.loads(selected_seats)
            session['booking_selected_seats'] = selected_seats_parsed
            print(selected_seats_parsed)
            selected_seats = selected_seats.replace('[','').replace(']','').replace('"','')
            session['booking_passenger_seats'] = selected_seats
            temporary_seats = [int(i) for i in selected_seats.split(",")]
            passenger_count = len(temporary_seats)
            session['booking_passenger_count'] = passenger_count
            print(f'Selected Seat Numbers: {temporary_seats}')
            print(f'Number of passegers: {passenger_count}')
            i=1
            for passenger in temporary_seats:
                seat_status = 'Temporary'
                mycursor = mysql.connection.cursor()
                mycursor.execute('UPDATE SEAT_DETAILS SET USER_ID=%s, SEAT_STATUS=%s WHERE TRAVEL_ID=%s AND SEAT_NUMBER=%s',(user_id,seat_status,travel_id,passenger))
                mycursor.execute('SELECT AVAILABLE_SEATS, TEMPORARY_SEATS FROM TRAVEL_DETAILS WHERE TRAVEL_ID=%s',(travel_id,))
                result = mycursor.fetchall()
                for row in result:
                    available_seats_db = row[0]
                    temporary_seats_db = row[1]
                available_seats_db = available_seats_db - i
                temporary_seats_db = temporary_seats_db + i
                mycursor.execute('UPDATE TRAVEL_DETAILS SET AVAILABLE_SEATS=%s, TEMPORARY_SEATS=%s WHERE TRAVEL_ID=%s',(available_seats_db,temporary_seats_db,travel_id))
                mysql.connection.commit()
                mycursor.close()
            return render_template('passenger-details.html', temporary_seats=temporary_seats, passenger_count=passenger_count)
        
        if action == 'AddPassengerDetails':
            passenger_details_object = request.form.get('passengerdetails')
            passenger_details_parsed = json.loads(passenger_details_object)
            session['booking_passenger_details'] = passenger_details_parsed
            selected_seats_parsed = session['booking_selected_seats']
            user_id = session['user_id']
            travel_id = session['booking_travel_id']
            mycursor = mysql.connection.cursor()
            mycursor.execute('SELECT TOTAL_FARE FROM TRAVEL_DETAILS WHERE TRAVEL_ID=%s',(travel_id,))
            result = mycursor.fetchall()
            for row in result:
                fare = row[0]
            passenger_count = session['booking_passenger_count']
            total_fare = fare * passenger_count     
            mycursor.execute('INSERT INTO BOOKING_DETAILS (USER_ID,TRAVEL_ID,PASSENGERS,TOTAL_FARE) VALUES (%s,%s,%s,%s)',(user_id,travel_id,passenger_count,total_fare))
            returning = mycursor.execute('SELECT LAST_INSERT_ID() AS BOOKING_ID')
            returning = mycursor.fetchall()
            for row in returning:
                booking_id = row[0]
            session['booking_booking_id'] = booking_id
            mysql.connection.commit()
            for i, passengers_details in enumerate(passenger_details_parsed):
                first_name = passengers_details['first_name']
                last_name = passengers_details['last_name']
                age = passengers_details['age']
                gender = passengers_details['gender']
                seat_number = selected_seats_parsed[i]
                mycursor.execute('INSERT INTO PASSENGER_DETAILS (BOOKING_ID,TRAVEL_ID,SEAT_NUMBER,FIRST_NAME,LAST_NAME,AGE,GENDER) VALUES (%s,%s,%s,%s,%s,%s,%s)',(booking_id,travel_id,seat_number,first_name,last_name,age,gender))
                mysql.connection.commit()
            mycursor.close()
            return redirect(url_for('PaymentGateway'))

        else:
            return redirect(url_for('SeatSelection'))
    else:
        return redirect(url_for('SeatSelection'))
    
@app.route('/session-data')
def session_data():
    if session['user_power'] != 'Admin':
        return redirect(url_for('HomePage'))
    
    else:
        session_data = []
        for key, value in session.items():
            session_data.append((key, value))
        return render_template('session-data.html', session_data=session_data)

@app.route('/payment-gateway', methods = ['GET','POST'])
def PaymentGateway():
    if request.method=='POST':
        action = request.form['action']
        if action == 'Wallet':
            total_fare = request.form['total_fare']
            user_id = session['user_id']
            booking_id = session['booking_booking_id']
            mycursor = mysql.connection.cursor()
            mycursor.execute("UPDATE USER_CREDENTIALS SET WALLET = WALLET - %s WHERE USER_ID = %s",(total_fare,user_id))
            mysql.connection.commit()
            mycursor.execute('SELECT WALLET FROM USER_CREDENTIALS WHERE USER_ID=%s',(user_id,))
            result = mycursor.fetchall()
            balance = result[0][0]
            action = 'Debit'
            description = 'Deducting money for ticket reservation'
            mycursor.execute("INSERT INTO TRANSACTION_DETAILS (USER_ID, AMOUNT, ACTION, BALANCE, DESCRIPTION) VALUES (%s,%s,%s,%s,%s)",(user_id,total_fare,action,balance,description))
            mysql.connection.commit()
            payment_status = 'Completed'
            booking_status = 'Confirmed'
            mycursor.execute("UPDATE BOOKING_DETAILS SET PAYMENT_STATUS=%s, BOOKING_STATUS=%s WHERE USER_ID=%s AND BOOKING_ID=%s",(payment_status,booking_status,user_id,booking_id))
            mysql.connection.commit()
            travel_id = session['booking_travel_id']
            mycursor.execute('SELECT BOOKED_SEATS, TEMPORARY_SEATS FROM TRAVEL_DETAILS WHERE TRAVEL_ID=%s',(travel_id,))
            result = mycursor.fetchall()
            for row in result:
                booked_seats_db = row[0]
                temporary_seats_db = row[1]
            booked_seats_db = booked_seats_db + session['booking_passenger_count']
            temporary_seats_db = temporary_seats_db - session['booking_passenger_count']
            mycursor.execute('UPDATE TRAVEL_DETAILS SET BOOKED_SEATS=%s, TEMPORARY_SEATS=%s WHERE TRAVEL_ID=%s',(booked_seats_db,temporary_seats_db,travel_id))
            mysql.connection.commit()
            status = 'Booked'
            completed_seats = session['booking_selected_seats']
            for seat in completed_seats:
                seat_number = seat
                mycursor.execute('UPDATE SEAT_DETAILS SET SEAT_STATUS=%s WHERE SEAT_NUMBER=%s AND TRAVEL_ID=%s',(status,seat_number,travel_id))
            mysql.connection.commit()
            mycursor.close()
            return redirect(url_for('BookingHistory'))
        else:
            return redirect(url_for('PaymentGateway'))

    else:
        travel_id = session['booking_travel_id']
        booking_id = session['booking_booking_id']
        mycursor = mysql.connection.cursor()
        mycursor.execute('SELECT BD.OPERATOR_NAME,BD.BUS_NUMBER,TD.SOURCE_LOCATION,TD.DESTINATION_LOCATION,TD.SOURCE_DATE,TD.DESTINATION_DATE,TD.SOURCE_TIME,TD.DESTINATION_TIME,TD.TOTAL_FARE FROM BUS_DETAILS BD INNER JOIN TRAVEL_DETAILS TD ON BD.BUS_ID = TD.BUS_ID WHERE TD.TRAVEL_ID=%s',(travel_id,))
        result1 = mycursor.fetchall()
        mycursor.execute('SELECT TOTAL_FARE, PASSENGERS FROM BOOKING_DETAILS WHERE BOOKING_ID=%s',(booking_id,))
        result2 = mycursor.fetchall()
        mycursor.execute('SELECT FIRST_NAME, LAST_NAME, AGE, GENDER FROM PASSENGER_DETAILS WHERE BOOKING_ID=%s AND TRAVEL_ID=%s',(booking_id,travel_id))
        result3 = mycursor.fetchall()
        mycursor.close()
        return render_template('payment-gateway.html', booking_id = booking_id, details1 = result1, details2 = result2, details3 = result3)
    
@app.route('/booking-history', methods=['GET','POST'])
def BookingHistory():
    if request.method=='POST':
        action = request.form['action']
        if action == 'ViewTicket':
            booking_id = request.form['booking_id']
            mycursor = mysql.connection.cursor()
            mycursor.execute('SELECT TRAVEL_ID FROM BOOKING_DETAILS WHERE BOOKING_ID=%s',(booking_id,))
            result = mycursor.fetchall()
            travel_id = result[0][0]
            mycursor = mysql.connection.cursor()
            mycursor.execute('SELECT BD.OPERATOR_NAME,BD.BUS_NUMBER,TD.SOURCE_LOCATION,TD.DESTINATION_LOCATION,TD.SOURCE_DATE,TD.DESTINATION_DATE,TD.SOURCE_TIME,TD.DESTINATION_TIME,TD.TOTAL_FARE, BD.BUS_TYPE FROM BUS_DETAILS BD INNER JOIN TRAVEL_DETAILS TD ON BD.BUS_ID = TD.BUS_ID WHERE TD.TRAVEL_ID=%s',(travel_id,))
            result1 = mycursor.fetchall()
            mycursor.execute('SELECT TOTAL_FARE, PASSENGERS, PAYMENT_STATUS, BOOKING_STATUS FROM BOOKING_DETAILS WHERE BOOKING_ID=%s',(booking_id,))
            result2 = mycursor.fetchall()
            mycursor.execute('SELECT FIRST_NAME, LAST_NAME, AGE, GENDER FROM PASSENGER_DETAILS WHERE BOOKING_ID=%s AND TRAVEL_ID=%s',(booking_id,travel_id))
            result3 = mycursor.fetchall()
            mycursor.close()
            return render_template('ticket-view.html', booking_id = booking_id, details1 = result1, details2 = result2, details3 = result3)

        elif action == 'CancelTicket':
            booking_id = request.form['booking_id']
            print(booking_id)
            user_id = session['user_id']
            mycursor = mysql.connection.cursor()
            mycursor.execute('SELECT TOTAL_FARE, PASSENGERS, TRAVEL_ID FROM BOOKING_DETAILS WHERE BOOKING_ID=%s',(booking_id,))
            result = mycursor.fetchall()
            total_fare = result[0][0]
            passengers_count = result[0][1]
            travel_id = result[0][2]
            mycursor.execute('SELECT SEAT_NUMBER FROM PASSENGER_DETAILS WHERE BOOKING_ID=%s',(booking_id,))
            result = mycursor.fetchall()
            seats = []
            for i in range(passengers_count):
                seats.append(result[i][0])
            # mycursor.execute('DELETE FROM PASSENGER_DETAILS WHERE BOOKING_ID=%s',(booking_id,))
            # mysql.connection.commit()
            # mycursor.execute('DELETE FROM BOOKING_DETAILS WHERE BOOKING_ID=%s',(booking_id,))
            # mysql.connection.commit()
            seat_status = 'Available'
            update_user_id = 0
            for i in range(passengers_count):
                seat_number = seats[i]
                mycursor.execute('UPDATE SEAT_DETAILS SET SEAT_STATUS=%s, USER_ID=%s WHERE SEAT_NUMBER=%s AND TRAVEL_ID=%s',(seat_status,update_user_id,seat_number,travel_id))
                mysql.connection.commit()
            mycursor.execute('SELECT AVAILABLE_SEATS, BOOKED_SEATS FROM TRAVEL_DETAILS WHERE TRAVEL_ID=%s',(travel_id,))
            result = mycursor.fetchall()
            available_seats_db = result[0][0]
            booked_seats_db = result[0][1]
            available_seats_db = available_seats_db + passengers_count
            booked_seats_db = booked_seats_db - passengers_count
            mycursor.execute('UPDATE TRAVEL_DETAILS SET AVAILABLE_SEATS=%s, BOOKED_SEATS=%s WHERE TRAVEL_ID=%s',(available_seats_db,booked_seats_db,travel_id,))
            mysql.connection.commit()
            mycursor.execute('UPDATE USER_CREDENTIALS SET WALLET=WALLET+%s WHERE USER_ID=%s',(total_fare,user_id))
            mysql.connection.commit()
            mycursor.execute('SELECT WALLET FROM USER_CREDENTIALS WHERE USER_ID=%s',(user_id,))
            result = mycursor.fetchall()
            balance = result[0][0]
            action = 'Credit'
            description = 'Crediting cancelled ticket fare'
            mycursor.execute("INSERT INTO TRANSACTION_DETAILS (USER_ID, AMOUNT, ACTION, BALANCE, DESCRIPTION) VALUES (%s,%s,%s,%s,%s)",(user_id,total_fare,action,balance,description))
            mysql.connection.commit()
            payment_status = 'Refunded'
            booking_status = 'Cancelled'
            mycursor.execute("UPDATE BOOKING_DETAILS SET PAYMENT_STATUS=%s, BOOKING_STATUS=%s WHERE BOOKING_ID=%s AND USER_ID=%s",(payment_status,booking_status,booking_id,user_id))
            mysql.connection.commit()
            return redirect(url_for('BookingHistory'))
        else:
            print("Error")
            user_id = session['user_id']
            mycursor = mysql.connection.cursor()
            mycursor.execute('SELECT BOOKING_ID, PASSENGERS, TOTAL_FARE, PAYMENT_STATUS, BOOKING_STATUS FROM BOOKING_DETAILS WHERE USER_ID=%s',(user_id,))
            result = mycursor.fetchall()
            return render_template('booking-history.html',booking_details=result)

    else:
        user_id = session['user_id']
        mycursor = mysql.connection.cursor()
        mycursor.execute('SELECT BOOKING_ID, PASSENGERS, TOTAL_FARE, PAYMENT_STATUS, BOOKING_STATUS FROM BOOKING_DETAILS WHERE USER_ID=%s',(user_id,))
        result = mycursor.fetchall()
        return render_template('booking-history.html',booking_details=result)

@app.route('/about-us', methods=['GET','POST'])
def AboutUs():
    return render_template('about-us.html')


if __name__ == '__main__':
    app.run(debug=True)

# Pending work - Filters, Sorting, Pickup Locations, Drop Locations