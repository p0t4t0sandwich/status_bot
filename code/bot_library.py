#!/bin/python3
#--------------------------------------------------------------------
# Project: Bot Function Library
# Purpose: Simplify creation of Discord bots.
# Author: Dylan Sperrer (p0t4t0sandwich|ThePotatoKing)
# Date: 10AUGUST2021
# Updated: 3AUGUST2022 - p0t4t0sandwich
#   - Added the linking database logic to be shared between bots.
#--------------------------------------------------------------------

# Function for simple logging
def bot_logger(path, bot, string):
    from datetime import datetime
    import os
    """
    Purpose:
        Logs the String with a time and date into bot.log.
    Pre-Conditions:
        :param string: The text to send to the log file
        :param bot: The name of the bot using the log function.
        :param path: Filepath of where to save the log file.
    Post-Conditions:
        Saves all necessary data to the log file.
    Return:
        None
    """
    now = str(datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
    folder = path
    if not os.path.exists(folder):
        os.makedirs(folder)
    try:
        file = open(folder + bot + ".log", "a")
    except:
        file = open(folder + bot + ".log", "w")
        file.close()
        file = open(folder + bot + ".log", "a")
    file.write("[" + now + "]: [" + bot + " Log] " + string + "\n")
    print("[" + now + "]: [" + bot + " Log] " + string)
    file.close()

def get_twitch_id(twitch_name):
    import os
    import requests
    import json
    """
    Purpose:
        Uses the Twitch API to collect a user id from a username.
    Pre-Conditions:
        :param twitch_name: The username of the Twitch user to collect the id of.
    Post-Conditions:
        None
    Return:
        The Twitch user id of the specified user.
    """
    client_id = os.getenv("TWITCH_CLIENT_ID")
    
    token_response = requests.post(
        'https://id.twitch.tv/oauth2/token',
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            },
        data = {
            'client_id': client_id,
            'client_secret': os.getenv("TWITCH_CLIENT_SECRET"),
            'grant_type': 'client_credentials'
        }
    )

    twitch_id_response = requests.get(
        'https://api.twitch.tv/helix/users',
        headers = {
            'Authorization': 'Bearer ' + json.loads(token_response.content)["access_token"],
            'Client-Id': client_id,
            },
        params=(('login', twitch_name),)
        )

    return json.loads(twitch_id_response.content)["data"][0]["id"]

# Function for linking different media accounts to the database.
def link_account(from_platform, from_platform_username, from_platform_id, to_platform, to_platform_username):
    import mysql.connector
    from mysql.connector import errorcode
    import os
    """
    Purpose:
        To link user accounts within the database.
    Pre-Conditions:
        :param from_platform: The platform the user is linking from.
        :param from_platform_username: The "from" platform username of the user.
        :param from_platform_id: The "from" platform username id of the user.
        :param to_platform: The platform the user is linking to.
        :param to_platform_username: The "to" platform username of the user.
    Post-Conditions:
        Link the specified user data within the database
    Return:
        A message notifying the user of their success/failure.
    """
    config = {
            'user': os.getenv("MYSQL_USER"),
            'password': os.getenv("MYSQL_PASSWORD"),
            'host': os.getenv("MYSQL_HOST"),
            'database': os.getenv("MYSQL_DATABASE"),
            'raise_on_warnings': True
        }

    # Simple injection sterilization
    from_platform = from_platform.replace("--","").replace("/*","").replace("%00","").replace("%16","")
    from_platform_username = from_platform_username.replace("--","").replace("/*","").replace("%00","").replace("%16","")
    from_platform_id = str(from_platform_id)
    to_platform = to_platform.replace("--","").replace("/*","").replace("%00","").replace("%16","")
    to_platform_username = to_platform_username.replace("--","").replace("/*","").replace("%00","").replace("%16","")

    err_msg = f"""
            There doesn't seem to be a MC username linked with your account, @{from_platform_username}.
            Please login to our MC server (!ip) if you haven't already, and then use: "!link minecraft [username]".
            Use "!link help" for details on usage.
            """

    account_data = {
        "from_platform": from_platform,
        "from_platform_username": from_platform_username,
        "from_platform_id": from_platform_id,
        "to_platform": to_platform,
        "to_platform_username": to_platform_username
    }

    try:
        cnx = mysql.connector.connect(**config)
        cursor = cnx.cursor()

        if to_platform == "minecraft":
            mc_id_query = "SELECT player_id FROM player_data WHERE player_name = %(to_platform_username)s"
        else:
            mc_id_query = "SELECT player_id FROM linked_accounts WHERE " + from_platform + " = %(from_platform_username)s"

        cursor.execute(mc_id_query, account_data)

        data = cursor.fetchall()
        if data != []:
            account_data["player_id"] = str(data[0][0])
        else:
            return err_msg

        # Creates new entry if player not referenced in linked_accounts, otherwise updates entry.
        init_row_query = (
                "INSERT INTO linked_accounts (player_id)"
                "SELECT (" + account_data["player_id"] + ")"
                "FROM DUAL WHERE NOT EXISTS (SELECT * FROM linked_accounts "
                "WHERE player_id = " + account_data["player_id"] + " LIMIT 1)"
                )
        cursor.execute(init_row_query, account_data)
        cnx.commit()

        if to_platform != "minecraft":
            # Link TO platform account
            link_account_query = (
                "UPDATE linked_accounts SET " + to_platform + " = %(to_platform_username)s WHERE player_id = " + account_data["player_id"] + ";"
            )
            cursor.execute(link_account_query, account_data)
            
            # Grab the Twitch id from the Twitch API
            if to_platform == 'twitch':
                twitch_id = get_twitch_id(to_platform_username)
                link_account_id_query = (
                    "UPDATE linked_accounts SET " + to_platform + "_id = " + twitch_id + " WHERE player_id = " + account_data["player_id"] + ";"
                )
                cursor.execute(link_account_id_query, account_data)

            cnx.commit()

        # Gather FROM user info
        if from_platform in ['discord', 'twitch']:
            platform_username_query = (
                "UPDATE linked_accounts SET " + from_platform + " = %(from_platform_username)s WHERE player_id = " + account_data["player_id"] + ";"
            )
            platform_id_query = (
                "UPDATE linked_accounts SET " + from_platform + "_id = " + from_platform_id + " WHERE player_id = " + account_data["player_id"] + ";"
            )
            cursor.execute(platform_username_query, account_data)
            cursor.execute(platform_id_query, account_data)
            cnx.commit()

            cursor.close()
            cnx.close()

        return f"You have successfully linked your {to_platform} account!"

    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with your user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)
    else:
        cnx.close()
