from setup import session, mysql

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
