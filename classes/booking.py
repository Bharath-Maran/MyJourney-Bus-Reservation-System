from setup import session, mysql
from classes.passenger import Passenger
from classes.paymentmanager import PaymentManager

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
            from classes.travel import Travel
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
                    from classes.seat import Seat
                    seat = Seat('',travel_id,'','0',seat_number,'Available')
                    result3 = seat.UpdateSeat()
                    if result3:
                        print(f'CancelTicket | Seat Number: {seat_number} updated to available.')
                        iteration += 1
                    else:
                        return False
                if iteration==passengers_count:
                    from classes.travel import Travel
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
