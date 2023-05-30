#Esential importations for the web application.
from flask import Flask, redirect, url_for, render_template, request, session, jsonify
from flask_mysqldb import MySQL
import json
import configparser

#Creates a instance of the Flask and assigns it to 'app'.
app = Flask(__name__)

#Parsing the configuration file
config = configparser.ConfigParser()
config.read('config.cfg')
host = config.get('mysql', 'host')
user = config.get('mysql', 'user')
password = config.get('mysql', 'password')
db = config.get('mysql', 'db')
secret_key = config.get('app', 'secret_key')


#Database configuration.   
app.config['MYSQL_HOST'] = host
app.config['MYSQL_USER'] = user
app.config['MYSQL_PASSWORD'] = password
app.config['MYSQL_DB'] = db

#Secret key to store the session data in server-side.
app.secret_key = secret_key

#Creates the instance of the MySQL and assigns it to 'mysql'.
mysql = MySQL(app)

#--------------|CLASS DECLARATION|--------------#

#Attributes and methods of the user.
class User:
    def __init__(self, user_id, user_power, user_status, first_name, last_name, dob, gender, email, phone_number, username, password):
        self.user_id = user_id
        self.user_power = user_power
        self.user_status = user_status
        self.first_name = first_name
        self.last_name = last_name
        self.dob = dob
        self.gender = gender
        self.email = email
        self.phone_number = phone_number
        self.username = username
        self.password = password

    #For registering the user in DB.
    def Register(self):
        mycursor = mysql.connection.cursor()
        try:
            #Fetches all the data from 'user_credentials' where the username value is the value submitted by user.
            query = 'SELECT * FROM USER_CREDENTIALS WHERE USERNAME=%s'
            value = (self.username,)
            mycursor.execute(query,value)
            result = mycursor.fetchall()

            #If data exists, it means the username already exists. 
            if result:

                #The registration process cannot be completed, so 'False' is returned.
                print('Register | Username already exists')
                return False
            
            #If data does not exist, it means the username is available for registration.
            else:
                query = 'INSERT INTO USER_CREDENTIALS (FIRST_NAME,LAST_NAME,DOB,GENDER,EMAIL,PHONE_NUMBER,USERNAME,PASSWORD) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)'
                values = (self.first_name, self.last_name, self.dob, self.gender, self.email, self.phone_number, self.username, self.password)
                mycursor.execute(query,values)
                mysql.connection.commit()

                #After commit, the number of rows modified by the cursor is checked if it is greater than 0 to confirm insertion.
                if(mycursor.rowcount > 0):
                    print("Register | User data added to DB.")
                    #Upon successful insertion 'True' is returned.
                    return True
                else:
                    print("Register | Failed to add user data to DB.")
                    #Upon failure, 'False' is returned.
                    return False

        #Prints the exception if raised.
        except Exception as e:
            mysql.connection.rollback()
            print(f"Register | Error: {e}")
            return False
        
        #Cursor is closed to free up system resources and prevent memory leaks.
        finally:
            mycursor.close()

    #For logging in of the user by verifying the credentials with DB.
    def Login(self):
        mycursor = mysql.connection.cursor()
        try:
            #Fetches all the data from 'user_credentials' where the username and password is the value passed by the user.
            query = 'SELECT USER_ID, USER_POWER, USER_STATUS, FIRST_NAME FROM USER_CREDENTIALS WHERE USERNAME=%s AND PASSWORD=%s'
            values = (self.username, self.password)
            mycursor.execute(query, values)
            result = mycursor.fetchall()

            #If data exists it means the username and password is correct.
            if result:
                #The retrieved data will be in the form of a list. Eg. (('1','Admin','Active'),)
                user_id = result[0][0]
                user_power = result[0][1]
                user_status = result[0][2]
                first_name = result[0][3]
                self.user_id = user_id
                self.user_power = user_power
                self.user_status = user_status
                self.first_name = first_name

                #Checks the status of the user, 'Active' or 'Disabled'
                if user_status == 'Active':

                    #If it is 'Active' the user ID, power, and status are stored in session for later use.
                    session['user_id'] = user_id
                    session['user_power'] = user_power
                    session['user_status'] = user_status
                    session['first_name'] = first_name
                    print("ValidateUser | User login successful.")
                    statement = 'User login successful.'
                    return True, statement
                
                #If the user status is disabled, it has to be activated.
                elif user_status == 'Disabled':

                    #Updates the user status to active due to login attempt.
                    updated_status = 'Active'
                    query = 'UPDATE USER_CREDENTIALS SET USER_STATUS = %s WHERE USER_ID = %s'
                    values = (updated_status, user_id)
                    mycursor.execute(query, values)
                    mysql.connection.commit()

                    #The user ID, power and status is stored in session for later use.
                    session['user_id'] = user_id
                    session['user_power'] = user_power
                    session['user_status'] = updated_status
                    session['first_name'] = first_name
                    self.user_status = updated_status
                    print("ValidateUser | User login successful (Deactivated -> Activated).")
                    #Upon successful verifcation, 'True' is returned.
                    statement = 'Account has been reactivated and login successful.'
                    return True, statement
                else:
                    print("ValidateUser | Invalid power.")
                    #Upon failure, 'False' is returned.
                    return False, None
                
            #If data does not exist, it means the username and password is wrong.
            else:
                statement = 'User does not exist / Invalid credentials.'
                print("ValidateUser | User does not exist / Invalid credentials.")
                return False, statement
            
        #Prints the exception if raised.
        except Exception as e:
            mysql.connection.rollback()
            print(f"Validate User | Error: {e}")
            return False, None
        
        #Cursor is closed to free up system resources and prevent memory leaks.
        finally:
            mycursor.close()

    #For viewing the profile.
    def Profile(self):
        mycursor = mysql.connection.cursor()
        try:
            #Fetches al lthe data from the 'user_credentials' where the user ID is the value from the session.
            query = 'SELECT FIRST_NAME, LAST_NAME, DOB, EMAIL, PHONE_NUMBER FROM USER_CREDENTIALS WHERE USER_ID = %s'
            value = (self.user_id,)
            mycursor.execute(query,value)
            result = mycursor.fetchall()

            #If data exists, the return is 'True'
            if result:
                print("Profile | User details collected.")
                return result
            
            #If data does not exist, the return is 'False' (Not possible in most case).
            else:
                print("Profile | User details not found")
                return False
            
        #Prints the exception if raised.
        except Exception as e:
            mysql.connection.rollback()
            print(f"Profile | Error : {e}")
            False

        #Cursor is closed to free up system resources and prevent memory leaks.
        finally:
            mycursor.close()

    #For deactivating a profile.
    def DeactivateProfile(self):
        mycursor = mysql.connection.cursor()
        try:
            #The user status is set to 'disabled' and updated in user_credentails where user_id is the session ID.
            user_status = 'Disabled'
            query = 'UPDATE USER_CREDENTIALS SET USER_STATUS = %s WHERE USER_ID = %s'
            values = (user_status, self.user_id)
            mycursor.execute(query, values)
            mysql.connection.commit()

            #Checks if the mycursor executed rowcount is greater than 0 to confirm updation.
            if mycursor.rowcount > 0:
                #If the updation is confirmed, the session data is cleared and the return value is 'True'.
                session.clear()
                print("DeactivateProfile | User successfully disabled.")
                return True
            else:
                #If the updation failed, the return value is 'False'
                print('DeactivateProfile | Failed to deactivate the user profile.')
                return False
            
        #Prints the exception if raised.
        except Exception as e:
            mysql.connection.rollback()
            print(f"DeactivateProfile | Error: {e}")
            return False
        
        #Cursor is closed to free up system resources and prevent memory leaks.
        finally:
            mycursor.close()

#Methods of the admin.
class Admin(User):

    def FetchUserData(self):
        mycursor = mysql.connection.cursor()
        try:
            query = 'SELECT USER_ID, FIRST_NAME, LAST_NAME, EMAIL, USER_POWER FROM USER_CREDENTIALS'
            value = ()
            mycursor.execute(query, value)
            result = mycursor.fetchall()
            if result:
                print("FetchUserData | User details fetched from DB.")
                return result
            else:
                print("FetchUserData | Failed to fetch user details from DB.")
                return False
        except Exception as e:
            mysql.connection.rollback()
            print(f"FetchUserData | Error: {e}")
            return False
        finally:
            mycursor.close()

    def ModifyUserPower(self, action):
        mycursor = mysql.connection.cursor()
        try:
            if action == 'PromoteUser':
                user_power = 'Admin'
            elif action == 'DemoteAdmin':
                user_power = 'User'
            else:
                print('ModifyUserPower | Invalid user power.')
                return False
            query = 'UPDATE USER_CREDENTIALS SET USER_POWER = %s WHERE USER_ID = %s'
            values = (user_power, self.user_id)
            mycursor.execute(query, values)
            mysql.connection.commit()
            if mycursor.rowcount > 0:
                print('ModifyUserPower | User power has been updated in DB.')
                return True
            else:
                print('ModifyUserPower | Failed to update user power in DB.')
                return False
        except Exception as e:
            mysql.connection.rollback()
            print(f"ModifyUserPower | Error: {e}")
            return False
        finally:
            mycursor.close()

    def KickUser(self):
        return True

#Attributes and methods responsible for payment.
class PaymentManager:
    def __init__(self, user_id, card_type, card_number, cardholder_name, card_expiry, card_cvv, card_balance, wallet_balance):
        self.user_id = user_id
        self.card_type = card_type
        self.card_number = card_number
        self.cardholder_name = cardholder_name
        self.card_expiry = card_expiry
        self.card_cvv = card_cvv
        self.card_balance = card_balance
        self.wallet_balance = wallet_balance
        
    #For fetching the wallet and card details to load 'Payments' HTML page.
    def FetchDetails(self):
        mycursor = mysql.connection.cursor()
        try:
            #Selects the wallet from user credentials table.
            query = 'SELECT WALLET FROM USER_CREDENTIALS WHERE USER_ID = %s'
            value = (self.user_id,)
            mycursor.execute(query, value)
            result1 = mycursor.fetchall()
            #If data exists, the wallet balance is stored in a variable.
            if result1:
                wallet_balance = result1[0][0]
            #If not, returns 'False'.
            else:
                print("FetchDetails | Failed to fetch wallet details from DB.")
                return False
            
            #Selects the all card details from card details table.
            query = 'SELECT CARD_NUMBER, CARDHOLDER_NAME, CARD_EXPIRY, CARD_BALANCE, CARD_TYPE FROM CARD_DETAILS WHERE USER_ID = %s'
            value = (self.user_id,)
            mycursor.execute(query, value)
            result2 = mycursor.fetchall()
            #If card data exists, the value is assigned 'True' and all the results are returned.
            if result2:
                value = True
                return (wallet_balance, self.card_balance, self.card_number, result2, value)
            #If card data does not exist, the value is assigned 'False' and all the result are returned.
            else:
                value = False
                return (wallet_balance, self.card_balance, self.card_number, result2, value)
            
        #Prints the exception if raised.
        except Exception as e:
            mysql.connection.rollback()
            print(f"FetchDetails | Error: {e}")
            return False
        
        #Cursor is closed to free up system resources and prevent memory leaks.
        finally:
            mycursor.close()

    #Checks the card existence in DB. 
    def VerifyCardExistence(self):
        mycursor = mysql.connection.cursor()
        try:
            #Selects the card details where the card number is the input passed by the user to check its existence.
            query = 'SELECT * FROM CARD_DETAILS WHERE CARD_NUMBER = %s'
            values = (self.card_number,)
            mycursor.execute(query, values)
            result = mycursor.fetchall()
            #If the card exists, 'True' is returned, else 'False' is returned.
            if result:
                print('VerifyCardExistence | Card exists in DB.')
                return True
            else:
                print('VerifyCardExistence | Card does not exist in DB.')
                return False
            
        #Prints the exception if raised.
        except Exception as e:
            mysql.connection.rollback()
            print(f'VerifyCardExistence | Error:: {e}')
            return False
        
        #Cursor is closed to free up system resources and prevent memory leaks.
        finally:
            mycursor.close()

    #Add / Remove card from DB.
    def CardModification(self, action):
        mycursor = mysql.connection.cursor()
        try:
            #Triggers 'VerifyCardExistence' to check if the card already exists or not.
            card_existence = self.VerifyCardExistence()

            #If card exists and needs to be removed, below code is executed.
            if card_existence == True and action == 'RemoveCard':
                query = 'DELETE FROM CARD_DETAILS WHERE CARD_NUMBER = %s AND USER_ID = %s AND CARD_CVV = %s'
                values = (self.card_number, self.user_id, self.card_cvv)

            #If card does not exist and needs to be added, below code is executed.
            elif card_existence == False and action == 'AddCard':
                query = 'INSERT INTO CARD_DETAILS (USER_ID, CARD_TYPE, CARD_NUMBER, CARDHOLDER_NAME, CARD_EXPIRY, CARD_CVV) VALUES (%s,%s,%s,%s,%s,%s)'
                values = (self.user_id, self.card_type, self.card_number, self.cardholder_name, self.card_expiry, self.card_cvv)   

            #Under any other circumstances, the card will neither be added nor removed.                 
            else:
                return False
            
            #If any condition with query and value is satisfied, it is executed and committed..
            mycursor.execute(query, values)
            mysql.connection.commit()

            #After commit, the number of rows modified by the cursor is checked if it is greater than 0 to confirm insertion.
            if(mycursor.rowcount > 0):
                print(f"CardModification | {action} successful.")
                return True
            else:
                print(f"CardModification | {action} failed.")
                return False
            
        #Prints the exception if raised.
        except Exception as e:
            mysql.connection.rollback()
            print(F"AddCard | Error: {e}")
            return False
        
        #Cursor is closed to free up system resources and prevent memory leaks.
        finally:
            mycursor.close()

    #Fetches the balance of (Wallet / Card).
    def FetchBalance(self, mode):
        mycursor = mysql.connection.cursor()
        try:
            #The mode can either be wallet / card.
            if mode == 'Wallet':
                query = 'SELECT WALLET FROM USER_CREDENTIALS WHERE USER_ID = %s'
                value = (self.user_id,)
            if mode == 'Card':
                query = 'SELECT CARD_BALANCE FROM CARD_DETAILS WHERE USER_ID = %s AND CARD_NUMBER = %s'
                value = (self.user_id, self.card_number)
            if mode == 'Admin':
                query = 'SELECT WALLET FROM USER_CREDENTIALS WHERE USER_ID = %s'
                value = (0,)                
            mycursor.execute(query, value)
            result = mycursor.fetchall()
            #Checks if the data is fetched.
            if result:
                balance = result[0][0]
                print(f'FetchBalance | Fetched {mode} balance from DB.')
                return balance
            else:
                print(f"FetchBalance | Failed to fetch {mode} balance from DB.")
                return False
            
        #Prints the exception if raised.
        except Exception as e:
            mysql.connection.rollback()
            print("FetchBalance | Error: {e}")
            return False
        
        #Cursor is closed to free up system resources and prevent memory leaks.
        finally:
            mycursor.close()

    #Fetches all the transaction logs from DB.
    def DisplayTransactionHistory(self):
        mycursor = mysql.connection.cursor()
        try:
            query = 'SELECT TRANSACTION_ID, AMOUNT, ACTION, BALANCE, DESCRIPTION, TRANSACTION_TIME FROM TRANSACTION_DETAILS WHERE USER_ID = %s ORDER BY TRANSACTION_TIME DESC'
            value = (self.user_id,)
            mycursor.execute(query, value)
            result = mycursor.fetchall()
            return result
        except Exception as e:
            mysql.connection.rollback()
            print(f"TransactionHistory | Error: {e}")
            return False
        finally:
            mycursor.close()

    #For executing transactions.
    def Transaction(self, sender, receiver, amount, action):
        mycursor = mysql.connection.cursor()
        try:
            if(sender=='Card' and receiver=='Wallet' and action=='Credit'):
                #Triggers 'FetchBalance' method to fetch the balance of 'Card'.
                card_balance = self.FetchBalance('Card')

                #Only if the card balance is greater than or equal to the amount, the transaction can be processed.
                if int(card_balance) >= int(amount):
                    #Update the balance of card (Card Balance = Card Balance - Amount).
                    query = 'UPDATE CARD_DETAILS SET CARD_BALANCE = CARD_BALANCE - %s WHERE CARD_NUMBER = %s AND USER_ID = %s'
                    values = (amount,self.card_number,self.user_id)
                    mycursor.execute(query, values)
                    mysql.connection.commit()

                    #Update the balance of wallet (Wallet = Wallet + Amount).
                    query = 'UPDATE USER_CREDENTIALS SET WALLET = WALLET + %s WHERE USER_ID = %s'
                    values = (amount,self.user_id)
                    mycursor.execute(query, values)
                    mysql.connection.commit()

                    #Triggers 'TransactionLog' to log the transaction from wallet POV.
                    result = self.TransactionLog(sender,receiver,amount,action)
                    if result:
                        #Upon successful debiting from card, crediting to wallet, adding transaction log, the card balance is returned.
                        card_balance = card_balance - amount
                        return card_balance
                else:
                    #If insufficient balance, the card balance is returned back.
                    print('Transaction | Card has insufficient balance.')
                    return card_balance
            
            elif(sender=='Wallet' and receiver=='MyJourney' and action=='Debit'):
                #Triggers 'FetchBalance' method to fetch the balance of 'Wallet'.
                wallet_balance = self.FetchBalance('Wallet')

                #Only if the wallet balance is greater than or equal to the amount, the transaction can be processed.
                if int(wallet_balance) >= int(amount):
                    #Update the balance of wallet (Wallet = Wallet - Amount).
                    query = 'UPDATE USER_CREDENTIALS SET WALLET = WALLET - %s WHERE USER_ID = %s'
                    values = (amount,self.user_id)
                    mycursor.execute(query, values)
                    mysql.connection.commit()

                    #Update the balance of MyJourney (Wallet = Wallet + Amount).
                    query = 'UPDATE USER_CREDENTIALS SET WALLET = WALLET + %s WHERE USER_ID = %s'
                    values = (amount,0)
                    mycursor.execute(query, values)
                    mysql.connection.commit()

                    #Triggers 'TransactionLog' to log the transaction from wallet POV.
                    result = self.TransactionLog(sender,receiver,amount,action)
                else:
                    #If insufficient balance, 'False' is returned indicating the transaction cannot be processed.
                    print('Transaction | Wallet has insufficient balance.')
                    return False
                
            elif(sender=='MyJourney' and receiver=='Wallet' and action=='Credit'):
                #Update the balance of MyJourney (Wallet = Wallet - Amount).
                query = 'UPDATE USER_CREDENTIALS SET WALLET = WALLET - %s WHERE USER_ID = %s'
                values = (amount,0)
                mycursor.execute(query, values)
                mysql.connection.commit()

                #Update the balance of wallet (Wallet = Wallet + Amount).
                query = 'UPDATE USER_CREDENTIALS SET WALLET = WALLET + %s WHERE USER_ID = %s'
                values = (amount,self.user_id)
                mycursor.execute(query, values)
                mysql.connection.commit()
                #Triggers 'TransactionLog' to log the transaction from wallet POV.
                result = self.TransactionLog(sender,receiver,amount,action)

            if result:
                return True
            else:
                return False
        
        #Prints the exception if raised.
        except Exception as e:
            mysql.connection.rollback()
            print(f'Transaction | Error: {e}')
            return False
        
        #Cursor is closed to free up system resources and prevent memory leaks.
        finally:
            mycursor.close()

    #Logs all the transaction details from the wallet POV. 
    def TransactionLog(self, sender, receiver, amount, action):
        mycursor = mysql.connection.cursor()
        try:
            #From wallet prespective the description of log changes.
            if action == 'Credit' and sender == 'Card' and receiver == 'Wallet':
                description_wallet = f'{receiver} received INR {amount} from {sender} ({self.card_number})'
            if action == 'Credit' and sender == 'MyJourney' and receiver == 'Wallet':
                description_wallet = f'{receiver} received INR {amount} refund from {sender}'
                description_myjourney = f'{sender} refunded booking cost INR {amount} to {receiver} (User ID: {self.user_id})'
            if action == 'Debit' and sender == 'Wallet' and receiver == 'MyJourney':
                description_wallet = f'{sender} paid booking cost INR {amount} to {receiver}'
                description_myjourney = f'User ID: {self.user_id} paid booking cost INR {amount} from {sender}'
                

            #Triggers 'FetchBalance' to get the balance of 'wallet'.
            user_balance = self.FetchBalance('Wallet')
            #Triggers 'FetchBalance' to get the balance of 'Admin'.
            admin_balance = self.FetchBalance('Admin')

            #Logs the details into the transaction details DB.
            query1 = 'INSERT INTO TRANSACTION_DETAILS (USER_ID, AMOUNT, ACTION, BALANCE, DESCRIPTION) VALUES (%s,%s,%s,%s,%s)'
            values1 = (self.user_id, amount, action, user_balance, description_wallet)
            mycursor.execute(query1, values1)
            mysql.connection.commit()

            if(sender=='MyJourney' or receiver=='MyJourney'):
                if action == 'Debit':
                    action = 'Credit'
                elif action == 'Credit':
                    action = 'Debit'
                query2 = 'INSERT INTO TRANSACTION_DETAILS (USER_ID, AMOUNT, ACTION, BALANCE, DESCRIPTION) VALUES (%s,%s,%s,%s,%s)'
                values2 = (0, amount, action, admin_balance, description_myjourney)
                mycursor.execute(query2, values2)
                mysql.connection.commit()

            #After commit, the number of rows modified by the cursor is checked if it is greater than 0 to confirm insertion.
            if mycursor.rowcount > 0:
                print('TransactionLog | Log added to DB.')
                return True
            else:
                print('TransactionLog | Failed to add log to DB.')
                return False
            
        #Prints the exception if raised.
        except Exception as e:
            mysql.connection.rollback()
            print(f'TransactionLog | Error: {e}')
            return False
        
        #Cursor is closed to free up system resources and prevent memory leaks.
        finally:
            mycursor.close()

#Attributes and methods responsible for managing the bus and its details.
class Bus:
    def __init__(self,bus_id,bus_number,operator_name,operator_number,total_seats,base_fare,bus_type,reclining_seats,charging_points,wifi,blankets_pillows,snacks,movie,reading_light,track_my_bus,m_ticket):
        self.bus_id = bus_id
        self.bus_number = bus_number
        self.operator_name = operator_name
        self.operator_number = operator_number
        self.total_seats = total_seats
        self.base_fare = base_fare
        self.bus_type = bus_type
        self.reclining_seats = reclining_seats
        self.charging_points = charging_points
        self.wifi = wifi
        self.blankets_pillows = blankets_pillows
        self.snacks = snacks
        self.movie = movie
        self.reading_light = reading_light
        self.track_my_bus = track_my_bus
        self.m_ticket = m_ticket

    def AddBus(self):
        mycursor = mysql.connection.cursor()
        try:
            query = 'SELECT * FROM BUS_DETAILS WHERE BUS_NUMBER = %s'
            value = (self.bus_number,)
            mycursor.execute(query, value)
            result = mycursor.fetchall()
            if result:
                print("AddBus | Bus details already exist in DB.")
                return False
            else:
                query = 'INSERT INTO BUS_DETAILS (BUS_NUMBER,OPERATOR_NAME,OPERATOR_NUMBER,TOTAL_SEATS,BASE_FARE,BUS_TYPE,RECLINING_SEATS,CHARGING_POINTS,WIFI,BLANKETS_PILLOWS,SNACKS,MOVIE,READING_LIGHT,TRACK_MY_BUS,M_TICKET) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
                values = (self.bus_number,self.operator_name,self.operator_number,self.total_seats,self.base_fare,self.bus_type,self.reclining_seats,self.charging_points,self.wifi,self.blankets_pillows,self.snacks,self.movie,self.reading_light,self.track_my_bus,self.m_ticket)
                mycursor.execute(query, values)
                mysql.connection.commit()
                if mycursor.rowcount > 0:
                    print("AddBus | Bus details inserted into DB.")
                    return True
                else:
                    print("AddBus | Failed to insert bus details into DB.")
                    return False
        except Exception as e:
            mysql.connection.rollback()
            print(f"AddBus | Error: {e}")
            return False
        finally:
            mycursor.close()

    def RemoveBus(self):
        mycursor = mysql.connection.cursor()
        try:
            query = 'SELECT TRAVEL_ID FROM TRAVEL_DETAILS WHERE BUS_ID = %s'
            values = (self.bus_id,)
            mycursor.execute(query, values)
            result = mycursor.fetchall()
            if result:
                print('RemoveBus | Bus details fetched successfully.')
                iteration = 0
                for i in range (len(result)):
                    travel = Travel('','','','','','','','','','','','','','','')
                    travel_deletion_result = travel.RemoveTravelDetails(result[i][0],'TravelManagement')
                    if travel_deletion_result:
                        print(f'RemoveBus | Bus ID: {result[i][0]} removed from DB.')
                        iteration += 1
                    else:
                        return False
                if iteration == (len(result)):
                    query = 'DELETE FROM BUS_DETAILS WHERE BUS_ID = %s'
                    values = (self.bus_id,)
                    mycursor.execute(query, values)
                    mysql.connection.commit()
                    if mycursor.rowcount > 0:
                        print(f'Remove Bus: Removed {len(result)+1} travel details.')
                        return True
                    else:
                        return False
                else:
                    print('RemoveBus | Failed to delete the bus details.')
                    return False
            else:
                query = 'DELETE FROM BUS_DETAILS WHERE BUS_ID = %s'
                values = (self.bus_id,)
                mycursor.execute(query, values)
                mysql.connection.commit()
                if mycursor.rowcount > 0:
                    print(f'Remove Bus: Removed {len(result)+1} travel details.')
                    return True
                else:
                    return False
                
        except Exception as e:
            mysql.connection.rollback()
            print(f'RemoveBus | Error: {e}')
            return False
        
        finally:
            mycursor.close()

    def FetchBus(self):
        mycursor = mysql.connection.cursor()
        try:
            query = 'SELECT BUS_ID, BUS_NUMBER, OPERATOR_NAME, OPERATOR_NUMBER, TOTAL_SEATS, BASE_FARE, BUS_TYPE, RECLINING_SEATS, CHARGING_POINTS, WIFI, BLANKETS_PILLOWS, SNACKS, MOVIE, READING_LIGHT, TRACK_MY_BUS, M_TICKET FROM BUS_DETAILS'
            value = ()
            mycursor.execute(query, value)
            result = mycursor.fetchall()
            if result:
                print("FetchBus | Bus details fetched from DB.")
                return result
            else:
                print("FetchBus | Failed to fetch bus details from DB.")
                return False
        except Exception as e:
            mysql.connection.rollback()
            print(f"FetchBus | Error: {e}")
            return False
        finally:
            mycursor.close()

    def BusDetails(self):
        mycursor = mysql.connection.cursor()
        try:
            query = 'SELECT OPERATOR_NAME, TOTAL_SEATS, BASE_FARE FROM BUS_DETAILS WHERE BUS_ID=%s'
            value = (self.bus_id,)
            mycursor.execute(query, value)
            result = mycursor.fetchall()
            if result:
                print('BusDetails | Fetched bus details for adding travel')
                return result
            else:
                print('BusDetails | Bus details does not exist')
                return False
        except Exception as e:
            mysql.connection.rollback()
            print(f"BusDetails | Error: {e}")
            return False
        finally:
            mycursor.close()

    #For searching and fetching the bus details as per user preference.
    def SearchBus(self, action):

        #The user preference is obtained from the session data.
        source_location = session['source_location']
        destination_location = session['destination_location']
        source_date = session['source_date']

        #An instance of the class 'Travel' is created.
        travel = Travel('','','',source_location,destination_location,source_date,'','','','','','','','','')

        #Triggers 'UserBusSearch' method of the class 'Travel' using the object 'search_result'.
        #The action contains the action passed through the HTML form. (i.e Searchbus, EarlyDeparture etc.)
        search_result = travel.UserBusSearch(action)

        #Checks if the result of the method is 'True' or 'False'
        if search_result:
            #If the travel details are found, the return value is passed as the 'search_result' containing the data. 
            print('SearchBus | Travel details found for user input.')
            return search_result
        else:
            #If the travel details are not found, the return value is 'False'.
            print('SearchBus | No travel detail found for user input.')
            return False

#Attributes and methods responsible for managing the travel and its details.
class Travel:
    def __init__(self, travel_id, bus_id, operator_name, source_location, destination_location, source_date, destination_date, source_time, destination_time, travel_distance, total_fare, total_seats, available_seats, booked_seats, temporary_seats):
        self.travel_id = travel_id
        self.bus_id = bus_id
        self.operator_name = operator_name
        self.source_location = source_location
        self.destination_location = destination_location
        self.source_date = source_date
        self.destination_date = destination_date
        self.source_time = source_time
        self.destination_time = destination_time
        self.travel_distance = travel_distance
        self.total_fare = total_fare
        self.total_seats = total_seats
        self.available_seats = available_seats
        self.booked_seats = booked_seats
        self.temporary_seats = temporary_seats

    def AddTravel(self):
        mycursor = mysql.connection.cursor()
        try:
            query = 'INSERT INTO TRAVEL_DETAILS (BUS_ID,OPERATOR_NAME,SOURCE_LOCATION,DESTINATION_LOCATION,SOURCE_DATE,DESTINATION_DATE,SOURCE_TIME,DESTINATION_TIME,TRAVEL_DISTANCE,TOTAL_FARE,TOTAL_SEATS,AVAILABLE_SEATS,BOOKED_SEATS,TEMPORARY_SEATS) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
            values = (self.bus_id, self.operator_name, self.source_location, self.destination_location, self.source_date, self.destination_date, self.source_time, self.destination_time, self.travel_distance, self.total_fare, self.total_seats, self.available_seats, self.booked_seats, self.temporary_seats)
            mycursor.execute(query, values)
            mysql.connection.commit()
            if mycursor.rowcount > 0:
                print("AddTravel | Travel details added to the DB.")
                return True
            else:
                print("AddTravel | Failed to add travel details to DB.")
                return False
        except Exception as e:
            mysql.connection.rollback()
            print(f"AddTravel | Error: {e}")
            return False
        finally:
            mycursor.close()

    def RemoveTravelDetails(self, travel_id, action):
        mycursor = mysql.connection.cursor()
        try:
            query = 'SELECT BOOKING_ID, USER_ID, PASSENGERS, TOTAL_FARE, PAYMENT_STATUS, BOOKING_STATUS FROM BOOKING_DETAILS WHERE TRAVEL_ID = %s'
            value = (travel_id,)
            mycursor.execute(query, value)
            booking_details = mycursor.fetchall()
            if booking_details:
                print('RemoveTravelDetails | Fetched the booking details from DB.')
                total_bookings = len(booking_details)
                iteration = 0
                for details in booking_details:
                    booking_id = details[0]
                    booking = Booking('','','','','','','')
                    result = booking.CancelTicket(booking_id)
                    if result:
                        print(f'RemoveTravelDetails | Ticket has been cancelled for Booking ID: {booking_id}')
                        iteration += 1
                    else:
                        print(f'RemoveTravelDetails | Failed to cancel ticket for Booking ID: {booking_id}')
                        iteration += 1
                if iteration == total_bookings:
                    print(f'RemoveTravelDetails | All {total_bookings} bookings have been cancelled')
                    seat = Seat('','','','','','')
                    result = seat.RemoveSeat(travel_id)
                    if result:
                        print('RemoveTravelDetails | Seat details have been removed from DB.')
                        travel = Travel('','','','','','','','','','','','','','','')
                        result = travel.RemoveTravel(travel_id)
                        if result:
                            print('RemoveTravelDetails | Travel details removed from DB.')
                            return True
                        else:
                            print('RemoveTravelDetails | Failed to remove travel details from DB.')
                            return False
                    else:
                        print('RemoveTravelDetails | Failed to remove seat details from DB.')
                        return False
                else:
                    print(f'RemoveTravelDetails | Failed to cancel {total_bookings-iteration} bookings from DB.')
                    return False
            else:
                seat = Seat('','','','','','')
                result = seat.RemoveSeat(travel_id)
                if result:
                    print('RemoveTravelDetails | Seat details have been removed from DB.')
                    travel = Travel('','','','','','','','','','','','','','','')
                    result = travel.RemoveTravel(travel_id)
                    if result:
                        print('RemoveTravelDetails | Travel details removed from DB.')
                        return True
                    else:
                        print('RemoveTravelDetails | Failed to remove travel details from DB.')
                        return False
                else:
                    print('RemoveTravelDetails | Failed to remove seat details from DB.')
                    return False

        except Exception as e:
            mysql.connection.rollback()
            print(f'RemoveTravel | Error: {e}')
            return False
        finally:
            mycursor.close()
            
    def RemoveTravel(self, travel_id):
        mycursor = mysql.connection.cursor()
        try:
            query = 'DELETE FROM TRAVEL_DETAILS WHERE TRAVEL_ID = %s'
            value = (travel_id,)
            mycursor.execute(query, value)
            mysql.connection.commit()
            if mycursor.rowcount > 0:
                print(f'RemoveTravel | Travel detail deleted for Travel ID: {travel_id}')
                return True
            else:
                print(f'RemoveTravel | Failed to remove travel detail for Travel ID: {travel_id}')
                return False
        except Exception as e:
            mysql.connection.rollback()
            print(f'RemoveTravel | Error: {e}')
            return False
        finally:
            mycursor.close()

    def FetchTravel(self):
        mycursor = mysql.connection.cursor()
        try:
            query = 'SELECT TRAVEL_ID,BUS_ID,OPERATOR_NAME,SOURCE_LOCATION,DESTINATION_LOCATION,SOURCE_DATE,DESTINATION_DATE,SOURCE_TIME,DESTINATION_TIME,TRAVEL_DISTANCE,TOTAL_FARE FROM TRAVEL_DETAILS'
            value = ()
            mycursor.execute(query, value)
            result = mycursor.fetchall()
            if result:
                print("FetchTravel | Travel details fetched from DB.")
                return result
            else:
                print("FetchTravel | Failed to fetch travel details from DB.")
                return False
        except Exception as e:
            mysql.connection.rollback()
            print(f"FetchTravel | Error: {e}")
            return False
        finally:
            mycursor.close()

    def TravelDetails(self):
        mycursor = mysql.connection.cursor()
        try:
            query = 'SELECT TRAVEL_ID, TOTAL_FARE FROM TRAVEL_DETAILS WHERE BUS_ID=%s AND SOURCE_LOCATION=%s AND DESTINATION_LOCATION=%s AND SOURCE_DATE=%s AND DESTINATION_DATE=%s AND SOURCE_TIME=%s AND DESTINATION_TIME=%s'
            values = (self.bus_id, self.source_location, self.destination_location, self.source_date, self.destination_date, self.source_time, self.destination_time)
            mycursor.execute(query, values)
            result = mycursor.fetchall()
            if result:
                print("TravelDetails | Fetched travel details for adding seats.")
                return result
            else:
                print("TravelDetails | Failed to fetch travel details for adding seats.")
                return False
        except Exception as e:
            mysql.connection.rollback()
            print(f"TravelDetails | Error: {e}")
            return False
        finally:
            mycursor.close()

    #For updating the seat count in travel details.
    def SeatCountUpdation(self, action):
        mycursor = mysql.connection.cursor()
        try:
            #Executes if the action value is 'Fetch'.
            if action == 'Fetch':

                #The SQL query fetchces avaialble, booked, and temporary seat count from travel details using the travel ID as where value.
                query = 'SELECT AVAILABLE_SEATS, BOOKED_SEATS, TEMPORARY_SEATS FROM TRAVEL_DETAILS WHERE TRAVEL_ID = %s'
                values = (self.travel_id,)
                mycursor.execute(query, values)
                result = mycursor.fetchall()

                #Checks if the result contains the seat count data.
                if result:
                    #Returns the result.
                    print('SeatCountUpdation | Seat details fetched from DB.')
                    return result
                
                else:
                    #Returns 'False' is data is not found.
                    print('SeatCountUpdation | Failed to fetch seat details from DB.')
                    return False
                
            #Executes if the action value is 'Update'.
            if action == 'Update':

                #The SQL query updates the available, booked, and temporary seats count in travel details using the travel ID as where value.
                query = 'UPDATE TRAVEL_DETAILS SET AVAILABLE_SEATS=%s, BOOKED_SEATS=%s , TEMPORARY_SEATS = %s WHERE TRAVEL_ID=%s'
                values = (self.available_seats,self.booked_seats,self.temporary_seats,self.travel_id,)
                mycursor.execute(query, values)
                mysql.connection.commit()

                #Checks if the updation is successful by checking the updation count of cursor.
                if mycursor.rowcount > 0:
                    #Returns 'True' if the updation is successful.
                    print('SeatCountUpdation | Seat detail updated in DB.')
                    return True
                else:
                    #Returns 'False' if the updation is unsuccessful.
                    print('SeatCountUpdation | Failed to update seat detail in DB.')
                    return False
                
        #Prints the exception if raised.
        except Exception as e:
            mysql.connection.rollback()
            print(f"SeatCountUpdation | Error: {e}")
            return False
        
        #Cursor is closed to free up system resources and prevent memory leaks.
        finally:
            mycursor.close()

    #For searching the bus, sorting, and fetching bus details specifically.
    def UserBusSearch(self,action):
        mycursor = mysql.connection.cursor()
        try:
            #Query fetches the basic travel details by joining 'travel_details' and 'bus_details' on Bus ID for fetching the travel data along with the bus data and its amenities.
            query = 'SELECT TD.OPERATOR_NAME, TD.SOURCE_LOCATION, TD.DESTINATION_LOCATION, TD.SOURCE_DATE, TD.DESTINATION_DATE, TD.SOURCE_TIME, TD.DESTINATION_TIME, TD.TOTAL_FARE, TD.AVAILABLE_SEATS, TD.TRAVEL_ID, TD.BUS_ID, BD.BUS_TYPE, BD.RECLINING_SEATS, BD.CHARGING_POINTS, BD.WIFI, BD.BLANKETS_PILLOWS, BD.SNACKS, BD.MOVIE, BD.READING_LIGHT, BD.TRACK_MY_BUS, BD.M_TICKET, BD.OPERATOR_NUMBER, BD.BUS_NUMBER FROM TRAVEL_DETAILS TD INNER JOIN BUS_DETAILS BD ON TD.BUS_ID = BD.BUS_ID WHERE '

            #Ordering the travel details in ascending order by the departure time.
            if action == 'EarlyDeparture':
                query = query + 'TD.SOURCE_LOCATION=%s AND TD.DESTINATION_LOCATION=%s AND TD.SOURCE_DATE=%s ORDER BY TD.SOURCE_TIME ASC'
            
            #Ordering the travel details in descending order by the departure time.
            elif action == 'LateDeparture':
                query = query + 'TD.SOURCE_LOCATION=%s AND TD.DESTINATION_LOCATION=%s AND TD.SOURCE_DATE=%s ORDER BY TD.SOURCE_TIME DESC'

            #Ordering the travel details in ascending order by the earliest destination date and destination time.
            elif action == 'EarlyArrival':
                query = query + 'TD.SOURCE_LOCATION=%s AND TD.DESTINATION_LOCATION=%s AND TD.SOURCE_DATE=%s ORDER BY TD.DESTINATION_DATE ASC, TD.DESTINATION_TIME ASC'

            #Ordering the travel details in descending order by the late destination date and destination time.
            elif action == 'LateArrival':
                query = query + 'TD.SOURCE_LOCATION=%s AND TD.DESTINATION_LOCATION=%s AND TD.SOURCE_DATE=%s ORDER BY TD.DESTINATION_DATE DESC, TD.DESTINATION_TIME DESC'

            #Ordering the travel details in ascending order by the cheapest fare.
            elif action == 'CheapFare':
                query = query + 'TD.SOURCE_LOCATION=%s AND TD.DESTINATION_LOCATION=%s AND TD.SOURCE_DATE=%s ORDER BY TD.TOTAL_FARE ASC'

            #Ordering the travel details in descending order by the costliest fare.
            elif action == 'ExpensiveFare':
                query = query + 'TD.SOURCE_LOCATION=%s AND TD.DESTINATION_LOCATION=%s AND TD.SOURCE_DATE=%s ORDER BY TD.TOTAL_FARE DESC'
            
            #Ordering the travel details in ascending order by the lowest seat count available.
            elif action == 'LowSeats':
                query = query + 'TD.SOURCE_LOCATION=%s AND TD.DESTINATION_LOCATION=%s AND TD.SOURCE_DATE=%s ORDER BY TD.AVAILABLE_SEATS ASC'
            
            #Ordering the travel details in descending order by the highest seat count available.
            elif action == 'HighSeats':
                query = query + 'TD.SOURCE_LOCATION=%s AND TD.DESTINATION_LOCATION=%s AND TD.SOURCE_DATE=%s ORDER BY TD.AVAILABLE_SEATS DESC'
            
            #Reseting the travel details removing all the sorting.
            elif action == 'ResetSort':
                query = query + 'TD.SOURCE_LOCATION=%s AND TD.DESTINATION_LOCATION=%s AND TD.SOURCE_DATE=%s'
            
            #Selects the details using the travel ID for seat selection.
            elif action == 'SelectSeat' or action == 'TicketBooking' or action == 'CompareNow':
                query = query + 'TD.TRAVEL_ID=%s'

            #Selects the departure time before 6 AM.
            elif action == 'dep_before_6am':
                query = query + 'TD.SOURCE_LOCATION=%s AND TD.DESTINATION_LOCATION=%s AND TD.SOURCE_DATE=%s AND TD.SOURCE_TIME < "06:00:00"'


            #Default searching.
            else:
                query = query + 'SOURCE_LOCATION=%s AND DESTINATION_LOCATION=%s AND SOURCE_DATE=%s'

            #If the action is to select the seat count, the value to be passed is converted into int.
            if action == 'SelectSeat' or action == 'TicketBooking' or action=='CompareNow':
                values = (int(self.travel_id),)

            #If the action is other than the select seat, default values for searching and filter are passed.
            else:
                values = (self.source_location,self.destination_location,self.source_date)
            mycursor.execute(query, values)
            result = mycursor.fetchall()

            #Checks if the result fetched by the query contains data or not.
            if result:
                #If the data is available, it is returned back.
                print('UserBusSearch | Travel & Bus detail fetched from DB.')
                return result
            else:
                #If the data is not available, 'False' is returned.
                print('UserBusSearch | Travel & Bus details does not exist.')
                return False
            
        #Prints the exception if raised.
        except Exception as e:
            mysql.connection.rollback()
            print(f'UserBusSearch | Error: {e}')
            return False
        
        #Cursor is closed to free up system resources and prevent memory leaks.
        finally:
            mycursor.close()

#Attributes and methods responsible for managing the seat and its details.
class Seat:
    def __init__(self, seat_id, travel_id, bus_id, user_id, seat_number, seat_status):
        self.seat_id = seat_id
        self.travel_id = travel_id
        self.bus_id = bus_id
        self.user_id = user_id
        self.seat_number = seat_number
        self.seat_status = seat_status
    
    def AddSeat(self, total_seats):
        mycursor = mysql.connection.cursor()
        try:
            count = 0
            for self.seat_number in range(1, int(total_seats)+1):
                query = 'INSERT INTO SEAT_DETAILS (TRAVEL_ID, BUS_ID, SEAT_NUMBER) VALUES (%s,%s,%s)'
                values = (self.travel_id, self.bus_id, self.seat_number)
                mycursor.execute(query, values)
                mysql.connection.commit()
                count = count+1
            if count == total_seats:
                print('AddSeat | Seats details added to the DB.')
                return True
            else:
                print('AddSeat | Failed to add seat deails to DB.')
                return False
        except Exception as e:
            mysql.connection.rollback()
            print(f"AddTravel | Error: {e}")
            return False
        finally:
            mycursor.close()       

    def RemoveSeat(self, travel_id):
        mycursor = mysql.connection.cursor()
        try:
            query = 'DELETE FROM SEAT_DETAILS WHERE TRAVEL_ID = %s'
            value = (travel_id,)
            mycursor.execute(query, value)
            mysql.connection.commit()
            if mycursor.rowcount > 0:
                print(f'RemoveSeat | Seat detail deleted for Travel ID: {travel_id}')
                return True
            else:
                print(f'RemoveSeat | Failed to remove seat detail for Travel ID: {travel_id}')
                return False
        except Exception as e:
            mysql.connection.rollback()
            print(f'RemoveSeat | Error: {e}')
            return False
        finally:
            mycursor.close()
        
    def FetchSeat(self, travel_id):
        mycursor = mysql.connection.cursor()
        try:
            if travel_id == None:
                query = 'SELECT TRAVEL_ID, SEAT_ID, USER_ID, SEAT_NUMBER, SEAT_STATUS FROM SEAT_DETAILS'
                value = ()
            else:
                query = 'SELECT TRAVEL_ID, SEAT_ID, USER_ID, SEAT_NUMBER, SEAT_STATUS FROM SEAT_DETAILS WHERE TRAVEL_ID = %s'
                value = (travel_id,)
            mycursor.execute(query, value)
            result = mycursor.fetchall()
            if result:
                print('FetchSeat | Seat details fetched from DB.')
                return result
            else:
                print("FetchSeat | Failed to fetch seat details from DB.")
                return False
        except Exception as e:
            mysql.connection.rollback()
            print("FetchSeat | Error: {e}")
            return False
        finally:
            mycursor.close()

    #For fetching the seat number and seat status for seat visualisation during the seat selection process.
    def SeatDisplay(self):    
        mycursor = mysql.connection.cursor()
        try:
            #The query selects the seat number and its status using the travel ID.
            query = 'SELECT SEAT_NUMBER, SEAT_STATUS FROM SEAT_DETAILS WHERE TRAVEL_ID=%s'
            value = (self.travel_id,)
            mycursor.execute(query, value)
            result = mycursor.fetchall()
            
            #Checks if the result contains the seat data or not.
            if result:
                #If exists, the data is passed as return.
                print('SeatDisplay | Seat details fetched from DB')
                return result
            else:
                #If it does not exist, the return value is 'False'.
                print('SeatDisplay | Failed to fetch seat details from DB.')
                return False
            
        #Prints the exception if raised.
        except Exception as e:
            mysql.connection.rollback()
            print(f'SeatDisplay | Error: {e}')
            return False
        
        #Cursor is closed to free up system resources and prevent memory leaks.
        finally:
            mycursor.close()

    #For updating the status of the seat.
    def UpdateSeat(self):
        mycursor = mysql.connection.cursor()
        try:
            #The SQL query updates the seat status along with the user ID who choose the seat with travel ID and seat number as values.
            query = 'UPDATE SEAT_DETAILS SET SEAT_STATUS=%s, USER_ID=%s WHERE TRAVEL_ID=%s AND SEAT_NUMBER=%s'
            values = (self.seat_status,self.user_id,self.travel_id,self.seat_number)
            mycursor.execute(query,values)
            mysql.connection.commit()

            #After commit, the number of rows modified by the cursor is checked if it is greater than 0 to confirm updation.
            if mycursor.rowcount > 0:
                #Upon successful updation 'True' is returned.
                print(f'UpdateSeat | Seat Number: {self.seat_number} updated to {self.seat_status} in DB')
                return True
            else:
                #Upon failure, 'False' is returned.
                return False
            
        #Prints the exception if raised.
        except Exception as e:
            mysql.connection.rollback()
            print(f"UpdateSeat | Error: {e}")
            return False
        
        #Cursor is closed to free up system resources and prevent memory leaks.
        finally:
            mycursor.close()

    #For fetching the seat and travel details for seat selection visualisation.
    def SeatSelection(self, travel_id, action):
        try:
            #Creates an instance of the class 'Seat' and assigns it to object 'seat'.
            seat = Seat('',travel_id,'','','','')

            #Triggers the 'SeatDisplay' method of the class 'Seat' to fetch the seat details.
            seat_result = seat.SeatDisplay()

            #Checks if the seat data exists or not.
            if seat_result:

                #Creates an instance of the class 'Travel' and assigns it to object 'travel'.
                travel = Travel(travel_id,'','','','','','','','','','','','','','')

                #Triggers the 'UserBusSearch' method of the class 'Travel' to fetch the travel details.
                travel_result = travel.UserBusSearch(action)

                #Checks if the travel data exists or not.
                if travel_result:
                    #If exists, the seat and travel details are returned.
                    return seat_result, travel_result
                else:
                    #If it does not exist, return value is 'False'.
                    print('SeatSelection | Failed to fetch the travel details from DB..')
                    return False
            else:
                #If the seat details are not found, return value is 'False'.
                print('SeatSelection | Failed to fetch the seat details from DB.')
                return False
        
        #Prints the exception if raised.
        except Exception as e:
            print(f'SeatSelection | {e}')
            return False

    #For updating the seat status and count.
    def SeatTemporaryReservation(self, user_id, travel_id, selected_seats,passenger_count):
        try:
            #Count:  Default value for updating count during each for loop iteration.
            count = 1

            #Iteration: Default value for calculating the number of iterations.
            iteration = 0

            #The list 'selected_seats' contains the seat numbers chosen by the user.
            for seat_number in selected_seats:
                #Status is assigned as temporary to a variable and will be used in Update SQL operation.
                status = 'Temporary'

                #An instance of the class 'Seat' is created and is assigned to the object 'seat'.
                seat = Seat('',travel_id,'',user_id,seat_number,status)

                #Triggers 'UpdateSeat' of class 'Seat' that updates the status of seat.
                result = seat.UpdateSeat()

                #Checks the result of the seat status updation.
                if result:
                    print(f'SeatTemporaryReservation | Seat Number: {self.seat_number} Seat status has been updated successfully. ')

                    #An instance of the class 'Travel' is created and is assigned to the object 'travel'.
                    travel = Travel(travel_id,'','','','','','','','','','','','','','')

                    #Operation is set to 'Fetch' to get the counts of the seats.
                    operation = 'Fetch'

                    #Triggers 'SeatCountUpdation' of class 'Travel' by passing operation value 'Fetch' to fetch the seat counts.
                    result = travel.SeatCountUpdation(operation)
                    if result:
                        print('SeatTemporaryReservation | Seat count has been fetched successfully from DB.')

                        #The  tuple values are assigned to respective variables.
                        available_seats_db = result[0][0]
                        booked_seats_db = result[0][1]
                        temporary_seats_db = result[0][2]

                        #As it is for loop only 1 seat is modified, so the default value count is used to update the counts.
                        available_seats_db = available_seats_db - count
                        temporary_seats_db = temporary_seats_db + count

                        #An instance of the class 'Travel' is created using the updated seat count values and is assigned to the object 'travel'.
                        travel = Travel(travel_id,'','','','','','','','','','','',available_seats_db,booked_seats_db,temporary_seats_db)
                        operation = 'Update'

                        #Triggers 'SeatCountUpdation' of class 'Travel' by passing operation value 'Update' to update the seat counts.
                        result = travel.SeatCountUpdation(operation)

                        #Checks if the updation is successful.
                        if result:
                            #Upon successful updation the iteration value is incremented.
                            print(f'SeatTemporaryReservation | Seat Number: {self.seat_number} The seat status and count has been updated succesfully.')
                            iteration += 1
                        else:
                            #Upon failure to update seat count, it returns False.
                            print(f'SeatTemporaryReservation | Seat Number: {self.seat_number} Failed to update the seat status and count.')
                            return False
                    else:
                        #Upon failure to fetch seat count, it returns False.
                        print('SeatTemporaryReservation | Failed to fetch the seat count from DB.')
                        return False
                else:
                    #Upon failure to update seat status, it returns False.
                    print(f'SeatTemporaryReservation | Seat Number: {self.seat_number} Failed to update the seat status.')
                    return False
            
            #Checks if the iteration value is same as passenger count after iteration to verify successful updation.
            if iteration == passenger_count:
                print(f'SeatTemporaryReservation | Seat Number: {selected_seats} Status and count has been updated successfully.')
                #If the updation is complete, it returns True.
                return True
            else:
                #If it is incomplete, it returns False.
                print(f'SeatTemporaryReservation | Failed to update {passenger_count - iteration} seat status and count in DB.')
                False

        except Exception as e:
            print(f'SeatTemporaryReservation | Error: {e}')
            return False

#Attributes and methdods reponsible for managing the booking and its details.
class Booking:
    def __init__(self, booking_id, user_id, travel_id, passengers, total_fare, payment_status, booking_status):
        self.booking_id = booking_id
        self.user_id = user_id
        self.travel_id = travel_id
        self.passengers = passengers
        self.total_fare = total_fare
        self.payment_status = payment_status
        self.booking_status = booking_status

    #Inserts the booking details in the DB.
    def AddBookingDetails(self):
        mycursor = mysql.connection.cursor()
        try:
            #This query inserts the booking details in DB.
            query = 'INSERT INTO BOOKING_DETAILS (USER_ID, TRAVEL_ID, PASSENGERS, TOTAL_FARE) VALUES (%s,%s,%s,%s)'
            #The values are from the instance of the class.
            values = (self.user_id, self.travel_id, self.passengers, self.total_fare)
            mycursor.execute(query, values)
            mysql.connection.commit()

            #After commit, the number of rows modified by the cursor is checked if it is greater than 0 to confirm insertion.
            if mycursor.rowcount > 0:
                print('AddBookingDetails | Booking details added to DB (Created booking ID)')

                #The last inserted row's primary key is returned as booking ID.
                query = 'SELECT LAST_INSERT_ID() AS BOOKING_ID'
                mycursor.execute(query)
                result = mycursor.fetchall()
                if result:
                    #Assigns the result value as booking ID and returns it.
                    print('AddBookingDetails | Booking ID fetched from DB.')
                    booking_id = result[0][0]
                    return booking_id
                else:
                    #Returns 'False' indicating failure to fetch booking ID.
                    print('AddBookingDetails | Failed to fetch booking ID from DB.')
                    return False
            else:
                #Returns 'False' indicating failure to insert booking details in DB.
                print('AddBookingDetails | Failed to add booking details to DB.')
                return False
            
        #Prints the exception if raised.
        except Exception as e:
            mysql.connection.rollback()
            print(f'AddBookingDetails | Error: {e}')
            return False
        
        #Cursor is closed to free up system resources and prevent memory leaks.
        finally:
            mycursor.close()

    #Fetches the booking details to display in the ticket.
    def FetchBookingDetails(self):
        mycursor = mysql.connection.cursor()
        try:
            #Fetches the booking details based on the booking ID.
            query = 'SELECT TOTAL_FARE, PASSENGERS, PAYMENT_STATUS, BOOKING_STATUS, TRAVEL_ID, USER_ID FROM BOOKING_DETAILS WHERE BOOKING_ID = %s'
            values = (self.booking_id,)
            mycursor.execute(query, values)
            result = mycursor.fetchall()
            if result:
                print('FetchBookingDetails | Fetched booking details from DB.')
                return result
            else:
                print("FetchBookingDetails | Failed to fetch booking details from DB.")
                return False
            
        #Prints the exception if raised.
        except Exception as e:
            mysql.connection.rollback()
            print(f'FetchBookingDetails | Error: {e}')
            return False
        
        #Cursor is closed to free up system resources and prevent memory leaks.
        finally:
            mycursor.close()

    #Updates the booking and payment status.
    def UpdateBookingDetails(self):
        mycursor = mysql.connection.cursor()
        try:
            #The query updates the payment and booking status of a specific booking ID.
            query = 'UPDATE BOOKING_DETAILS SET PAYMENT_STATUS = %s, BOOKING_STATUS = %s WHERE USER_ID = %s AND BOOKING_ID = %s'
            values = (self.payment_status,self.booking_status,self.user_id, self.booking_id)
            mycursor.execute(query, values)
            mysql.connection.commit()

            #After commit, the number of rows modified by the cursor is checked if it is greater than 0 to confirm insertion.
            if mycursor.rowcount > 0:
                print(f'UpdateBookingDetails | Booking status updated {self.booking_status}.')
                return True
            else:
                print('UpdateBookingDetails | Failed to update booking details.')
                return False
            
        #Prints the exception if raised.
        except Exception as e:
            mysql.connection.rollback()
            print(f'UpdateBookingDetails | Error: {e}')
            return False
        
        #Cursor is closed to free up system resources and prevent memory leaks.
        finally:
            mycursor.close()

    def BookingHistory(self, action):
        mycursor = mysql.connection.cursor()
        try:
            if action == 'All':
                query = 'SELECT BOOKING_ID, USER_ID, TRAVEL_ID, PASSENGERS, TOTAL_FARE, PAYMENT_STATUS, BOOKING_STATUS FROM BOOKING_DETAILS'
                value = ()
            if action == 'Individual':
                query = 'SELECT BOOKING_ID, PASSENGERS, TOTAL_FARE, PAYMENT_STATUS, BOOKING_STATUS FROM BOOKING_DETAILS WHERE USER_ID = %s'
                value = (self.user_id,)
            mycursor.execute(query,value)
            result = mycursor.fetchall()
            if result:
                print('BookingHistory | Fetched booking details from DB.')
                return result
            else:
                print('BookingHistory | No data found on booking details in DB.')
                return result
        except Exception as e:
            mysql.connection.rollback()
            print(f'BookingHistory | Error: {e}')
            return False
        finally:
            mycursor.close()

    def ViewTicket(self, booking_id):
        booking = Booking(booking_id,'','','','','','')
        result1 = booking.FetchBookingDetails()
        if result1:
            print('ViewTicket | Booking details fetched from DB.')
            travel_id = result1[0][4]
            travel = Travel(travel_id,'','','','','','','','','','','','','','')
            result2 = travel.UserBusSearch('TicketBooking')
            if result2:
                print('ViewTicket | Travel details fetched from DB.')
                passenger = Passenger('',booking_id,travel_id,'','','','','')
                result3 = passenger.FetchPassengerDetails()
                if result3:
                    print('ViewTicket | Passenger details fetched from DB.')
                    return result1, result2, result3
                else:
                    print('ViewTicket | Failed to passenger travel details from DB.')
                    return False
            else:
                print('ViewTicket | Failed to booking travel details from DB.')
                return False
        else:
            print('ViewTicket | Failed to fetch travel details from DB.')
            return False
        
    def CancelTicket(self, booking_id):
        booking = Booking(booking_id,'','','','','','')
        result1 = booking.FetchBookingDetails()
        if result1:
            print('CancelTicket | Booking details fetched from DB.')
            total_fare = result1[0][0]
            passengers_count = result1[0][1]
            payment_status = result1[0][2]
            booking_status = result1[0][3]
            travel_id = result1[0][4]
            user_id = result1[0][5]
        if payment_status == 'Processed' and booking_status == 'Confirmed':
            print('CancelTicket | Payment details confirmed.')
            passenger = Passenger('',booking_id,travel_id,'','','','','')
            result2 = passenger.FetchPassengerDetails()
            if result2:
                print('CancelTicket | Passenger details fetched from DB.')
                iteration=0
                for i in range(passengers_count):
                    seat_number = result2[i][0]
                    seat = Seat('',travel_id,'','0',seat_number,'Available')
                    result3 = seat.UpdateSeat()
                    if result3:
                        print(f'CancelTicket | Seat Number: {seat_number} updated to available.')
                        iteration += 1
                    else:
                        return False
                if iteration==passengers_count:
                    print('CancelTicket | Seat status has been updated to available in DB.')
                    travel = Travel(travel_id,'','','','','','','','','','','','','','')
                    result4 = travel.SeatCountUpdation('Fetch')
                    if result4:
                        print('CancelTicket | Seat count fetched from travel details DB.')
                        available_seats_db = result4[0][0]
                        booked_seats_db = result4[0][1]
                        temporary_seats_db = result4[0][2]
                        available_seats_db = available_seats_db + passengers_count
                        booked_seats_db = booked_seats_db - passengers_count
                        travel = Travel(travel_id,'','','','','','','','','','','',available_seats_db,booked_seats_db,temporary_seats_db)
                        result5 = travel.SeatCountUpdation('Update')
                        if result5:
                            print('CancelTicket | Available and booked counts updated in DB.')
                            payment_manager = PaymentManager(user_id,'','','','','','','')
                            result6 = payment_manager.Transaction('MyJourney','Wallet',total_fare,'Credit')
                            if result6:
                                print('CancelTicket | Refund successful.')
                                booking = Booking(booking_id,user_id,travel_id,'','','Refunded','Cancelled')
                                result7 = booking.UpdateBookingDetails()
                                if result7:
                                    print('CancelTicket | Booking has been cancelled and fare refunded.')
                                    return True
                                else:
                                    print('CancelTicket | Failed to update the cancel status in booking DB.')
                                    return False
                            else:
                                print('CancelTicket | Failed to refund.')
                                return False
                        else:
                            print('CancelTicket | Failed to update available and booking count in travel DB.')
                            return False
                    else:
                        print('CancelTicket | Failed to fetch seat count from travel details DB.')
                        return False
                else:
                    print('CancelTicket | Failed to update seat status')
                    return False
            else:
                print('CancelTicket | Passenger details not found in DB.')
                return False
        else:
            print('CancelTicket | Payment not yet completed to cancel and refund.')
            return False

#Attributes and methods responsible for managing the booking and its details.
class Passenger:
    def __init__(self, passenger_id, booking_id, travel_id, seat_number, first_name, last_name, age, gender):
        self.passenger_id = passenger_id
        self.booking_id = booking_id
        self.travel_id = travel_id
        self.seat_number = seat_number
        self.first_name = first_name
        self.last_name = last_name
        self.age = age
        self.gender = gender

    #Adds the passenger details to DB.
    def AddPassengerDetails(self):
        mycursor = mysql.connection.cursor()
        try:
            #The query insert the passenger details in to DB. 
            query = 'INSERT INTO PASSENGER_DETAILS (BOOKING_ID, TRAVEL_ID, SEAT_NUMBER, FIRST_NAME, LAST_NAME, AGE, GENDER) VALUES (%s,%s,%s,%s,%s,%s,%s)'
            #The values are from the instance of the class.
            values = (self.booking_id, self.travel_id, self.seat_number, self.first_name, self.last_name, self.age, self.gender)
            mycursor.execute(query, values)
            mysql.connection.commit()

            #After commit, the number of rows modified by the cursor is checked if it is greater than 0 to confirm insertion.
            if mycursor.rowcount > 0:
                print('AddPassengerDetails | Passenger details added to DB.')
                return True
            else:
                print('AddPassengerDetails | Failed to add passenger details to DB.')
                return False
            
        #Prints the exception if raised.
        except Exception as e:
            mysql.connection.rollback()
            print(f'AddPassengerDetails | Error: {e}')
            return False
        
        #Cursor is closed to free up system resources and prevent memory leaks.
        finally:
            mycursor.close()

    #Fetches the passenger details to display in the ticket.
    def FetchPassengerDetails(self):
        mycursor = mysql.connection.cursor()
        try:
            #Fetches the passenger details using the booking ID.
            query = 'SELECT SEAT_NUMBER, FIRST_NAME, LAST_NAME, AGE, GENDER FROM PASSENGER_DETAILS WHERE BOOKING_ID = %s AND TRAVEL_ID = %s'
            values = (self.booking_id, self.travel_id)
            mycursor.execute(query, values)
            result = mycursor.fetchall()
            if result:
                print('FetchPassengerDetails | Fetched the passenger details from DB.')
                return result
            else:
                print('FetchPassengerDetails | Failed to fetch passenger details from DB.')
                return False
            
        #Prints the exception if raised.
        except Exception as e:
            mysql.connection.rollback()
            print(f"FetchPassengerDetails | Error: {e}")
            return False
        
        #Cursor is closed to free up system resources and prevent memory leaks.
        finally:
            mycursor.close()

#--------------|COMMON DASHBOARD|--------------#

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



