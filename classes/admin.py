from setup import session, mysql
from classes.user import User

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
                print(result)
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
