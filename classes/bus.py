from setup import session, mysql

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
                    from classes.travel import Travel
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
        from classes.travel import Travel
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
