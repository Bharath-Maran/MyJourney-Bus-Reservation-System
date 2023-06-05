from setup import session, mysql

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
