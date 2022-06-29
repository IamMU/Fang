# Importing Libraries
import random
import socket
import json
import threading
import time

import pygame
import pygame_widgets
from pygame_widgets.button import Button
from pygame_widgets.textbox import TextBox
from utils import log
from player import Player

log("success", "All libraries have been imported!")

# Initializing pygame
log('info', "Initializing pygame...")

pygame.init()

log("success", "Pygame has been initialized!")

# Variables
log("info", "Defining variables...")

# Game
quit_game = False
start_game = False

runners = []
catchers = []

# Screen displays
display_main_menu = True
display_connecting_screen = False
display_connection_screen = False
display_connection_failed_screen = False
display_waiting_queue_screen = False
display_game_starting_screen = False
display_game = False
display_disconnection_screen = False
display_error_screen = False

# Initializing variables
initialized_main_menu = False
initialized_connection_screen = False
initialized_connecting_screen = False
initialized_connection_failed_screen = False
initialized_waiting_queue_screen = False
initialized_disconnection_screen = False
initialized_error_screen = False

initialized_game_onetime_data = False

# Main menu screen
buttons_main_menu_screen = []

# Connection screen
widgets_connection_screen = []

# Connecting screen
connecting_screen_text_dots = ['.', '..', '...', '....']
connecting_screen_text_dot_index = 0

# Connection failed screen
widgets_connection_failed_screen = []

# Error screen
widgets_error_screen = []

# Disconnection screen
widgets_disconnection_screen = []

# Game starting screen
time_to_start_game = 3
time_to_display_role = 2

# Waiting queue screen
max_players = 0
joined_players = 0

waiting_queue_screen_text_dots = [".", "..", "...", "...."]
waiting_queue_screen_text_dot_index = 0

widgets_waiting_queue_screen = []

# Fonts
font_gigantic = pygame.font.SysFont("monospace", 90)
font_giant = pygame.font.SysFont("monospace", 74)
font_big = pygame.font.SysFont("monospace", 40)
font_small_big = pygame.font.SysFont("monospace", 30)
font_normal = pygame.font.SysFont("monospace", 20)
font_small = pygame.font.SysFont("monospace", 12)

# Player
player_position = (0, 0)
username = f"Player#{random.randint(0, 50)}"
role = "none"

time_to_allow_catching = 20

log("success", "All variables have been defined!")

is_caught = False

# Server/Client connection
client = None
data_to_send = {
    "position": (0, 0),
    "caught": is_caught
}

time_remaining = 0

all_players = {}

# Thread
stop_threads = False

# Constants
log("info", "Defining constants...")

# Window
WINDOW_TITLE = "Fang!"

WINDOW_WIDTH = 650
WINDOW_HEIGHT = 600

WINDOW_CENTER_X = int(WINDOW_WIDTH/2)
WINDOW_CENTER_Y = int(WINDOW_HEIGHT/2)

WINDOW_BACKGROUND_COLOR = (0, 0, 0)
WINDOW_IN_GAME_BACKGROUND_COLOR = (255, 255, 255)

WINDOW_FPS = 60

# Text
TEXT_COLOR = (255, 255, 255)
TEXT_COLOR_IN_GAME = (0, 0, 0)

# Button
BUTTON_WIDTH = 100
BUTTON_HEIGHT = 40

BUTTON_BACKGROUND_COLOR = (255, 255, 0)
BUTTON_HOVER_COLOR = (0, 0, 255)
BUTTON_CLICKED_COLOR = (255, 255, 255)

# Text Boxes
TEXT_BOX_WIDTH = 250
TEXT_BOX_HEIGHT = 30

TEXT_BOX_BORDER_COLOR = (255, 255, 255)
TEXT_BOX_BORDER_WIDTH = 1
TEXT_BOX_FONT_SIZE = 25

TEXT_BOX_RADIUS = 5

TEXT_BOX_BACKGROUND_COLOR = WINDOW_BACKGROUND_COLOR

ENCODING_FORMAT = 'ascii'

MESSAGE_ENDING = "[ END MESSAGE HERE ]"
MESSAGE_START = "[ MESSAGE STARTING NOW ]"

MESSAGE_DISCONNECTION_CLIENT = 'ClientDisconnect'
MESSAGE_DISCONNECTION_SERVER = 'ServerError'

################################
### TESTING VARIABLES #########
wrong = 0
correct = 0
total = 0

x = 0
y = 0
#############################

log("success", "All constants have been defined!")

# Making window
log("info", "Making pygame window...")

window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))

# Changing title
pygame.display.set_caption(WINDOW_TITLE)

log("success", "Pygame window has been initialized!")


# Classes
class UserClient(socket.socket):
    def __init__(self, client_username, ip="127.0.1.1", port=5555, encoding_format="ascii"):
        super().__init__(socket.AF_INET, socket.SOCK_STREAM)

        # Variables
        self.SERVER_IP = str(ip)

        try:
            self.SERVER_PORT = int(port)
        except Exception as e:
            log('error', "Unable to set server port!")
            log("exception", e)
            log("info", "Using default port 5555")
            self.SERVER_PORT = 5555

        self.username = client_username

        self.encoding_format = encoding_format

        # Connecting to server
        self.connect_to_server()

    def connect_to_server(self):
        # Global variables
        global stop_threads

        try:
            self.connect((self.SERVER_IP, self.SERVER_PORT))

            # Going to waiting queue
            go_to_waiting_screen()
        except Exception as e:
            log("error", f"Unable to connect to server -> {self.SERVER_IP}:{self.SERVER_PORT}")
            log("exception", e)
            stop_threads = True
            go_to_connection_failed_screen()

    def send_data(self, data):
        # Global variables
        global stop_threads

        # Other
        data_json = json.dumps(data)
        # log('sending', data_json)
        data_json_with_protocols = MESSAGE_START + data_json + MESSAGE_ENDING
        data_encoded = data_json_with_protocols.encode(self.encoding_format)

        try:
            self.send(data_encoded)
        except Exception as e:
            log("error", "Unable to send data to server!")
            log("exception", e)

            go_to_error_screen()
            stop_threads = True

    def receive_data(self):
        data_received = self.recv(1024)

        try:
            try:
                data_received = data_received.decode(self.encoding_format)
            except Exception as e:
                log('exception', e)

            try:
                data_received = data_received.split(MESSAGE_ENDING)[0]
            except Exception as e:
                log('error', data_received)
                log("exception", e)
                return 'error'

            try:
                data_received = data_received.split(MESSAGE_START)[1]
            except Exception as e:
                log('error', data_received)
                log("exception", e)

            try:
                data_received = json.loads(data_received)
            except Exception as e:
                log('exception', e)
            # log('receiv', data_received)

            return data_received
        except Exception as e:
            log("error", "Unable to remove protocols in received message!")
            log("exception", e)

            return None

    def send_normal_data(self, data):
        # Global variables
        global stop_threads

        # Other
        log('sending', data)
        data_with_protocols = MESSAGE_START + data + MESSAGE_ENDING
        data_encoded = data_with_protocols.encode(self.encoding_format)

        try:
            self.send(data_encoded)
        except Exception as e:
            log("error", "Unable to send data to server!")
            log("exception", e)

            go_to_error_screen()
            stop_threads = True


# Functions
log("info", "Defining functions...")


def movement():
    global x
    global y

    keys = pygame.key.get_pressed()

    if keys[pygame.K_w]:
        y += 1
        print("UP")

    if keys[pygame.K_s]:
        y -= 1
        print("DOWN")

    if keys[pygame.K_a]:
        x -= 1

    if keys[pygame.K_d]:
        x += 1

    print(x, y)


def conn():
    log("Making pygame screens...")
    global wrong
    global correct
    global total
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(("127.0.1.1", 5556))

    starting_data = {
        "username": "i guy"
    }

    updated_data = {
        "position": (100, 150),
        "caught": False
    }

    client.send(json.dumps(starting_data).encode(ENCODING_FORMAT))

    time.sleep(1)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                break

        movement()
        recv_msg = client.recv(1024).decode(ENCODING_FORMAT)
        total += 1
        try:
            recv_msg = recv_msg.split(MESSAGE_ENDING)[0].split(MESSAGE_START)[1].replace('[', "(").replace("]", ")")
            correct += 1
        except Exception as e:
            # print(recv_msg)
            wrong += 1

        print(f"[ RECEIVE ] {recv_msg}")
        print(wrong)
        print(correct)

        updated_data['position'] = (x, y)

        updated_data_json = MESSAGE_START + json.dumps(updated_data) + MESSAGE_ENDING

        try:
            print(str(round((wrong/total) * 100, 2)) + "%")
        except:
            print("0%")

        client.send(updated_data_json.encode(ENCODING_FORMAT))
        time.sleep(0.0)

    # TODO: Integrate pygame


# THREAD FUNCTIONS
def broadcasting_data(connection):
    # Global variables

    # Sleeping so that basic data has been exchanged
    time.sleep(0.1)
    # time.sleep(5)

    # Function
    while not stop_threads:
        if stop_threads:
            break

        try:
            connection.send_data(data_to_send)
        except Exception as e:
            log("error", "Unable to broadcast data!")
            log("exception", e)

        time.sleep(0.1)

        log("sending", data_to_send)
    log("info", "Broadcasting thread closing...\n")


def game_handler():
    # Global variables
    global start_game

    while not stop_threads:
        if stop_threads:
            break

        if start_game:
            go_to_game_starting_screen()

        if time_remaining <= 0:
            start_game = False


def handle_client(connection):
    # Global variables
    global stop_threads
    global joined_players
    global max_players
    global role
    global start_game
    global time_remaining
    global all_players

    # Sending starting data
    log("sending", "Sending starting data...")

    starting_data = {
        "username": username,
        "caught": is_caught
    }

    try:
        connection.send_data(starting_data)
    except Exception as e:
        log("error", "Unable to send starting data successfully!")
        log("exception", e)
    log("success", "Starting data has been sent!")

    # # Updating data_to_send
    # time.sleep(2)
    # log("info", "Updating data_to_send...")
    #
    # received_data = connection.receive_data()['player-data'][username]['starting-position']
    #
    # data_to_send['position'] = received_data
    #
    # log("success", "Data_to_send has been updated!")

    # Creating thread for broadcasting data
    time.sleep(0.25)
    log("info", "Starting broadcasting thread...")
    broadcast_data = threading.Thread(target=broadcasting_data, args=(client,))
    broadcast_data.start()
    log("success", "Broadcasting thread has been started!")

    # Function
    while not stop_threads:
        if stop_threads:
            break

        # Received message
        recv_msg = connection.receive_data()

        if recv_msg == "error":
            continue
        elif recv_msg == MESSAGE_DISCONNECTION_SERVER:
            stop_threads = False
            go_to_error_screen()
        # elif recv_msg == MESSAGE_DISCONNECTION_CLIENT:
        #     stop_threads = False
        #     go_to_disconnection_screen()
        else:
            try:
                max_players = recv_msg['max-players']
                joined_players = recv_msg['joined-players']
                role = recv_msg['player-data'][username]['role']
            except Exception as e:
                log('error', "Unable to set variables (line 460)")
                log("exception", e)

            try:
                if recv_msg['start-game']:
                    start_game = True
                    log("success", "START GAME")

                if recv_msg['time-remaining']:
                    time_remaining = recv_msg['time-remaining']
            except Exception as e:
                log("error", "Unable to set start game and time remaining variables!")
                log("exception", e)

            try:
                all_players = recv_msg['player-data']
            except Exception as e:
                log('error', "Unable to get data for all players! (line 480)")
                log("exception", e)

            data_to_send['caught'] = is_caught
            data_to_send['position'] = player_position

        log('receiv', recv_msg)

    log("info", "Broadcasting thread closing...\n")


# CLIENT/SERVER
def connect_to_server(ip: str, port: int, client_username: str):
    # Global variables
    global username
    global client
    global stop_threads

    # Setting stop threads to false to allow threads to function again
    stop_threads = False

    # Updating username
    if not client_username == "":
        log("info", "Updating username...")
        username = client_username
        log("success", "Username updated!")
    else:
        log("error", "Username field is empty!")

    # Setting up variables for ease of use
    if not ip == "":
        log("info", "Updating ip address of the server...")
        server_ip = ip
        log("success", "Successfully updated ip address!")
    else:
        log("error", "Unable to set ip address of the server!")
        log("info", "Using default ip address!")
        server_ip = "127.0.1.1"

    if not str(port) == "":
        if not int(port) <= 0:
            log("info", "Updating port of the server...")
            server_port = int(port)
            log("success", "Successfully updated port!")
        else:
            log("error", "Unable to set port of the server!")
            log("info", "Using default port address!")
            server_port = 5555
    else:
        log("error", "Unable to set port of the server!")
        log("info", "Using default port address!")
        server_port = 5555

    log("info", f"Attempting to connect to {server_ip}:{server_port} as {username}")

    # Displaying connecting screen
    go_to_connecting_screen()

    # Making client connection
    client = UserClient(username, server_ip, server_port, ENCODING_FORMAT)

    # Creating thread for receiving and updating data
    log("info", "Starting thread for handling/updating data from server...")
    handle_and_update_data = threading.Thread(target=handle_client, args=(client, ))
    handle_and_update_data.start()
    log("success", "Handling/updating data thread has been started!")

    # Displaying waiting queue screen
    # go_to_waiting_screen()


# NAVIGATORS
def go_to_connection_screen():
    global display_main_menu
    global display_connecting_screen
    global display_waiting_queue_screen
    global display_game
    global display_connection_screen
    global display_disconnection_screen
    global display_connection_failed_screen
    global display_error_screen
    global display_game_starting_screen

    # Disabling other screens
    display_main_menu = False
    display_connection_failed_screen = False
    display_waiting_queue_screen = False
    display_game_starting_screen = False
    display_game = False
    display_disconnection_screen = False
    display_error_screen = False
    display_connecting_screen = False

    # Hiding/showing widgets
    hide_buttons(buttons_main_menu_screen)
    hide_buttons(widgets_connection_failed_screen)
    hide_buttons(widgets_error_screen)
    hide_buttons(widgets_disconnection_screen)
    hide_buttons(widgets_waiting_queue_screen)

    show_buttons(widgets_connection_screen)

    # Displaying connecting screen
    display_connection_screen = True


def go_to_disconnection_screen():
    global display_main_menu
    global display_connecting_screen
    global display_waiting_queue_screen
    global display_game
    global display_connection_screen
    global display_disconnection_screen
    global display_connection_failed_screen
    global display_error_screen
    global display_game_starting_screen

    # Disabling other screens
    display_main_menu = False
    display_connection_failed_screen = False
    display_waiting_queue_screen = False
    display_game_starting_screen = False
    display_game = False
    display_error_screen = False
    display_connecting_screen = False
    display_connection_screen = False

    # Hiding/showing widgets
    hide_buttons(buttons_main_menu_screen)
    hide_buttons(widgets_connection_failed_screen)
    hide_buttons(widgets_error_screen)
    hide_buttons(widgets_connection_screen)
    hide_buttons(widgets_waiting_queue_screen)

    show_buttons(widgets_disconnection_screen)

    # Displaying connecting screen
    display_disconnection_screen = True


def go_to_error_screen():
    global display_main_menu
    global display_connecting_screen
    global display_waiting_queue_screen
    global display_game
    global display_connection_screen
    global display_disconnection_screen
    global display_connection_failed_screen
    global display_error_screen
    global display_game_starting_screen

    # Disabling other screens
    display_main_menu = False
    display_connection_failed_screen = False
    display_waiting_queue_screen = False
    display_game_starting_screen = False
    display_game = False
    display_disconnection_screen = False
    display_connecting_screen = False
    display_connection_screen = False

    # Hiding/showing widgets
    hide_buttons(buttons_main_menu_screen)
    hide_buttons(widgets_connection_failed_screen)
    hide_buttons(widgets_connection_screen)
    hide_buttons(widgets_disconnection_screen)
    hide_buttons(widgets_waiting_queue_screen)

    show_buttons(widgets_error_screen)

    # Displaying connecting screen
    display_error_screen = True


def go_to_waiting_screen():
    global display_main_menu
    global display_connecting_screen
    global display_waiting_queue_screen
    global display_game
    global display_connection_screen
    global display_disconnection_screen
    global display_connection_failed_screen
    global display_error_screen
    global display_game_starting_screen

    # Disabling other screens
    display_main_menu = False
    display_connection_failed_screen = False
    display_game_starting_screen = False
    display_game = False
    display_disconnection_screen = False
    display_connecting_screen = False
    display_connection_screen = False
    display_error_screen = False

    # Hiding/showing widgets
    hide_buttons(buttons_main_menu_screen)
    hide_buttons(widgets_connection_failed_screen)
    hide_buttons(widgets_connection_screen)
    hide_buttons(widgets_disconnection_screen)
    hide_buttons(widgets_error_screen)

    show_buttons(widgets_waiting_queue_screen)

    # Displaying connecting screen
    display_waiting_queue_screen = True


# def reset_initialization_variables():
#     # Global variables
#     global initialized_main_menu
#     global initialized_connection_screen
#     global initialized_connecting_screen
#     global initialized_disconnection_screen
#     global initialized_error_screen
#     global initialized_waiting_queue_screen
#     global initialized_connection_failed_screen
#
#     initialized_main_menu = False
#     initialized_connecting_screen = False
#     initialized_connection_screen = False
#     initialized_disconnection_screen = False
#     initialized_error_screen = False
#     initialized_connection_failed_screen = False
#     initialized_waiting_queue_screen = False


def go_to_connecting_screen():
    global display_main_menu
    global display_connecting_screen
    global display_waiting_queue_screen
    global display_game
    global display_connection_screen
    global display_disconnection_screen
    global display_connection_failed_screen
    global display_error_screen
    global display_game_starting_screen

    # Disabling other screens
    display_connection_screen = False
    display_main_menu = False
    display_connection_failed_screen = False
    display_waiting_queue_screen = False
    display_game_starting_screen = False
    display_game = False
    display_disconnection_screen = False
    display_error_screen = False

    # Hiding/showing widgets
    hide_buttons(widgets_connection_screen)
    hide_buttons(buttons_main_menu_screen)
    hide_buttons(widgets_connection_failed_screen)
    hide_buttons(widgets_error_screen)
    hide_buttons(widgets_disconnection_screen)
    hide_buttons(widgets_waiting_queue_screen)

    # Displaying connecting screen
    display_connecting_screen = True


def go_to_main_menu_screen():
    # Global variables for screen variables
    global display_main_menu
    global display_connecting_screen
    global display_connection_screen
    global display_waiting_queue_screen
    global display_game
    global display_disconnection_screen
    global display_connection_failed_screen
    global display_error_screen
    global display_game_starting_screen

    # Disabling other screens
    display_connecting_screen = False
    display_connection_failed_screen = False
    display_waiting_queue_screen = False
    display_game_starting_screen = False
    display_game = False
    display_disconnection_screen = False
    display_error_screen = False
    display_connection_screen = False

    # Disabling other screen buttons
    hide_buttons(widgets_connection_screen)
    hide_buttons(widgets_connection_failed_screen)
    hide_buttons(widgets_error_screen)
    hide_buttons(widgets_disconnection_screen)
    hide_buttons(widgets_waiting_queue_screen)

    show_buttons(buttons_main_menu_screen)

    # Displaying main menu screen
    display_main_menu = True


def go_to_connection_failed_screen():
    # Global variables for screen variables
    global display_main_menu
    global display_connecting_screen
    global display_connection_screen
    global display_waiting_queue_screen
    global display_game
    global display_disconnection_screen
    global display_connection_failed_screen
    global display_error_screen
    global display_game_starting_screen

    # Disabling other screens
    display_connecting_screen = False
    display_waiting_queue_screen = False
    display_game_starting_screen = False
    display_game = False
    display_disconnection_screen = False
    display_error_screen = False
    display_connection_screen = False
    display_main_menu = False

    # Disabling other screen buttons
    hide_buttons(widgets_connection_screen)
    hide_buttons(buttons_main_menu_screen)
    hide_buttons(widgets_error_screen)
    hide_buttons(widgets_disconnection_screen)
    hide_buttons(widgets_waiting_queue_screen)

    show_buttons(widgets_connection_failed_screen)

    # Displaying failed connection screen
    display_connection_failed_screen = True


def go_to_game_starting_screen():
    # Global variables for screen variables
    global display_main_menu
    global display_connecting_screen
    global display_connection_screen
    global display_waiting_queue_screen
    global display_game
    global display_disconnection_screen
    global display_connection_failed_screen
    global display_error_screen
    global display_game_starting_screen

    # Disabling other screens
    display_connecting_screen = False
    display_waiting_queue_screen = False
    display_game = False
    display_disconnection_screen = False
    display_error_screen = False
    display_connection_screen = False
    display_main_menu = False
    display_connection_failed_screen = False

    # Disabling other screen buttons
    hide_buttons(widgets_connection_screen)
    hide_buttons(buttons_main_menu_screen)
    hide_buttons(widgets_error_screen)
    hide_buttons(widgets_disconnection_screen)
    hide_buttons(widgets_waiting_queue_screen)
    hide_buttons(widgets_connection_failed_screen)

    # Displaying failed connection screen
    display_game_starting_screen = True


# UTILITIES
def exit_game():
    # Global variables
    global quit_game
    global stop_threads

    # Function
    quit_game = True

    if not stop_threads:
        stop_threads = True


def hide_buttons(buttons):
    for button, original_pos in buttons:
        button.setY(10000)


def show_buttons(buttons):
    for button, original_pos in buttons:
        button.setY(original_pos[1])


def disconnect_from_waiting_queue():
    # Global variables
    global stop_threads

    # TODO: Disconnect from server
    try:
        client.send_normal_data(MESSAGE_DISCONNECTION_CLIENT)
        client.close()
    except Exception as e:
        log("error", "Unable to disconnect from the server!")
        log("exception", e)

    # Stopping threads
    stop_threads = True

    go_to_disconnection_screen()

    print("DISCONNECT FROM WAITING QUEUE")


# DISPLAYS
def connection_screen():
    # Global variables
    global initialized_connection_screen

    # Removing buttons of main menu screen
    if not initialized_connection_screen:
        pass

    # Filling window with color
    window.fill(WINDOW_BACKGROUND_COLOR)

    # Function

    # Title text
    if not initialized_connection_screen:
        log("info", "Initializing connection screen...")

        global connection_screen_title_text
        connection_screen_title_text = font_big.render("Connect", 1, TEXT_COLOR)

    window.blit(connection_screen_title_text, (WINDOW_CENTER_X - connection_screen_title_text.get_width()/2, connection_screen_title_text.get_height()))

    # Making text boxes
    if not initialized_connection_screen:
        # Username
        global username_text
        username_text = font_small_big.render("Username", 1, TEXT_COLOR)

        global username_text_box_positions
        username_text_box_positions = (WINDOW_CENTER_X - TEXT_BOX_WIDTH/5, WINDOW_CENTER_Y - TEXT_BOX_HEIGHT * 5)
        username_text_box = TextBox(
            window,
            username_text_box_positions[0],
            username_text_box_positions[1],
            TEXT_BOX_WIDTH,
            TEXT_BOX_HEIGHT,
            fontSize=TEXT_BOX_FONT_SIZE,
            borderColour=TEXT_BOX_BORDER_COLOR,
            textColour=TEXT_COLOR,
            onSubmit=lambda: log("info", "Username text box updated!"),
            radius=TEXT_BOX_RADIUS,
            borderThickness=TEXT_BOX_BORDER_WIDTH,
            colour=TEXT_BOX_BACKGROUND_COLOR,
            placeholderText="Username"
        )

        widgets_connection_screen.append((username_text_box, username_text_box_positions))

        # IP Info
        global ip_address_text
        ip_address_text = font_small_big.render("IP", 1, TEXT_COLOR)

        global ip_text_box_positions
        ip_text_box_positions = (WINDOW_CENTER_X - TEXT_BOX_WIDTH / 5, WINDOW_CENTER_Y - TEXT_BOX_HEIGHT * 2)
        ip_text_box = TextBox(
            window,
            ip_text_box_positions[0],
            ip_text_box_positions[1],
            TEXT_BOX_WIDTH,
            TEXT_BOX_HEIGHT,
            fontSize=TEXT_BOX_FONT_SIZE,
            borderColour=TEXT_BOX_BORDER_COLOR,
            textColour=TEXT_COLOR,
            onSubmit=lambda: log("info", "IP text box updated!"),
            radius=TEXT_BOX_RADIUS,
            borderThickness=TEXT_BOX_BORDER_WIDTH,
            colour=TEXT_BOX_BACKGROUND_COLOR,
            placeholderText="IP Address"
        )

        widgets_connection_screen.append((ip_text_box, ip_text_box_positions))

        # Port
        global port_address_text
        port_address_text = font_small_big.render("Port", 1, TEXT_COLOR)

        global port_text_box_positions
        port_text_box_positions = (WINDOW_CENTER_X - TEXT_BOX_WIDTH / 5, WINDOW_CENTER_Y + TEXT_BOX_HEIGHT)
        port_text_box = TextBox(
            window,
            port_text_box_positions[0],
            port_text_box_positions[1],
            TEXT_BOX_WIDTH,
            TEXT_BOX_HEIGHT,
            fontSize=TEXT_BOX_FONT_SIZE,
            borderColour=TEXT_BOX_BORDER_COLOR,
            textColour=TEXT_COLOR,
            onSubmit=lambda: log("info", "Port text box updated!"),
            radius=TEXT_BOX_RADIUS,
            borderThickness=TEXT_BOX_BORDER_WIDTH,
            colour=TEXT_BOX_BACKGROUND_COLOR,
            placeholderText="Port"
        )

        widgets_connection_screen.append((port_text_box, port_text_box_positions))

    # Showing text along side of text boxes
    window.blit(username_text, (username_text_box_positions[0] - username_text.get_width() - 20, username_text_box_positions[1]))
    window.blit(ip_address_text, (ip_text_box_positions[0] - ip_address_text.get_width() - 20, ip_text_box_positions[1]))
    window.blit(port_address_text, (port_text_box_positions[0] - port_address_text.get_width() - 20, port_text_box_positions[1]))

    # Buttons
    if not initialized_connection_screen:
        # Attempt connection method
        connect_button_positions = (WINDOW_CENTER_X - BUTTON_WIDTH/2, port_text_box_positions[1] + BUTTON_HEIGHT * 2)

        connect_button = Button(
            window,
            connect_button_positions[0],
            connect_button_positions[1],
            BUTTON_WIDTH,
            BUTTON_HEIGHT,
            text='Connect!',
            fontSize=20,
            margin=20,
            inactiveColour=BUTTON_BACKGROUND_COLOR,
            hoverColour=BUTTON_HOVER_COLOR,
            pressedColour=BUTTON_CLICKED_COLOR,
            radius=10,
            onClick=lambda: connect_to_server(ip_text_box.getText(), port_text_box.getText(), username_text_box.getText())
        )

        widgets_connection_screen.append((connect_button, connect_button_positions))

        # Return to main menu button
        return_to_main_menu_button_positions = (connect_button_positions[0], connect_button_positions[1] + BUTTON_HEIGHT * 2)
        return_to_main_menu_button = Button(
            window,
            return_to_main_menu_button_positions[0],
            return_to_main_menu_button_positions[1],
            BUTTON_WIDTH,
            BUTTON_HEIGHT,
            text='Return!',
            fontSize=20,
            margin=20,
            inactiveColour=BUTTON_BACKGROUND_COLOR,
            hoverColour=BUTTON_HOVER_COLOR,
            pressedColour=BUTTON_CLICKED_COLOR,
            radius=10,
            onClick=go_to_main_menu_screen
        )

        widgets_connection_screen.append((return_to_main_menu_button, return_to_main_menu_button_positions))

        log("success", "Initialized connection screen!")

        initialized_connection_screen = True


def main_menu_screen():
    # Global variable
    global initialized_main_menu

    # Function
    window.fill(WINDOW_BACKGROUND_COLOR)

    # Making title
    if not initialized_main_menu:
        log("info", "Initializing main menu...")

        # Making title text global, so it can be accessed next execution
        global title_text
        title_text = font_gigantic.render(WINDOW_TITLE, 1, TEXT_COLOR)

    window.blit(title_text, (WINDOW_CENTER_X - title_text.get_width()/2, title_text.get_height()))

    # Buttons

    # Play button
    if not initialized_main_menu:
        play_button_positions = (WINDOW_CENTER_X - BUTTON_WIDTH / 2, WINDOW_CENTER_Y - BUTTON_HEIGHT)
        play_button = Button(
                window,
                play_button_positions[0],
                play_button_positions[1],
                BUTTON_WIDTH,
                BUTTON_HEIGHT,
                text='Play',
                fontSize=20,
                margin=20,
                inactiveColour=BUTTON_BACKGROUND_COLOR,
                hoverColour=BUTTON_HOVER_COLOR,
                pressedColour=BUTTON_CLICKED_COLOR,
                radius=10,
                onClick=go_to_connection_screen
        )

        buttons_main_menu_screen.append((play_button, play_button_positions))

        # Exit button
        exit_button_positions = (WINDOW_CENTER_X - BUTTON_WIDTH / 2, WINDOW_CENTER_Y + BUTTON_HEIGHT)
        exit_button = Button(
            window,
            exit_button_positions[0],
            exit_button_positions[1],
            BUTTON_WIDTH,
            BUTTON_HEIGHT,
            text='Exit',
            fontSize=20,
            margin=20,
            inactiveColour=BUTTON_BACKGROUND_COLOR,
            hoverColour=BUTTON_HOVER_COLOR,
            pressedColour=BUTTON_CLICKED_COLOR,
            radius=10,
            onClick=exit_game
        )

        buttons_main_menu_screen.append((exit_button, exit_button_positions))

        initialized_main_menu = True

        log("success", "Main menu initialized!")


def connecting_screen():
    # Global variables
    global connecting_screen_text_dot_index
    global initialized_connecting_screen

    # Other

    # TODO: Create thread for connecting and managing data from/to the server
    # TODO: Make thread stop if connection is not made

    # For testing purposes

    # if random.randint(0, 10000000000000000000000000) % 1130 == 0:
    #     go_to_connection_failed_screen()
    # elif random.randint(0, 10000000000000000000000000) % 2130 == 0:
    #     go_to_error_screen()
    # elif random.randint(0, 10000000000000000000000000) % 3130 == 0:
    #     go_to_disconnection_screen()
    # elif random.randint(0, 10000000000000000000000000) % 4130 == 0 or random.randint(0, 10000000000000000000000000) % 5130 == 0:
    #     go_to_waiting_screen()
    # elif random.randint(0, 10000) % 130 == 0 or random.randint(0, 10000000000000000000000000) % 5130 == 0:
    #     go_to_game_starting_screen()

    # Filling window with color
    window.fill(WINDOW_BACKGROUND_COLOR)

    # Connecting screen text
    if not initialized_connecting_screen:
        log("info", "Initializing connecting screen")

    if connecting_screen_text_dot_index >= len(connecting_screen_text_dots):
        connecting_screen_text_dot_index = 0

    connecting_text = font_big.render(f"Connecting{connecting_screen_text_dots[int(connecting_screen_text_dot_index)]}", 1, TEXT_COLOR)

    window.blit(connecting_text, (WINDOW_CENTER_X - connecting_text.get_width()/2, WINDOW_CENTER_Y - connecting_text.get_height()))

    connecting_screen_text_dot_index += 0.005

    if not initialized_connecting_screen:
        log("success", "Connecting screen initialized!")
        initialized_connecting_screen = True


def connection_failed_screen():
    # Global variables
    global initialized_connection_failed_screen

    # Other

    # Filling window with color
    window.fill(WINDOW_BACKGROUND_COLOR)

    if not initialized_connection_failed_screen:
        log("info", "Initializing failed screen...")

        global connection_failed_text
        connection_failed_text = font_big.render("Failed to connect!", 1, (255, 0, 0))

    # Displaying text
    window.blit(connection_failed_text, (WINDOW_CENTER_X - connection_failed_text.get_width()/2, WINDOW_CENTER_Y - connection_failed_text.get_height()/2))

    # Buttons
    if not initialized_connection_failed_screen:
        return_button_position = (WINDOW_CENTER_X - BUTTON_WIDTH/2, WINDOW_CENTER_Y + BUTTON_HEIGHT * 2)

        return_button = Button(
            window,
            return_button_position[0],
            return_button_position[1],
            BUTTON_WIDTH,
            BUTTON_HEIGHT,
            text='Return!',
            fontSize=20,
            margin=20,
            inactiveColour=BUTTON_BACKGROUND_COLOR,
            hoverColour=BUTTON_HOVER_COLOR,
            pressedColour=BUTTON_CLICKED_COLOR,
            radius=10,
            onClick=go_to_connection_screen
        )

        widgets_connection_failed_screen.append((return_button, return_button_position))

        log("success", "Initialized failure connecting screen!")
        initialized_connection_failed_screen = True


def waiting_queue_screen():
    # Global variables
    global waiting_queue_screen_text_dot_index
    global initialized_waiting_queue_screen

    # Functions

    # Filling window with color
    window.fill(WINDOW_BACKGROUND_COLOR)

    if not initialized_waiting_queue_screen:
        log("info", "Initializing waiting queue screen...")

    #  Waiting queue info text

    if waiting_queue_screen_text_dot_index >= len(waiting_queue_screen_text_dots):
        waiting_queue_screen_text_dot_index = 0

    waiting_queue_text = font_big.render(f"Waiting for match{waiting_queue_screen_text_dots[int(waiting_queue_screen_text_dot_index)]}", 1, TEXT_COLOR)
    window.blit(waiting_queue_text, (WINDOW_CENTER_X - waiting_queue_text.get_width()/2, WINDOW_CENTER_Y - waiting_queue_text.get_height()/2))

    waiting_queue_screen_text_dot_index += 0.005

    # Players Joined text
    players_text = font_normal.render(f"Players: {joined_players}/{max_players}", 1, TEXT_COLOR)
    window.blit(players_text, (WINDOW_CENTER_X - players_text.get_width()/2, WINDOW_CENTER_Y - players_text.get_height() * 4))

    # Disconnect Button
    if not initialized_waiting_queue_screen:
        disconnect_button_positions = (WINDOW_CENTER_X - BUTTON_WIDTH/2, WINDOW_CENTER_Y + BUTTON_HEIGHT * 2)
        disconnect_button = Button(
            window,
            disconnect_button_positions[0],
            disconnect_button_positions[1],
            BUTTON_WIDTH,
            BUTTON_HEIGHT,
            text='Disconnect',
            fontSize=20,
            margin=20,
            inactiveColour=BUTTON_BACKGROUND_COLOR,
            hoverColour=BUTTON_HOVER_COLOR,
            pressedColour=BUTTON_CLICKED_COLOR,
            radius=10,
            onClick=disconnect_from_waiting_queue
        )

        widgets_waiting_queue_screen.append((disconnect_button, disconnect_button_positions))

        log("success", "Successfully initialized waiting queue screen!")

        initialized_waiting_queue_screen = True

    if start_game:
        go_to_game_starting_screen()


def game_screen():
    # Global variables
    global initialized_game_onetime_data
    global player_position
    global time_to_allow_catching

    # Local variables

    # Other

    # Filling window with color
    window.fill(WINDOW_IN_GAME_BACKGROUND_COLOR)

    if not initialized_game_onetime_data:
        try:
            log("info", "Initializing one time game data...")
            role_text = font_big.render(f"You are {role}", 1, TEXT_COLOR_IN_GAME)
            window.blit(role_text, (WINDOW_CENTER_X - role_text.get_width() / 2, WINDOW_CENTER_Y - role_text.get_height() / 2))

            pygame.display.update()

            time.sleep(time_to_display_role)
            log("success", "One time game data has been initialized!")

            initialized_game_onetime_data = True

            # TODO: Display players in starting positions
            player_data = all_players[username]

            global player
            player = Player(role, player_data['starting-position'], player_data['color'], (WINDOW_WIDTH, WINDOW_HEIGHT), username, True)

            log("success", "Player has been declared!")

            log("info", "Making global catchers and runners variables")
            # Making catchers
            global catchers
            catchers = []

            # Making runners
            global runners

            runners = []

            try:
                if player_data['role'].lower() == "catcher":
                    catchers.append(player)
                    log("info", "Adding player to catchers...")
                elif player_data['role'].lower() == "runner":
                    runners.append(player)
                    log("info", "Adding player to runners...")
            except Exception as e:
                log("error", "Unable to set player class!")
                log('exception', e)
            # Adding players to their respective categories

            for p in all_players:
                p_d = all_players[p]

                if p_d['role'].lower() == "runner" and not p == username:
                    runner = Player(p_d['role'], p_d['starting-position'], p_d['color'], (WINDOW_WIDTH, WINDOW_HEIGHT), p, False)
                    runners.append(runner)
                elif p_d['role'].lower() == "catcher" and not p == username:
                    catcher = Player(p_d['role'], p_d['starting-position'], p_d['color'], (WINDOW_WIDTH, WINDOW_HEIGHT),
                                    p, False)
                    catchers.append(catcher)
        except Exception as e:
            log("error", "Unable to declare player variables!")
            log("exception", e)

        player_position = (all_players[username]['starting-position'][0], all_players[username]['starting-position'][0])

        for runner in runners:
            runner.rect.x = all_players[runner.username]['starting-position'][0]
            runner.rect.y = all_players[runner.username]['starting-position'][1]

        for catcher in catchers:
            catcher.rect.x = all_players[catcher.username]['starting-position'][0]
            catcher.rect.y = all_players[catcher.username]['starting-position'][1]
        # global runners
        # runners = []
        # #
        # # global catcher
        # #
        # # if player.role == "catcher":
        # #     catcher = player
        # #
        # for player in all_players.keys():
        #     if all_players[player]['role'].lower() == "runner":
        #         runner = Player(all_players[player]['role'], all_players[player]['starting-position'], all_players[player]['color'], (WINDOW_WIDTH, WINDOW_HEIGHT), player, False)
        #         runners.append(runner)
        #     elif all_players[player]['role'].lower() == "catcher":
        #         catcher = Player(all_players[player]['role'], all_players[player]['starting-position'], all_players[player]['color'], (WINDOW_WIDTH, WINDOW_HEIGHT), player, False)

        for catcher in catchers:
            try:
                all_players[catcher.username]['position'][0] = all_players[catcher.username]['starting-position'][0]
                all_players[catcher.username]['position'][1] = all_players[catcher.username]['starting-position'][1]

                # if not catcher.rect.x == new_pos_x:
                catcher.rect.x = all_players[catcher.username]['position'][0]

                # if not catcher.rect.y == new_pos_y:
                catcher.rect.y = all_players[catcher.username]['position'][1]
            except Exception as e:
                log("error", f'Unable to update position for {catcher.username}!')
                log("exception", e)

            catcher.update(window)

        for runner in runners:
            try:
                all_players[runner.username]['position'][0] = all_players[runner.username]['starting-position'][0]
                all_players[runner.username]['position'][1] = all_players[runner.username]['starting-position'][1]

                # if not runner.rect.x == new_pos_x:
                runner.rect.x = all_players[runner.username]['position'][0]

                # if not runner.rect.y == new_pos_y:
                runner.rect.y = all_players[runner.username]['position'][1]
            except Exception as e:
                log("error", f"Unable to update position of {runner.username}!")
                log("exception", e)

            runner.update(window)

        pygame.display.update()

    # TODO: Update players' positions
    # player.update(window)
    #
    # player_position = (player.rect.x, player.rect.y)
    for catcher in catchers:
        try:
            new_pos_x = all_players[catcher.username]['position'][0]
            new_pos_y = all_players[catcher.username]['position'][1]

            if not catcher.rect.x == new_pos_x:
                catcher.rect.x = all_players[catcher.username]['position'][0]

            if not catcher.rect.y == new_pos_y:
                catcher.rect.y = all_players[catcher.username]['position'][1]
        except Exception as e:
            log("error", f'Unable to update position for {catcher.username}!')
            log("exception", e)

        catcher.update(window)

    for runner in runners:
        try:
            new_pos_x = all_players[runner.username]['position'][0]
            new_pos_y = all_players[runner.username]['position'][1]

            if not runner.rect.x == new_pos_x:
                runner.rect.x = all_players[runner.username]['position'][0]

            if not runner.rect.y == new_pos_y:
                runner.rect.y = all_players[runner.username]['position'][1]
        except Exception as e:
            log("error", f"Unable to update position of {runner.username}!")
            log("exception", e)

        runner.update(window)

        for catcher in catchers:
            if not time_to_allow_catching > 0:
                runner.handle_catcher_collisions(catcher)
                log("success", "+++++==========================+++++++++++++++++++++++++++++======================+++++++++=")
            else:
                time_to_allow_catching -= 0.05
                log("info", "***************************************88")

    # TODO: SEND Updated positions
    player_position = (player.rect.x, player.rect.y)

    # if not start_game:
    #     runners = []
    #     catchers = []
    #     initialized_game_onetime_data = False
    #     log("info", "Exiting game screen and going back to main menu screen...")
    #     disconnect_from_waiting_queue()
    #     go_to_main_menu_screen()


def game_starting_screen():
    # Global variables
    global time_to_start_game
    global display_game
    global display_game_starting_screen

    # Function

    # Filling window with color
    window.fill(WINDOW_IN_GAME_BACKGROUND_COLOR)

    # Timer Text
    timer_text = font_big.render(str(int(time_to_start_game)), 1, TEXT_COLOR_IN_GAME)
    window.blit(timer_text, (WINDOW_CENTER_X - timer_text.get_width()/2, WINDOW_CENTER_Y - timer_text.get_height()/2))

    pygame.display.update()

    # TIMER
    if time_to_start_game <= 0:
        log("info", "Starting game")

        log("info", "Going to game screen...")

        display_game = True
        display_game_starting_screen = False
    else:
        time.sleep(0.1)
        time_to_start_game -= 0.1


def error_screen():
    # Global variables
    global initialized_error_screen

    # Other

    # Filling window with color
    window.fill(WINDOW_BACKGROUND_COLOR)

    if not initialized_error_screen:
        log("info", "Initializing error screen...")

        global error_text
        error_text = font_big.render("An error occurred!", 1, (255, 0, 0))

    # Displaying text
    window.blit(error_text, (WINDOW_CENTER_X - error_text.get_width() / 2,
                                         WINDOW_CENTER_Y - error_text.get_height() / 2))

    # Buttons
    if not initialized_error_screen:
        return_button_position = (WINDOW_CENTER_X - BUTTON_WIDTH / 2, WINDOW_CENTER_Y + BUTTON_HEIGHT * 2)

        return_button = Button(
            window,
            return_button_position[0],
            return_button_position[1],
            BUTTON_WIDTH,
            BUTTON_HEIGHT,
            text='Return!',
            fontSize=20,
            margin=20,
            inactiveColour=BUTTON_BACKGROUND_COLOR,
            hoverColour=BUTTON_HOVER_COLOR,
            pressedColour=BUTTON_CLICKED_COLOR,
            radius=10,
            onClick=go_to_main_menu_screen
        )

        widgets_error_screen.append((return_button, return_button_position))

        log("success", "Initialized error screen!")
        initialized_error_screen = True


def disconnection_screen():
    # Global variables
    global initialized_disconnection_screen

    # Other

    # Filling window with color
    window.fill(WINDOW_BACKGROUND_COLOR)

    if not initialized_disconnection_screen:
        log("info", "Initializing disconnection screen...")

        global disconnection_text
        disconnection_text = font_big.render("Disconnected!", 1, (255, 0, 0))

    # Displaying text
    window.blit(disconnection_text, (WINDOW_CENTER_X - disconnection_text.get_width() / 2,
                             WINDOW_CENTER_Y - disconnection_text.get_height() / 2))

    # Buttons
    if not initialized_disconnection_screen:
        return_button_position = (WINDOW_CENTER_X - BUTTON_WIDTH / 2, WINDOW_CENTER_Y + BUTTON_HEIGHT * 2)

        return_button = Button(
            window,
            return_button_position[0],
            return_button_position[1],
            BUTTON_WIDTH,
            BUTTON_HEIGHT,
            text='Return!',
            fontSize=20,
            margin=20,
            inactiveColour=BUTTON_BACKGROUND_COLOR,
            hoverColour=BUTTON_HOVER_COLOR,
            pressedColour=BUTTON_CLICKED_COLOR,
            radius=10,
            onClick=go_to_main_menu_screen
        )

        widgets_disconnection_screen.append((return_button, return_button_position))

        log("success", "Initialized disconnection screen!")
        initialized_disconnection_screen = True


# MAIN FUNCTION
def run():
    # Global variables
    global quit_game

    # Local variables
    clock = pygame.time.Clock()

    # Function

    log("info", "Making pygame screens...")

    while not quit_game:
        clock.tick(WINDOW_FPS)

        events = pygame.event.get()

        for event in events:
            if event.type == pygame.QUIT:
                quit_game = True

        if display_main_menu:
            main_menu_screen()
        elif display_connection_screen:
            connection_screen()
        elif display_connecting_screen:
            connecting_screen()
        elif display_connection_failed_screen:
            connection_failed_screen()
        elif display_waiting_queue_screen:
            waiting_queue_screen()
        elif display_game:
            game_screen()
        elif display_game_starting_screen:
            game_starting_screen()
        elif display_error_screen:
            error_screen()
        elif display_disconnection_screen:
            disconnection_screen()

        # Updating the pygame widgets
        pygame_widgets.update(events)

        # Updating pygame display
        pygame.display.update()


log("success", "All functions have been defined!")

# Other
if __name__ == '__main__':
    log("info", "Running script...")
    run()
