from setup import session, mysql

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
