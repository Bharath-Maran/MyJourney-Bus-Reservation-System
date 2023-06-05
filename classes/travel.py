from setup import session, mysql
from classes.seat import Seat
from classes.booking import Booking

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
