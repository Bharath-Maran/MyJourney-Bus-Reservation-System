from setup import app, mysql, session, render_template, redirect, request, url_for, json, jsonify

#--------------|CLASS DECLARATION|--------------#
from classes.admin import Admin
from classes.booking import Booking
from classes.bus import Bus
from classes.passenger import Passenger
from classes.paymentmanager import PaymentManager
from classes.seat import Seat
from classes.travel import Travel
from classes.user import User

#--------------|COMMON DASHBOARD|--------------#

@app.route('/dummy')
def Dummy():
    return render_template('dummy.html')

#Default url of the web application.
@app.route('/')
def Initial():
    session['redirect_searchbus'] = False
    #Redirects the default url to the html page we need to display.
    return redirect(url_for('HomePage'))

#Renders the homepage of the web application.
@app.route('/home')
def HomePage():
    if 'redirect_searchbus' not in session:
        session['redirect_searchbus'] = False
        return render_template('homepage.html')
    else:
        if session['redirect_searchbus']:
            return redirect(url_for('SearchBus'))
        else:
            session['redirect_searchbus'] = False
            return render_template('homepage.html')

#User registration.
@app.route('/register', methods = ['GET', 'POST'])
def Registration():
    #Enters into the below if code if the request method in submitted form is 'POST'.
    if request.method == 'POST':

        #Gets the details submitted by the user in the form in HTML page.
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        dob = request.form['dob']
        gender = request.form['gender']
        email = request.form['email']
        phone_number = request.form['phone_number']
        username = request.form['username']
        password = request.form['password']

        #Creates an instance using all the details passed by the user.
        user = User("","","",first_name, last_name, dob, gender, email, phone_number, username, password)

        #Triggers the 'Register' method of the class 'User' using the instance 'user'.
        result = user.Register()

        #Checks if the result of the method is True or False.
        if result:
            print("Registration | User registration successful.")
            #Redirects the user to the 'Login' page.
            return redirect(url_for('LoggingIn'))
        else:
            #Redirects the user back to the 'Registration' page
            return redirect(url_for('Registration'))
    
    else:
        #If the request method is not 'POST' the 'Registration' page is loaded.
        return render_template('register.html')

#User login.
@app.route('/login', methods = ['GET', 'POST'])
def LoggingIn():
    #Enters into the below if code if the request method in submitted form is 'POST'.
    if request.method == 'POST':
        action = request.form['action']
        if action == 'Login':
            #Gets the details submitted by the user in the form in HTML page.
            username = request.form['username']
            password = request.form['password']

            #Creates an instance using all the details passed by the user.
            user = User("","","","","","","","","",username, password)

            #Triggers the 'Login' method of the class 'User' using the instance 'user'.
            result, statement = user.Login()

            #Checks if the result of the method is True or False.
            if result:
                print("LoggingIn | Login successful.")
                #Redirects the user to the 'HomePage' page.
                # return redirect(url_for('HomePage'))
                print(session['redirect_searchbus'])
                if session['redirect_searchbus']:
                    return(redirect(url_for('SearchBus')))
                else:
                    return render_template('homepage.html', login_statement = statement)
            else:
                #Redirects the user back to the 'Login' page
                return redirect(url_for('LoggingIn'))
        if action == 'Register':
            return redirect(url_for('Registration'))
        
        else:
            print('LoggingIn | Invalid action command.')
            return redirect(url_for('LoggingIn'))
    else:
        if 'redirect_searchbus' not in session:
            session['redirect_searchbus'] = False
        #If the request method is not 'POST' the 'Login' page is loaded.
        return render_template('login.html')
          
#User logout.
@app.route('/logout', methods = ['GET', 'POST'])
def Logout():
    #All the session data is cleared.
    session.clear()
    print("Logout | Session data cleared successfully.")
    #The user is redirected to the 'Login' page.
    return redirect(url_for('LoggingIn'))

#User profile options.
@app.route('/profile', methods = ['GET', 'POST'])
def Profile():
    #Enters into the below if code if the request method in submitted form is 'POST'.
    if request.method == 'POST':

        #The action is the name of the button that holds some value assigned to it. (There are multiple buttons with different values.)
        action = request.form['action']

        #If the action of the button submitted is 'DisableAccount'.
        if action == 'DisableAccount':

            #The user ID stored in the session is accessed.
            user_id = session['user_id']

            #Creates an instance using the user ID.
            user = User(user_id,'','','','','','','','','','')

            #Triggers the 'DeactivateProfile' method of the class 'User' using the instance 'user'.
            result = user.DeactivateProfile()

            #Checks if the result of the method is True or False.
            if result:
                print("Profile | Deactivation successful.")
                #Redirects the user back to the 'Login' page.
                return redirect(url_for('LoggingIn'))
            else:
                print("Profile | Failed to deactivate account.")
                #The user remain in the 'Profile' page.
                return render_template('profile.html')
            
        else:
            #If the request method is not 'POST' the 'Profile' page is loaded.
            print("Profile | Invalid action command.")
            return render_template('profile.html')
        
    #Checks if the user ID in session.
    elif 'user_id' in session:

        #The user ID is retrieved from the session data.
        user_id = session['user_id']

        #An instance of class 'User' is created and assigned to the object 'user'.
        user = User(user_id,'','','','','','','','','','')

        #Triggers the 'Profile' method to fetch all the profile details to be displayed in the HTML page.
        result = user.Profile()

        #Checks if the result contains data or not.
        if result:
            #Renders the profile by filling in all the profile details in HTML.
            return render_template('profile.html', details = result)
        else:
            #Renders the profile with blank HTML without profile data.
            print("Profile | Failed to fetch profile details from DB.")
            return render_template('profile.html')
        
    #If user ID is not in session, it indicates that the user has not yet logged in.
    else:
        #The user is redirected to 'Login' page.
        return redirect(url_for('LoggingIn'))
    
#--------------|USER DASHBOARD|--------------#

#Bus search and sorting features.
@app.route('/search-bus', methods = ['GET', 'POST'])
def SearchBus():
    #Enters into the below if code if the request method in submitted form is 'POST'.
    if request.method == 'POST':

        #The action is the name of the button that holds some value assigned to it. (There are multiple buttons with different values.)
        action = request.form['action']

        #Redirects the user to login if not logged in.
        if action == 'RedirectLogin':
            session['redirect_searchbus'] = True
            return redirect(url_for('LoggingIn'))

        #Executes if the action value is 'SearchBus'.
        if action == 'SearchBus':
            user_id = session.get('user_id')

            #The travel preference of the user is fetched from the HTML form.
            source_location = request.form['source_location']
            destination_location = request.form['destination_location']
            source_date = request.form['source_date']

            #The user preference is stored in session for future use in seat selection, booking etc.
            session['source_location'] = source_location
            session['destination_location'] = destination_location
            session['source_date'] = source_date 

            #Creates an empty instance of the class.
            bus = Bus('','','','','','','','','','','','','','','','')

            #Triggers the 'SearchBus' method of the class.
            result = bus.SearchBus(action)

            #Checks if the result of the method is 'True' or 'False'.
            if result:
                #Counts the len of the result i.e length of the tuple.
                count = len(result)
                #Travel_details holds the bus result.
                #count holds the number of buses found.
                #value is True, as the buses are available for displaying.
                #User ID is passed to enable / disable 'Compare' and 'Select Seats' feature.
                return render_template('search-bus.html', travel_details = result, count = count, value = True, user_id = user_id)
            else:
                #Value is False, as the buses are not available.
                return render_template('search-bus.html', value = False)
        
        #Each action passed contains a sorting feature that has to be executed.
        if ((action == 'EarlyDeparture') or (action == 'LateDeparture') or (action == 'EarlyArrival') or (action == 'LateArrival') or (action == 'CheapFare') or (action == 'ExpensiveFare') or (action == 'LowSeats') or (action == 'HighSeats')) or (action == 'ResetSort'):
            user_id = session.get('user_id')
            bus = Bus('','','','','','','','','','','','','','','','')
            result = bus.SearchBus(action)
            if result:
                search_result = result
                count = len(search_result)
                return render_template('search-bus.html', travel_details = search_result, count = count, value = True, user_id = user_id, option = action)
            else:
                return render_template('search-bus.html', value = False, option = action)
            
        #The 'SelectSeat' is passed to fetch the seat counts of a specific travel detail.
        if action == 'SelectSeat':
            #The button clicked by the user sends the value assigned to it i.e travel ID through the HTML form.
            travel_id = request.form['travel_id']

            #The user may or may not book the ticket, the travel ID is stored in session for future use. If the user does not book, and the browser is closed the session data will be cleared.
            session['booking_travel_id'] = travel_id
            session['action'] = action

            #An instance of the class 'Seat' is created and is assigned to the object 'seat'.
            seat = Seat('','','','','','')

            #Triggers the 'SeatSelection' method of the class 'Seat' to fetch all the seat details for visualisation to the user.
            result = seat.SeatSelection(travel_id, action)

            #Checks the if seat data is available or not.
            if result:
                #The tuple data 'Result' is unpacked into two variables 'seat_result' and 'travel_result'
                seat_result, travel_result = result
                #Seat result contains seat number, status from seat DB.
                #Travel result contains source location, destination location, source date, fare from travel DB.
                return render_template('seat-selection.html', seat_details = seat_result, travel_details = travel_result)
            else:
                #If the seat details does not exist, the user will be redirected back to the 'search bus' page.
                print('SeatSelection | Booking has not been initiated yet.')
                return redirect(url_for('SearchBus'))
            
        if action == 'CompareNow':
            json_data = request.form['CompareOptions']
            compare_options = json.loads(json_data)
            final_result = []
            if(len(compare_options)==3):
                for travel_id in compare_options:
                    travel = Travel(travel_id,'','','','','','','','','','','','','','')
                    result = travel.UserBusSearch(action)
                    if result:
                        final_result.append(result)
                    else:
                        return render_template('search-bus.html')
                if final_result:
                    return render_template('comparison-3.html',bus_details = final_result)
                else:
                    return render_template('search-bus.html')
                
            if(len(compare_options)==2):
                for travel_id in compare_options:
                    travel = Travel(travel_id,'','','','','','','','','','','','','','')
                    result = travel.UserBusSearch(action)
                    if result:
                        final_result.append(result)
                    else:
                        return render_template('search-bus.html')
                if final_result:
                    return render_template('comparison-2.html',bus_details = final_result)
                else:
                    return render_template('search-bus.html')
                
            else:
                return 'More than 3 buses have been selected. Check JavaScript!'
            
        if action == 'Filters':
            json_data = request.form['selected_options']
            filter_options = json.loads(json_data)
            return render_template('search-bus.html', filter_options = filter_options)

        else:
            #Executes if the action command is not listed in 'if'. (Might not occur unless HTML is modified)
            print('SearchBus | Invalid action command.')
            return render_template('search-bus.html')
        
    else:
        if session['redirect_searchbus']:
            user_id = session.get('user_id')
            source_location =  session['source_location']
            destination_location = session['destination_location']
            source_date =  session['source_date']

            #Creates an empty instance of the class.
            bus = Bus('','','','','','','','','','','','','','','','')

            #Triggers the 'SearchBus' method of the class.
            result = bus.SearchBus('SearchBus')

            #Checks if the result of the method is 'True' or 'False'.
            if result:
                #Counts the len of the result i.e length of the tuple.
                count = len(result)
                #Travel_details holds the bus result.
                #count holds the number of buses found.
                #value is True, as the buses are available for displaying.
                #User ID is passed to enable / disable 'Compare' and 'Select Seats' feature.
                return render_template('search-bus.html', travel_details = result, count = count, value = True, user_id = user_id)
            else:
                #Value is False, as the buses are not available.
                return render_template('search-bus.html', value = False)
        else:
            return render_template('search-bus.html')
    
@app.route('/filter', methods = ['GET', 'POST'])
def filter():
    checkbox_value = request.get_json()['checkbox_value']
    bus = Bus('','','','','','','','','','','','','','','','')
    data = bus.SearchBus(checkbox_value)
    data = json.dumps(data, default=serialize)
    if data:
        print(data)
        return jsonify(data)
    else:
        return jsonify(False)

#Passenger form for booking.
@app.route('/seat-selection/passenger-details', methods = ['GET', 'POST'])
def PassengerDetails():

    #Stores the user ID and booking travel ID from the session for use in the below codes.
    user_id = session['user_id']
    travel_id = session['booking_travel_id']

    #Enters into the below if code if the request method in submitted form is 'POST'.
    if request.method == 'POST':

        #The action is the name of the button that holds some value assigned to it. (There are multiple buttons with different values.) 
        action = request.form['action']

        #Executed to update the seat status and count of the selected seats.
        if action == 'SeatSelection':

            #The selected seats is received in the form of JSON data.
            json_data = request.form.get('selectedseats')
            #The JSON data is converted in to List using json.loads() function.
            selected_seats = json.loads(json_data)
            #The length of the list is found, it is the passenger count.
            passenger_count = len(selected_seats)

            #The selected seats and the passenger count is stored in session data for future use.
            session['booking_selected_seats'] = selected_seats
            session['booking_passenger_count'] = passenger_count
            print(f'Selected Seat Numbers: {selected_seats}')
            print(f'Number of passegers: {passenger_count}')

            #An instance of the class 'Seat' is created and assigned to the object 'seat'.
            seat = Seat('','','','','','')

            #Triggers the 'SeatTemporaryReservation' method of class 'Seat' to assign the status of seats to temporary. 
            #Updating status prevents other users from interfering the booking process.
            result = seat.SeatTemporaryReservation(user_id, travel_id, selected_seats,passenger_count)

            #Checks the status of seat status assigning.
            if result:
                #Renders the 'passenger-details' HTML for the user to fill passenger details.
                #Selected Seats contains the selected seat numbers.
                #Passenger count contains the number of passengers.
                return render_template('passenger-details.html', selected_seats = selected_seats, passenger_count = passenger_count)
            else:
                #If the seat status updation failed, the user is redirected back to the 'SeatSelection' page containing seat visualisation.
                print("Seat Selection | Failed to update the status of selected seats.")
                return redirect(url_for('SeatSelection'))

        #Executed to add the passenger details in the DB.
        if action == 'AddPassengerDetails':

            #Seat Numbers, Passenger Count, and Travel ID is assigned to variables from session data.
            selected_seats = session['booking_selected_seats']
            passenger_count = session['booking_passenger_count']
            travel_id = session['booking_travel_id']

            #The passenger details submitted by the form has to be stored in a list within a list. Eg. [[1],[2],[3]] where 1,2,3 - Indicates the passenger number.
            passenger_details = []
            for i in range(passenger_count):
                
                #The passenger details from the form is assigned to variables.
                first_name = request.form[f'first_name_{i}']
                last_name = request.form[f'last_name_{i}']
                age = request.form[f'age_{i}']
                gender = request.form[f'gender_{i}']

                #The variables are then assigned to list. The list is appended into the 'Passenger Details' list.
                temporary = []
                temporary = [first_name,last_name,age,gender]
                passenger_details.append(temporary)

            #Instance of class 'Travel' is created using Travel ID and is assigned to object 'travel'.
            travel = Travel(travel_id,'','','','','','','','','','','','','','')

            #Triggers 'UserBusSaerch' to fetch the travel details required for booking.
            result = travel.UserBusSearch('TicketBooking')
            if result:
                #The individual fare of the travel is stored in a variable.
                individual_fare = result[0][7]
            else:
                return redirect(url_for('SeatSelection'))
            
            #Total fare of the ticket is individual fare multiplied by the total passenger count.
            total_fare = individual_fare * passenger_count

            #Instance of class 'Booking' is created using available values and is assigned to object 'booking'.
            booking = Booking('',user_id,travel_id,passenger_count,total_fare,'','')

            #Triggers 'AddBookingDetails' to add the booking details to DB.
            result = booking.AddBookingDetails()
            if result:
                #Upon insertion, the booking ID is passed as return and it is stored in session.
                booking_id = result
                session['booking_id'] = booking_id
            else:
                return redirect(url_for('SeatSelection'))
            
            #Iteration: Used to calculate the number of iterations executed.
            iteration = 0

            #The passengers and seat are zipped into a tuple.
            for passengers, seat in zip(passenger_details, selected_seats):
                #The passenger details and a seat number is assigned for each iteration.
                first_name = passengers[0]
                last_name = passengers[1]
                age = passengers[2]
                gender = passengers[3]
                seat_number = seat

                #An instance of class 'Passenger' is created using the passenger details and assigned to object 'passenger'.
                passenger = Passenger('',booking_id,travel_id,seat_number,first_name,last_name,age,gender)

                #Triggers 'AddPassengerDetails' to add the passenger detail into the DB.
                result = passenger.AddPassengerDetails()
                if result:
                    #Iteration is incremented upon successful insertion.
                    iteration += 1
                    print(f'PassengerDetails | Passenger Form {iteration} added to DB.')
                else:
                    return redirect(url_for('SeatSelection'))
                
            #The iteration and passenger count is compared to confirm if all the details are iterated and added to DB.
            if iteration == passenger_count:
                #The user is redirected to the 'Booking Payment' page.
                print('PassengerDetails | All passenger details added to DB.')
                return redirect(url_for('BookingPayment'))
            else:
                #The user is redirected back to the 'Seat Selection' page.
                print('PassengerDetails | Failed to add passenger details to DB.')
                return redirect(url_for('SeatSelection'))
            
        else:
            #Incase of invalid action value, the user is redirected to the 'Seat Selection' page.
            print('PassengerDetails | Invalid action command.')
            return redirect(url_for('SeatSelection'))
        
    else:
        #If the request method is not post, the user is redirected to the 'Seat Selection' page.
        return redirect(url_for('SeatSelection'))
        # return render_template('passenger-details.html')

#Ticket confirmation payment process.
@app.route('/passenger-details/booking-payment', methods = ['GET','POST'])
def BookingPayment():
    #Enters into the below if code if the request method in submitted form is 'POST'.
    if request.method == 'POST':

        #The action is the name of the button that holds some value assigned to it. (There are multiple buttons with different values.) 
        action = request.form['action']

        #Executed to pay the fare and confirm the ticket.
        if action == 'Wallet':

            #Gets the total fare detail when user clicks the 'Wallet Payment' button.
            total_fare = request.form['total_fare']

            #All the essential details to be inserted in DB is obtained from the session data.
            user_id = session['user_id']
            booking_id = session['booking_id']
            travel_id = session['booking_travel_id']
            selected_seats = session['booking_selected_seats']
            passenger_count = session['booking_passenger_count']

            #An instance of class 'PaymentManager' is created and is assigned to object 'payment_manager'.
            payment_manager = PaymentManager(user_id,'','','','','','','')

            #Triggers 'Transaction(sender, receiver, amount, action)' to process payment.
            result = payment_manager.Transaction('Wallet','MyJourney',total_fare,'Debit')
            if result:

                #Upon successful payment, the booking and payment status has to be updated in the booking details DB.
                #An instance of class 'Booking' is created and is assigned to object 'booking'.
                booking = Booking(booking_id,user_id,travel_id,'','','Processed','Confirmed')

                #Triggers 'UpdateBookingDetails' which updates the payment and booking status.
                result = booking.UpdateBookingDetails()
                if result:

                    #Upon successful updation of booking status, the seat status has to be updated.
                    #The selected seat list is traversed and each seat status is updated.
                    for seat_number in selected_seats:

                        #An instance of class 'Seat' is created using the available values and is assigned to object 'seat'.
                        seat = Seat('',travel_id,'',user_id,seat_number,'Booked')
                        #Triggers 'UpdateSeat' which updates the status of the seat.
                        result = seat.UpdateSeat()
                        
                    #An instance of class 'Travel' is created using the travel ID and is assigned to object 'travel'.
                    travel = Travel(travel_id,'','','','','','','','','','','','','','')
                    #Triggers 'SeatCountUpdation', whose action value is 'Fetch'. It fetches the seat count in travel details DB.
                    result = travel.SeatCountUpdation('Fetch')
                    if result:
                        #The seat counts are assigned to variables.
                        available_seats_db = result[0][0]
                        booked_seats_db = result[0][1]
                        temporary_seats_db = result[0][2]

                        #The seat count is updated using the passenger count (Temporary -> Booked)
                        booked_seats_db = booked_seats_db + passenger_count
                        temporary_seats_db = temporary_seats_db - passenger_count

                        #An instance of class 'Travel' is created using the updated seat counts and is assigned to object 'travel'.
                        travel = Travel(travel_id,'','','','','','','','','','','',available_seats_db,booked_seats_db,temporary_seats_db)
                        #Triggers 'SeatCountUpdation' method, whose action value is 'Update'. It updates the seat count in travel details DB.
                        result = travel.SeatCountUpdation('Update')

                        #Checks if the updation is successful.
                        if result:
                            #Redirects the user to the 'HomePage'.
                            print('BookingPayment | Ticket booked.')
                            return redirect(url_for('BookingHistory'))
                        else:
                            #Failure to update seat count, redirects the user to the 'TransactionHistory'.
                            print('BookingPayment | Failed to book ticket.')
                            return redirect(url_for('TransactionHistory'))
                    else:
                        #Failure to fetch seat count, redirects the user to the 'TransactionHistory'.
                        print('BookingPayment | Failed to book ticket.')
                        return redirect(url_for('TransactionHistory'))
                else:
                    #Failure to update the booking details, redirects the user to the 'TransactionHistory'.
                    print('BookingPayment | Failed to book ticket.')
                    return redirect(url_for('TransactionHistory'))
            else:
                #Failure to process the payment, redirects the user to the 'BookingPayment'.
                return redirect(url_for('BookingPayment'))
        
    #Execute if the request method is not 'POST'.
    else:
        #The travel and booking ID are assigned to variables from session data.
        travel_id = session['booking_travel_id']
        booking_id = session['booking_id']

        #An instance of class 'Travel' is created using the travel ID and is assigned to object 'travel'.
        travel = Travel(travel_id,'','','','','','','','','','','','','','')
        #Triggers 'UserBusSearch' method to fetch the travel details for displaying ticket preview to user.
        result1 = travel.UserBusSearch('TicketBooking')
        if result1:

            #An instance of class 'Booking' is created using the Booking and Travel ID and is assigned to object 'booking'.
            booking = Booking(booking_id,'',travel_id,'','','','')
            #Triggers 'FetchBookingDetails' method to fetch the booking details for displaying ticket preview to user.
            result2 = booking.FetchBookingDetails()
            if result2:
                #An instance of class 'Passenger' is created using the Booking and Travel ID and is assigned to object 'passenger'.
                passenger = Passenger('',booking_id,travel_id,'','','','','')
                #Triggers 'FetchPassengerDetails' method to fetch the passenger details for displaying ticket preview to user.
                result3 = passenger.FetchPassengerDetails()
                if result3:
                    #Booking ID: Displays the booking ID.
                    #Details1: Contains the travel details.
                    #Details2: Contains the booking details.
                    #Details3: Contains the Passenger details.
                    return render_template('booking-payment.html', booking_id = booking_id, details1 = result1, details2 = result2, details3 = result3)
                else:
                    #Failing to fetch passenger details, redirects the user to seat selection.
                    return redirect(url_for('SeatSelection'))
            else:
                #Failing to fetch booking details, redirects the user to seat selection.
                return redirect(url_for('SeatSelection'))
        else:
            #Failing to fetch travel details, redirects the user to seat selection.
            return redirect(url_for('SeatSelection'))

#Code to fetch the card from the DB upon loading the wallet.
@app.route('/payments/wallet')
def FetchCard():

    #The card details can be fetched only if the user has logged in and the session data is generated.
    if 'user_id' in session:
        user_id = session['user_id']
        card_balance = request.args.get('card_balance')
        card_number = request.args.get('card_number')

        #An instance of class 'PaymentManager' is created and it is stored in object 'payment manager'
        payment_manager = PaymentManager(user_id,'',card_number,'','','',card_balance,'')
        #Triggers 'FetchDetails' method to fetch the card details using the available attribute values.
        result =  payment_manager.FetchDetails()
        if result:
            wallet_balance = result[0]
            card_balance = result[1]
            card_number = result[2]
            card_details = result[3]
            value = result[4]
            print('FetchCard | Wallet & Card details fetched from DB.')
            return render_template('payments.html', wallet_balance = wallet_balance, card_balance = card_balance, card_number = card_number, card_details = card_details, value = value)
        else:
            #Failing to fetch payment details will render the 'Payments' HTMl page.
            print('FetchCard | Failed to fetch payment details from DB.')
            return render_template('payments.html')
        
    #If the user ID is not in session, the viewer will be redirected to login page.
    else:
        return redirect(url_for('LoggingIn'))

#The payment functions within the wallet.
@app.route('/payments/wallet', methods = ['GET', 'POST'])
def PaymentFunctions():

    #The card details can be fetched only if the user has logged in and the session data is generated.
    if 'user_id' in session:
        user_id = session['user_id']

        #Enters into the below if code if the request method in submitted form is 'POST'.
        if request.method == 'POST':

            #The action is the name of the button that holds some value assigned to it. (There are multiple buttons with different values.)
            action = request.form['action']

            #Executes to add card to DB.
            if action == 'AddCard':
                #The card details are obtained from the HTML form.
                card_type = request.form['card_type']
                card_number = request.form['card_number']
                cardholder_name = request.form['cardholder_name']
                card_expiry = request.form['card_expiry']
                card_cvv = request.form['card_cvv']

                #An instance of class 'PaymentManager' is created and is assigned to object 'payment_manager'
                payment_manager = PaymentManager(user_id, card_type, card_number, cardholder_name, card_expiry, card_cvv, '','')
                #Triggers 'CardModification' along with the action 'AddCard'.
                result =  payment_manager.CardModification(action)

                #Checks if the card has been added.
                if result:
                    #If added, the card and wallet details are fetched from the 'FetchCard' and the 'Payments' HTML is rendered.
                    print("PaymentFunction | Card details added to DB.")
                    return redirect(url_for('FetchCard'))
                else:
                    #If failed to add, the card and wallet details are fetched from the 'FetchCard' and the 'Payments' HTML is rendered.
                    print("PaymentFunction | Failed to add card details to DB.")
                    return redirect(url_for('FetchCard'))
                
            #Executes to remove card in DB.
            if action == 'RemoveCard':
                #The card details are obtained from the HTML form.
                card_number = request.form['card_number']
                card_cvv = request.form['card_cvv']

                #An instance of class 'PaymentManager' is created and is assigned to object 'payment_manager'
                payment_manager = PaymentManager(user_id,'', card_number,'', '', card_cvv, '','')
                #Triggers 'CardModification' along with the action 'AddCard'.
                result =  payment_manager.CardModification(action)

                #Checks if the card has been removed.
                if result:
                    #If removed, the card and wallet details are fetched from the 'FetchCard' and the 'Payments' HTML is rendered.
                    print("PaymentFunction | Card details removed from DB.")
                    return redirect(url_for('FetchCard'))
                else:
                    #If failed to remove, the card and wallet details are fetched from the 'FetchCard' and the 'Payments' HTML is rendered.
                    print("PaymentFunction | Failed to remove card details from DB.")
                    return redirect(url_for('FetchCard'))
                
            #Executes to fetch the balance of card when clicked over it.
            if len(action) == 19:
                #The card number is the action value.
                card_number = action

                #An instance of class 'PaymentManager' is created and is assigned to object 'payment_manager'
                payment_manager = PaymentManager(user_id,'',card_number,'','','','','')
                mode = 'Card'

                #Triggers 'FetchBalance' along with the mode 'Card' to fetch its balance.
                result = payment_manager.FetchBalance(mode)
                if result==0 or result:
                    card_balance = result
                    session['card_number'] = card_number
                    print('PaymentFunction | Card balance fetched from DB.')
                    #Redirects to 'FetchCard' to display the card.
                    return redirect(url_for('FetchCard', card_balance = card_balance, card_number = card_number))
                else:
                    return redirect(url_for('FetchCard'))
                
            #Executes to add cash to wallet from card.
            if action == 'AddWallet':
                #The amount to credit is obtained from the HTML form.
                amount = request.form['amount']
                amount = int(amount)
                #The card number is stored in a variable from session data.
                card_number = session['card_number']
                
                #An instance of class 'PaymentManager' is created and is assigned to object 'payment_manager'
                payment_manager = PaymentManager(user_id,'',card_number,'','','','','')
                #Triggers 'Transaction' to transfer money from card to walelt.
                result = payment_manager.Transaction('Card','Wallet',amount,'Credit')
                if result:
                    card_balance = result
                    return redirect(url_for('FetchCard', card_balance = card_balance, card_number = card_number))
                else:
                    return redirect(url_for('FetchCard'))

            else:
                #If invalid action command is passed, the user is redirected to 'FetchCard'.
                print('PaymentFunction | Invalid action command.')
                return redirect(url_for('FetchCard'))
        else:
            #If invalid action command is passed, the user is redirected to 'FetchCard'.
            print('PaymentFunction | Invalid action command.')
            return redirect(url_for('FetchCard'))
    else:
        #If the user is not logged in, the viewer is redirected to the 'Login' page.
        print("PaymentFunction | User has not logged in.")
        return redirect(url_for('LoggingIn'))

#Transaction history viewing .
@app.route('/payments/transaction-history')
def TransactionHistory():
    #If the user ID is in session, the below code is executed.
    if 'user_id' in session:
        user_id = session['user_id']

        #An instance of class 'PaymentManager' is created and is assigned to object 'payment_manager'
        payment_manager = PaymentManager(user_id,'','','','','','','')
        #Triggers 'DisplayTransactionHistory' to display all the wallet transactions.
        result = payment_manager.DisplayTransactionHistory()

        if result:
            #The transaction details contains tuple of all the transactions from DB.
            print("DisplayTransactionHistory | Fetched transaction details.")
            return render_template('transaction-history.html', transaction_details = result)
        else:
            #The HTML page is rendered without any transactions.
            print("DisplayTransactionHistory | No transaction detail found.")
            return render_template('transaction-history.html')
    else:
        #If the user is not logged in, the viewer is redirected to the 'Login' page.
        print("DisplayTransactionHistory | User has not logged in.")
        return redirect(url_for('LoggingIn'))

#Booking history viewing.
@app.route('/booking-history', methods = ['GET', 'POST'])
def BookingHistory():
    #The booking history can be fetched only if the user has logged in and the session data is generated.
    if 'user_id' in session:

        #Enters into the below if code if the request method in submitted form is 'POST'.
        if request.method == 'POST':

            #The action is the name of the button that holds some value assigned to it. (There are multiple buttons with different values.)
            action = request.form['action']

            #Executes to view the ticket booked by the user.
            if action == 'ViewTicket':

                #Gets the booking ID from the button clicked by the user.
                booking_id = request.form['booking_id']

                #An instance of class 'Booking' is created and is assigned to object 'booking'
                booking = Booking('','','','','','','')
                #Triggers 'ViewTicket' along with the action 'booking_id' to fetch the ticket details for viewing it.
                result = booking.ViewTicket(booking_id)

                #Checks if the data exists.
                if result:
                    result1, result2, result3 = result
                    return render_template('ticket.html',booking_id=booking_id, details1=result1, details2=result2, details3=result3)
                else:
                    #If the data does not exist / failed to fetch the user is redirected to the 'BookingHistory'.
                    return redirect(url_for('BookingHistory'))

            #Executes to cancel the ticket booked by the user.    
            if action == 'CancelTicket':
                booking_id = request.form['booking_id']
                booking = Booking('','','','','','','')
                result = booking.CancelTicket(booking_id)
                if result:
                    print('BookingHistory | Ticket successfully cancelled.')
                    return redirect(url_for('BookingHistory'))
                else:
                    print('BookingHistory | Failed to cancel the ticket.')
                    return redirect(url_for('BookingHistory'))
                
            else:
                print('BookingHistory | Invalid action command.')
                return redirect(url_for('BookingHistory'))
            
        #If the request method is not 'POST' the below code is executed.
        else:
            user_id = session['user_id']
            booking = Booking('',user_id,'','','','','')
            result = booking.BookingHistory('Individual')
            return render_template('booking-history.html', booking_history = result)
    else:
        #If the user is not logged in, the viewer is redirected to the 'Login' page.
        print("BookingHistory | User has not logged in.")
        return redirect(url_for('LoggingIn'))


#--------------|ADMIN DASHBOARD|--------------#

#Managing the users of the web application.
@app.route('/user-management', methods = ['GET', 'POST'])
def UserManagement():
    if session['user_power'] == 'Admin':
        admin_id = session['user_id']
        admin_id = str(admin_id)
        if request.method == 'POST':
            action = request.form['action']
            if action == 'PromoteUser':
                user_id = request.form['user_id']
                admin_access = Admin(user_id,'','','','','','','','','','')
                result = admin_access.ModifyUserPower(action)   
                if result:
                    print("UserManagement | User->Admin successfully promoted.")
                    return redirect(url_for('UserManagement'))
                else:
                    return redirect(url_for('UserManagement'))
                
            if action == 'DemoteAdmin':
                demote_admin_id = request.form['user_id'] 
                if demote_admin_id == admin_id:
                    print("UserManagement | Admin cannot use this access on themselves.")
                    return redirect(url_for('UserManagement'))
                else:
                    admin_access = Admin(demote_admin_id,'','','','','','','','','','')
                    result = admin_access.ModifyUserPower(action)
                    if result:
                        print("UserManagement | Admin->User successfully demoted.")
                        return redirect(url_for('UserManagement'))
                    else:
                        return redirect(url_for('UserManagement'))
                    
            if action == 'Kick':
                user_id = request.form['user_id']
                if user_id == admin_id:
                    print("UserManagement | Admin cannot use this access on themselves.")
                    return redirect(url_for('UserManagement'))
                else:
                    admin_access = Admin(user_id,'','','','','','','','','','')
                    result = admin_access.KickUser()
                    if result:
                        print("UserManagement | User successfully kicked.")
                        return redirect(url_for('UserManagement'))
                    else:
                        return redirect(url_for('UserManagement'))

            else:
                print("UserManagement | Invalid action command.")
                return redirect(url_for('UserManagement'))
        else:
            admin_access = Admin('','','','','','','','','','','')
            result = admin_access.FetchUserData()
            if result:
                return render_template('user-management.html', user_details = result)
            else:
                return render_template('user-management.html')
                
    else:
        print('UserManagement | Unauthorised entry! User is not an admin')
        return redirect(url_for('HomePage'))
    
#Managing the buses that are available.
@app.route('/bus-management', methods = ['GET', 'POST'])
def BusManagement():
    if session['user_power'] == 'Admin':
        if request.method == 'POST':
            action = request.form['action']
            if action == 'AddBus':
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
                bus = Bus('',bus_number,operator_name,operator_number,total_seats,base_fare,bus_type,reclining_seats,charging_points,wifi,blankets_pillows,snacks,movie,reading_light,track_my_bus,m_ticket)
                result = bus.AddBus()
                if result:
                    print("BusManagement | Bus details have been added successfully.")
                    return redirect(url_for('BusManagement'))
                else:
                    return redirect(url_for('BusManagement'))
                
            if action == 'RemoveBus':
                bus_id = request.form['bus_id']
                bus = Bus(bus_id,'','','','','','','','','','','','','','','')
                result = bus.RemoveBus()
                if result:
                    print('BusManagement | Bus details have been removed successfully.')
                    return redirect(url_for('BusManagement'))
                else:
                    print('BusManagement | Failed to delete bus details from DB.')
                    return redirect(url_for('BusManagement'))
                
            else:
                print("BusManagement | Invalid action command.")
                return redirect(url_for('BusManagement'))
            
        else:
            bus = Bus('','','','','','','','','','','','','','','','')
            result = bus.FetchBus()
            if result:
                print("BusManagement | Bus details fetched from DB.")
                return render_template('bus-management.html', bus_details = result)
            else:
                return render_template('bus-management.html')

    else:
        print("BusManagement | Unauthorised entry! User is not an admin.")
        return redirect(url_for('HomePage'))

#Managing the travel details of each and every bus (Each bus may have multiple travel schedule).
@app.route('/travel-management', methods = ['GET', 'POST'])
def TravelManagement():
    if session['user_power'] == 'Admin':
        if request.method == 'POST':
            action = request.form['action']
            if action == 'AddTravel':
                bus_id = request.form['bus_id']
                travel_distance = request.form['travel_distance']
                source_location = request.form['source_location']
                destination_location = request.form['destination_location']
                source_date = request.form['source_date']
                destination_date = request.form['destination_date']
                source_time = request.form['source_time']
                destination_time = request.form['destination_time']
                bus = Bus(bus_id,'','','','','','','','','','','','','','','')
                result = bus.BusDetails()
                if result:
                    operator_name = result[0][0]
                    total_seats = result[0][1]
                    available_seats = result[0][1]
                    base_fare = result[0][2]
                    total_fare = int(base_fare) * int(travel_distance)
                    travel = Travel('',bus_id, operator_name, source_location, destination_location, source_date, destination_date, source_time, destination_time, travel_distance, total_fare, total_seats, available_seats, '0', '0')
                    result = travel.AddTravel()
                    if result:
                        print('TravelManagement | Travel details added successfully.')
                        result = travel.TravelDetails()
                        if result:
                            travel_id = result[0][0]
                            seat = Seat('',travel_id,bus_id,'','','')
                            result = seat.AddSeat(total_seats)
                            if result:
                                print("TravelManagement | Seat details added successfully.")
                                return redirect(url_for('TravelManagement'))
                            else:
                                print('TravelManagement | Failed to add seat details.')
                                return redirect(url_for('TravelManagement'))
                        return redirect(url_for('TravelManagement'))
                    else:
                        print('TravelManagement | Failed to add travel details.')
                        return redirect(url_for('TravelManagement'))
                else:
                    return redirect(url_for('TravelManagement'))
                
            if action == 'RemoveTravel':
                travel_id = request.form['travel_id']
                travel = Travel('','','','','','','','','','','','','','','')
                result = travel.RemoveTravelDetails(travel_id, 'TravelManagement')
                if result:
                    print('TravelManagement | Travel details removed from DB.')
                    return redirect(url_for('TravelManagement'))
                else:
                    print('TravelManagement | Failed to remove travel details from DB.')
                    return redirect(url_for('TravelManagement'))
                
            else:
                print("TravelManagement | Invalid action command.")
                return redirect(url_for('TravelManagement'))
        else:
            travel = Travel('','','','','','','','','','','','','','','')
            result = travel.FetchTravel()
            if result:
                return render_template('travel-management.html', travel_details = result)
            else:
                return render_template('travel-management.html')
    else:
        print("TravelManagement | Unauthorised entry! User is not an admin.")
        return redirect(url_for('HomePage'))

#Managing the seat status of each and every travel.
@app.route('/seat-management', methods = ['GET', 'POST'])
def SeatManagement():
    if session['user_power'] == 'Admin':
        if request.method == 'POST':
            action = request.form['action']
            if action == 'FetchSeats':
                travel_id = request.form['travel_id']
                session['admin_travel_id'] = travel_id
                seat = Seat('','','','','','')
                result = seat.FetchSeat(travel_id)
                if result:
                    return render_template('seat-management.html', seat_details = result)
                else:
                    return render_template('seat-management.html')
                
            if action == 'Available' or action == 'Temporary':
                seat_number = request.form['seat_number']
                travel_id = session['admin_travel_id']
                if action =='Available':
                    seat = Seat('',travel_id,'','0',seat_number,'Available')
                if action =='Temporary':
                    seat = Seat('',travel_id,'','-1',seat_number,'Temporary')
                result = seat.UpdateSeat()
                if result:
                    travel = Travel(travel_id,'','','','','','','','','','','','','','')
                    result = travel.SeatCountUpdation('Fetch')
                    if result:
                        available_seat_db = result[0][0]
                        booked_seat_db = result[0][1]
                        temporary_seat_db = result[0][2]
                        if action == 'Available':
                            available_seat_db = available_seat_db + 1
                            temporary_seat_db = temporary_seat_db - 1
                        if action == 'Temporary':
                            available_seat_db = available_seat_db - 1
                            temporary_seat_db = temporary_seat_db + 1
                        travel = Travel(travel_id,'','','','','','','','','','','',available_seat_db,booked_seat_db,temporary_seat_db)
                        result = travel.SeatCountUpdation('Update')
                        if result:
                            return redirect(url_for('SeatManagement'))
                        else:
                            return redirect(url_for('SeatManagement'))
                    else:
                        return redirect(url_for('SeatManagement'))
                else:
                    return redirect(url_for('SeatManagement'))
            else:
                print('SeatManagement | Invalid action command.')
                return redirect(url_for('SeatManagement'))

        else:
            seat = Seat('','','','','','')
            if 'admin_travel_id' in session:
                travel_id = session['admin_travel_id']
                result = seat.FetchSeat(travel_id)
            else:
                result = seat.FetchSeat(None)
            if result:
                return render_template('seat-management.html', seat_details = result)
            else:
                return render_template('seat-management.html')
    else:
        print("SeatManagement | Unauthorised entry! User is not an admin.")
        return redirect(url_for('HomePage'))

#Managing the tickets that are booked using the web application.
@app.route('/booking-management', methods = ['GET', 'POST'])
def BookingManagement():
    if session['user_power'] == 'Admin':
        if request.method == 'POST':
            action = request.form['action']
            if action == 'ViewTicket':
                booking_id = request.form['booking_id']
                booking = Booking('','','','','','','')
                result = booking.ViewTicket(booking_id)
                if result:
                    result1 = result[0]
                    result2 = result[1]
                    result3 = result[2]
                    return render_template('ticket.html',booking_id=booking_id, details1=result1, details2=result2, details3=result3)
                else:
                    return redirect(url_for('HomePage'))
                
            if action == 'CancelTicket':
                booking_id = request.form['booking_id']
                booking = Booking('','','','','','','')
                result = booking.CancelTicket(booking_id)
                if result:
                    print('BookingManagement | Ticket successfully cancelled.')
                    return redirect(url_for('BookingManagement'))
                else:
                    print('BookingManagement | Failed to cancel the ticket.')
                    return redirect(url_for('BookingManagement'))

            else:
                print('BookingManagement | Invalid action command.')
                return redirect(url_for('BookingManagement'))
        else:
            booking = Booking('','','','','','','')
            result = booking.BookingHistory('All')
            return render_template('booking-management.html', booking_details = result)

#Viewing all the session data stored in the client browser.
@app.route('/session-data')
def SessionData():
    if session['user_power'] == 'Admin':
        session_data = []
        for key, value in session.items():
            session_data.append((key,value))
        return render_template('session-data.html', session_data = session_data)
    else:
        print("SeatManagement | Unauthorised entry! User is not an admin.")
        return redirect(url_for('HomePage'))

if __name__ == '__main__':
    app.run(debug=True)

#Input validation (Completed)
#Homepage - Completed
#Login - Completed
#Register - Completed
#Payments - Completed
#Bus Management - Completed
#Travel Management - Completed
#Seat Management - Completed
#Passenger Details - Completed



