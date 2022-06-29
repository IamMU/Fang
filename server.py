# Importing Libraries

import socket
import threading
import random
import json
from colorama import Fore, Back, Style, init as colorama_init
import time
from pprint import pprint
from utils import *
import time
import atexit
import sys

# Setting up colorama
colorama_init(autoreset=True)

log("info", "Imported all libraries.")

# Variables
log("info", "Defining variables...")

# CLIENT VARIABLES
clients = []

max_players = 2

current_players = 0

# Game
match_time = 120
time_remaining = match_time

start_game = False

number_of_catcher_positions = 1
number_of_runner_positions = max_players - number_of_catcher_positions

colors_catchers = ["#000000", "#0101a1"]
colors_runners = ["#FF0000", "#00FF00", "#0000FF", "#FF5555", "#55FF55", "#5555FF", "#AA0000", "#00AA00", "#0000AA"]

starting_positions_catchers = [(600, 150), (600, 200), (600, 250)]
starting_positions_runners = [(50, 50), (50, 100), (50, 150), (50, 200), (50, 250), (100, 75), (100, 125), (100, 175)]

time_before_starting_game = 5

# SERVER SIDE
server = None
stop_threads = False

data_to_send = {
    'player-data': {},
    'time-remaining': time_remaining,
    'start-game': start_game,
    'max-players': max_players,
    'joined-players': current_players
}

log("success", "Defined all variables.")

# Constants
log("info", "Defining constants...")

# SERVER SIDE
HOST_NAME = socket.gethostname()
SERVER_IP = socket.gethostbyname(HOST_NAME)
SERVER_PORT = 5555
SERVER_ADDRESS = (SERVER_IP, SERVER_PORT)

# COMMUNICATION CONSTANTS
ENCODING_FORMAT = "ascii"

MESSAGE_DISCONNECTION_CLIENT = 'ClientDisconnect'
MESSAGE_DISCONNECTION_SERVER = 'ServerError'

MESSAGE_START = "[ MESSAGE STARTING NOW ]"
MESSAGE_ENDING = "[ END MESSAGE HERE ]"


log("success", "Defined all constants")

# Functions
log("info", "Defining functions...")


def close_server():
    # Global variables
    global stop_threads

    # Functionality
    log("info", "Closing server...")

    log("info", "Sending disconnection messages...")

    broadcast(MESSAGE_DISCONNECTION_SERVER.encode(ENCODING_FORMAT))

    log('success', "Disconnection messages sent to clients!")

    log('info', "Stopping all threads...")

    stop_threads = True

    log("success", "All threads have been stopped!")

    log("info", "Closing server...")

    server.close()

    log("success", "Server has been closed!")

    log("info", "Exiting...")

    sys.exit()


def broadcast(data, exclude=None):
    # Global variables
    global current_players

    # Other
    # log("info", "Broadcasting data...")

    try:
        for index, client in enumerate(clients):
            if exclude:
                if client == exclude:
                    continue
                else:
                    try:
                        client.send(data)
                    except Exception as e:
                        log("error", f"Unable to send data to client#{index + 1}")
                        log("exception", e)
                        clients.remove(client)
                        current_players -= 1
                        log("info", f"Client#{index} has been disconnected!")
            else:
                try:
                    client.send(data)
                except Exception as e:
                    log("error", f"Unable to send data to client#{index + 1}")
                    log("exception", e)
                    clients.remove(client)
                    current_players -= 1
                    log("info", f"Client#{index} has been disconnected!")
    except Exception as e:
        log("error", "Unable to broadcast data to clients!")
        log("exception", e)

    # log('broadcast', f"{data.decode(ENCODING_FORMAT)}")


def server_controller():
    print('info', "Server controller is active now!")

    user_input = ""

    # Loop
    while not stop_threads:
        # Checking if we need to close the thread
        if stop_threads:
            break

        user_input = input()

        # TODO: Make functionality for the server controller

    # Telling that the thread is closing
    log("info", "Server controller thread has been closed!")


def handle_broadcasting():
    # Loop
    while True:
        # Checking if we need to close the thread
        if stop_threads:
            break

        # Converting data to json
        try:
            data_to_send_json = json.dumps(data_to_send)

            data_to_send_json_safe = MESSAGE_START + data_to_send_json + MESSAGE_ENDING

            data_to_send_json_safe_encoded = data_to_send_json_safe.encode(ENCODING_FORMAT)

            broadcast(data_to_send_json_safe_encoded)
        except Exception as e:
            log("error", "Unable to broadcast data to clients!")
            log("exception", e)

        time.sleep(0.06)

    # Telling that the thread is closing
    log("info", "Broadcasting thread has been closed!")


def add_starting_information(received_data, index):
    # Global variables
    global number_of_catcher_positions
    global number_of_runner_positions

    # Local variables
    # role = ""
    # color = ""

    # Functionality
    try:
        # Setting up the username
        try:
            username = received_data['username']
        except Exception as e:
            log("error", f"Unable to get username for client#{index}")
            log("exception", e)

        # Setting role for client
        is_catcher = True if random.randint(0, 10) % 2 == 0 else False
        log("info", f"Is Catcher: {is_catcher}")

        # try:
        try:
            if is_catcher and number_of_catcher_positions > 0:
                log("info", "Role --> Catcher")
                role = "catcher"
                number_of_catcher_positions -= 1
        except Exception as e:
            log("error", "Unable to set catcher role for client!")
            log("exception", e)

        # return None

        try:
            if not is_catcher and number_of_runner_positions > 0:
                log("info", "Role --> Runner")
                role = "runner"
                number_of_runner_positions -= 1
        except Exception as e:

            if not is_catcher and number_of_runner_positions > 0:
                role = "runner"
                number_of_runner_positions -= 1
            elif is_catcher and number_of_catcher_positions > 0:
                role = "catcher"
                number_of_catcher_positions -= 1

            log("error", "Unable to set runner role for client!")
            log("exception", e)
        except Exception as e:
            log("exception", e)
        # except Exception as e:
        #     log("error", f"Unable to set role for client#{index}")
        #     log("exception", e)

        try:
            log("info", f"Role: {role}")
        except Exception as e:
            log("error", "Unable to access role!")
            log("exception", e)

        # Setting color for client
        try:
            try:
                if role == "catcher":
                    color = random.choice(colors_catchers)
                    colors_catchers.remove(color)
            except Exception as e:
                log("error", "Unable to set catcher color!")
                log("exception", e)

            try:
                if role == "runner":
                    color = random.choice(colors_runners)
                    colors_runners.remove(color)
            except Exception as e:
                log("error", "Unable to set runner color!")
                log("exception", e)
        except Exception as e:
            log("error", f"Unable to set color for client#{index}")
            log("exception", e)

        try:
            log("info", f"Color: {color}")
        except Exception as e:
            log("error", "Unable to access color!")
            log("exception", e)

        # Setting starting position
        try:
            try:
                if role == "catcher":
                    starting_position = random.choice(starting_positions_catchers)
                    starting_positions_catchers.remove(starting_position)
            except Exception as e:
                log("error", "Unable to get starting position for client!")
                log("exception", e)

            try:
                if role == "runner":
                    starting_position = random.choice(starting_positions_runners)
                    starting_positions_runners.remove(starting_position)
            except Exception as e:
                log("error", "Unable to get starting position for client!")
                log("exception", e)
        except Exception as e:
            log("error", f"Unable to set starting position for client#{index}")
            log("exception", e)

        try:
            log('info', f"Starting position: {starting_position}")
        except Exception as e:
            log("error", "Unable to access starting position!")
            log("exception", e)

        # Get starting position based on role

        # Making all the data into a dict
        try:
            data = {
                "username": str(username),
                "role": str(role),
                "color": color,
                "starting-position": starting_position
            }
        except Exception as e:
            log("error", f"Unable to make starting data for client#{index}")
            log("exception", e)

        log("info", f"Data: {data}")

        # Adding data to all data
        try:
            data_to_send['player-data'][username] = data
            log("info", f"New Data: {data_to_send}")
        except Exception as e:
            log("error", "Unable to add starting data to sending data!")
            log("exception", e)
    except Exception as e:
        log("error", f"Unable to get starting information for client#{index}")
        log('exception', e)
        return None

    return username


def update_data(received_data, index, username, set_p_to_sp=False):
    log("info", f'Updating data for {username}')
    try:
        # Updating start game value
        if current_players >= max_players:
            data_to_send['start-game'] = True
        else:
            data_to_send['start-game'] = False

        # Getting the positional data
        try:
            if set_p_to_sp:
                position = data_to_send['player-data'][username]['starting-position']
            else:
                position = received_data['position']
        except Exception as e:
            log("error", f"Unable to get position for client#{index}")
            log("exception", e)
            log("info", data_to_send)

        # Getting response if player got caught
        try:
            caught = received_data['caught']
        except Exception as e:
            log("error", f'Unable to get caught value from client#{index}')
            log("exception", e)

        # Adding data to all data
        try:
            log('info', data_to_send['player-data'][username])
            data_to_send['player-data'][username]['position'] = position
            data_to_send['player-data'][username]['caught'] = caught
        except Exception as e:
            log("error", "Unable to add updated data to sending data!")
            log("exception", e)
    except Exception as e:
        log("error", f"Unable to get starting information for client#{index}")

    log("success", f"Updated data for client#{index} ({username})")


def match_timer():
    pass
    # # Global variable
    # global start_game
    #
    # # Function
    # time_to_start_game = time_before_starting_game
    # game_time = match_time
    #
    # while not stop_threads:
    #     if current_players >= max_players:
    #         start_game = True
    #     else:
    #         start_game = False
    #
    #     while not start_game:
    #         # clear_screen()
    #         log("info", start_game)
    #         if start_game:
    #             break
    #
    #         log("info", "Match timer waiting...")
    #
    #     while start_game:
    #         if not start_game:
    #             break
    #
    #         log("success", "Match timer started!")
    #
    #         while not time_to_start_game <= 0:
    #             if time_to_start_game <= 0:
    #                 break
    #
    #             clear_screen()
    #             time_to_start_game -= 1
    #             time.sleep(1)
    #             log(f"Time to start game: {Fore.MAGENTA}{str(time_to_start_game)}")
    #
    #         while not game_time <= 0:
    #             if game_time <= 0:
    #                 break
    #
    #             log("info", f"Time Remaining to Game END: {game_time}")
    #             game_time -= 1
    #             time.sleep(1)
    #
    #         start_game = False


def handle_client_receiving(conn, addr):
    # Global variables
    global current_players

    # Local variables
    set_position_to_starting_position = True

    # Function

    # Updating value of current_players
    current_players += 1

    client_number = len(clients)

    log('success', f"Client handler thread for client#{client_number} has been created!")

    # Getting and adding starting information from the client
    log("info", f"Getting starting information from client#{client_number}!")

    try:
        starting_data_from_client = json.loads(conn.recv(1024).decode(ENCODING_FORMAT).split(MESSAGE_ENDING)[0].split(MESSAGE_START)[1])
        log("receiv", f"[ RECEIVING STARTING DATA ] {starting_data_from_client}")
    except Exception as e:
        log("error", f"Unable to get starting information from client#{client_number}!")
        log("exception", e)

    try:
        client_username = add_starting_information(starting_data_from_client, client_number)
    except Exception as e:
        log("Error", "Unable to add starting information to main data!")
    log("success", "Starting information has been collected successfully!")

    log("info", f"{client_username} has joined the server successfully!")
    # Loop
    while True:
        # Checking if we need to close the thread
        if stop_threads:
            break

        try:
            recv_data = conn.recv(1024).decode(ENCODING_FORMAT)
        except Exception as e:
            log("error", f"Unable to receive data from client#{client_number}")
            log("exception", e)

        if recv_data:
            try:
                # log("receiv", recv_data)

                try:
                    recv_data = recv_data.split(MESSAGE_ENDING)[0].split(MESSAGE_START)[1]
                    recv_data = json.loads(recv_data)
                except IndexError as e:
                    log("receiv", recv_data)
                    log("error", "Unable to remove protocols from received message!")
                    log('exception', e)
                    try:
                        recv_data = recv_data.replace(MESSAGE_START, "").replace(MESSAGE_ENDING, "")
                    except Exception as e:
                        log('exception', e)

                # log('receive', recv_data)
            except IndexError as e:
                log("receiv", recv_data)
                log("error", "Unable to get client data")
                log("exception", e)
            except Exception as e:
                log("receiv", recv_data)
                log("error", "Unable to receive msg from client")
                log("exception", e)

            # log("received", recv_data)

            # Updating value of joined players in all data to send to clients
            data_to_send['joined-players'] = current_players

            try:
                update_data(recv_data, client_number, client_username, set_position_to_starting_position)
                set_position_to_starting_position = False
            except Exception as e:
                pass

            # Test
            # time.sleep(0.0)

    # Telling that the thread is closing
    log("info", f"Client handler thread for client#{client_number} has been closed!")
    current_players -= 1


def run():
    # Global variables
    global server

    # Functionality

    # Making server socket
    log("info", "Making server socket...")

    try:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except Exception as e:
        log("error", "Unable to make server socket!")
        log("exception", e)
        return 1

    log("success", "Server socket made!")

    # Connecting server socket
    log("info", "Binding server socket...")

    try:
        server.bind(SERVER_ADDRESS)
    except Exception as e:
        log("error", "Unable to bind server socket!")
        log("exception", e)
        return 1

    log("success", "Server socket bound to address!")

    # Clearing screen
    log("info", "Clearing screen...")

    clear_screen()

    # Creating match timer thread
    log("info", "Creating match timer thread...")

    try:
        match_timer_thread = threading.Thread(target=match_timer)
        match_timer_thread.start()
    except Exception as e:
        log("error", "Unable to make match timer thread!")
        log("exception", e)

        return 1

    log("success", "Broadcasting thread has been created!")

    # Creating broadcast thread
    log("info", "Creating broadcasting thread...")

    try:
        broadcast_thread = threading.Thread(target=handle_broadcasting)
        broadcast_thread.start()
    except Exception as e:
        log("error", "Unable to make broadcasting thread!")
        log("exception", e)

        return 1

    log("success", "Broadcasting thread has been created!")

    # Creating server controller thread
    log("info", "Creating server controller thread...")

    try:
        server_controller_thread = threading.Thread(target=server_controller)
        server_controller_thread.start()
    except Exception as e:
        log("error", "Unable to make server controller thread!")
        log("exception", e)

        return 1

    log("success", "Server controller thread has been created!")

    # Telling the ip and port of the server for ease of use
    log("info", f"Server running at {SERVER_ADDRESS[0]}:{SERVER_ADDRESS[1]}")

    # Listening for connections
    log("info", f"Listening for connections...(Max allowed: {max_players})")

    server.listen(max_players)

    while True:
        if current_players <= max_players:
            # Accepting connections
            connection, address = server.accept()

            # When connections get accepted

            log("info", f"New connection from {address[0]}:{address[1]}!")

            # Adding new client to clients list
            try:
                clients.append(connection)
            except Exception as e:
                log("error", f"Unable to add client#{len(clients)} to the clients list!")
                log("exception", e)

            log("success", "Client added to clients list")

            # Initialize starting information
            log("info", f"Creating starting information for client#{len(clients)}")

            log("success", f"Created starting information for client#{len(clients)}")

            # Creating threads for the client
            log("info", f"Creating threads for the client#{len(clients)}...")

            # TODO: Create threads
            client_receiving_thread = threading.Thread(target=handle_client_receiving, args=(connection, address))
            client_receiving_thread.start()

            log("success", f"Threads for client#{len(clients)} have been created!")


log("success", "Defined all functions")

# Other
if __name__ == "__main__":
    # Adding stuff that we need to do when script is closed
    atexit.register(close_server)

    # Running the server
    log("info", "Running server...")
    run()
    log("info", "Closing server...")
