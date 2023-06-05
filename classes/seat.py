from setup import session, mysql

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
                from classes.travel import Travel
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
                    from classes.travel import Travel
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
