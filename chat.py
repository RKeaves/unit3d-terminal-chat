import os
import sys
import time
import logging
import threading
import queue
import curses
import re
from datetime import datetime
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from selenium.common.exceptions import TimeoutException, WebDriverException
from colorama import init as colorama_init, Fore, Style
from dotenv import load_dotenv

# /*==================================================================================!/*
# !/* - Project: unit3d-terminal-chat                                                 !/*
# !/* - Repository: https://github.com/RKeaves/unit3d-terminal-chat                   !/*
# !/* - Description: Automated python live chat monitor with terminal UI for unit3d.  !/*
# !/* - Version: 1.0.0                                                                !/*
# !/* - Author: RKeaves                                                               !/*
# !/* - Author URL: https://github.com/rkeaves                                        !/*
# !/* - License: MIT                                                                  !/*
# !/* - Contributions & Feedback:                                                     !/*
# !/* - Feel free to suggest improvements, submit commits, or report issues on GitHub !/*
# !/* - https://github.com/RKeaves/rkeaves.github.io/blob/main/css-theme/cyber.css    !/*
# !/*==================================================================================/*

# Initialize Colorama for logging and non-curses output.
colorama_init(autoreset=True)

# Load environment variables from the .env file
load_dotenv()

# ---------------------
# Configuration
# ---------------------
TRACKER_URL = os.getenv("TRACKER_URL")
TRACKER_USERNAME = os.getenv("TRACKER_USERNAME")
TRACKER_PASSWORD = os.getenv("TRACKER_PASSWORD")

DEBUG_MODE = "--debug" in sys.argv
LOG_LEVEL = logging.DEBUG if DEBUG_MODE else logging.INFO
logging.basicConfig(level=LOG_LEVEL,
                    format="%(asctime)s [%(levelname)s] %(message)s",
                    datefmt="%H:%M:%S")
logging.getLogger("urllib3.connectionpool").setLevel(logging.ERROR)

# A thread-safe queue for chat messages.
# Each entry is a tuple: (display_time, username, content)
chat_queue = queue.Queue()

# ---------------------
# BBCode Parsing Helper
# ---------------------
def convert_color(hex_code: str) -> str:
    """
    Map a few hex colors to plain text placeholders.
    (Not used in curses mode.)
    """
    hex_to_color = {
        "#ff0000": "RED",
        "#00ff00": "GREEN",
        "#0000ff": "BLUE",
        "#ffff00": "YELLOW",
        "#888888": "GRAY",
        "#8888": "GRAY"  # Fallback for shorthand.
    }
    return hex_to_color.get(hex_code.lower(), "")

def parse_bbcode(text: str) -> str:
    """
    Converts a subset of BBCode to plain text modifications.
    In curses mode, we simulate formatting by, for example, uppercasing bold text
    and wrapping italic text in underscores.
    """
    # Bold: [b]text[/b] -> simulate by uppercasing.
    text = re.sub(r'\[b\](.*?)\[/b\]', lambda m: m.group(1).upper(), text, flags=re.DOTALL)
    # Italic: [i]text[/i] -> simulate with underscores.
    text = re.sub(r'\[i\](.*?)\[/i\]', lambda m: "_" + m.group(1) + "_", text, flags=re.DOTALL)
    # Color: [color=...]text[/color] -> remove color tags.
    text = re.sub(r'\[color=([^]]+)\](.*?)\[/color\]', lambda m: m.group(2), text, flags=re.DOTALL)
    return text


# ---------------------
# Chat Monitor Class
# ---------------------
class ChatMonitor:
    def __init__(self, driver, message_queue):
        self.driver = driver
        self.seen_messages = set()
        self.queue = message_queue
        self.init_observer()

    def init_observer(self):
        """
        Inject a MutationObserver into the page to monitor the chat container.
        """
        script = """
        if (!window.newMessages) {
            window.newMessages = [];
            var chatContainer = document.querySelector('ul.chatroom__messages');
            if (chatContainer) {
                var observer = new MutationObserver(function(mutations) {
                    mutations.forEach(function(mutation) {
                        mutation.addedNodes.forEach(function(node) {
                            if (node.nodeType === Node.ELEMENT_NODE && node.matches('li')) {
                                window.newMessages.push(node.outerHTML);
                            }
                        });
                    });
                });
                observer.observe(chatContainer, { childList: true });
            }
        }
        """
        self.driver.execute_script(script)

    def process_messages(self):
        """
        Retrieve new messages from the browser, parse them, and queue their components.
        """
        try:
            new_msgs_html = self.driver.execute_script("var msgs = window.newMessages; window.newMessages = []; return msgs;")
            for msg_html in new_msgs_html:
                soup = BeautifulSoup(msg_html, 'html.parser')
                username_elem = soup.select_one("header address a span")
                username = username_elem.get_text(strip=True) if username_elem else ""
                time_elem = soup.select_one("header time")
                if time_elem and time_elem.has_attr("title"):
                    timestamp = time_elem["title"].strip()
                    try:
                        dt = datetime.fromisoformat(timestamp)
                        display_time = dt.strftime("%H:%M:%S")
                    except Exception:
                        display_time = timestamp
                else:
                    display_time = "Unknown time"
                content_elem = soup.select_one("section.chatbox-message__content")
                content = content_elem.get_text(strip=True) if content_elem else ""
                if not content:
                    continue
                unique_key = f"{display_time}-{content}"
                if unique_key in self.seen_messages:
                    continue
                self.seen_messages.add(unique_key)
                processed_content = parse_bbcode(content)
                self.queue.put((display_time, username, processed_content))
        except Exception as e:
            logging.error(Fore.RED + f"Error processing messages: {e}")

    def monitor_live(self):
        """
        Continuously poll for new messages.
        """
        logging.info(Fore.GREEN + "Starting live chat feed. (Press Ctrl+C to exit.)")
        try:
            while True:
                self.process_messages()
                time.sleep(0.05)
        except Exception as e:
            logging.error(Fore.RED + f"Unexpected error in monitor_live: {e}")
        finally:
            try:
                self.driver.quit()
                logging.info(Fore.BLUE + "WebDriver closed.")
            except Exception as e:
                logging.error(Fore.RED + f"Error closing WebDriver: {e}")

# ---------------------
# Message Sending Function
# ---------------------
def send_message(driver, message):
    """
    Locate the chat input field and send the provided message.
    """
    try:
        chat_input = driver.find_element(By.CSS_SELECTOR, "textarea#chatbox__messages-create")
        chat_input.clear()
        chat_input.send_keys(message)
        chat_input.send_keys(Keys.ENTER)
        logging.info(Fore.GREEN + f"Sent message: {message}")
    except Exception as e:
        logging.error(Fore.RED + f"Error sending message: {e}")

# ---------------------
# WebDriver Login Function
# ---------------------
def login_and_get_driver():
    """
    Logs into the site and returns an authenticated WebDriver instance.
    """
    try:
        logging.debug("Setting up Edge WebDriver in headless mode.")
        edge_options = EdgeOptions()
        edge_options.add_argument("--headless")
        edge_options.add_argument("--disable-gpu")
        edge_options.add_argument("--window-size=1920,1080")
        driver = webdriver.Edge(
            service=EdgeService(EdgeChromiumDriverManager().install()),
            options=edge_options
        )
        logging.info(Fore.GREEN + "Edge WebDriver set up in headless mode.")

        login_url = f"{TRACKER_URL}/login"
        logging.info(Fore.CYAN + f"Navigating to login page: {login_url}")
        driver.get(login_url)

        WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.ID, "username")))
        driver.find_element(By.ID, "username").send_keys(TRACKER_USERNAME)
        logging.info(Fore.BLUE + "Entered username.")

        WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.ID, "password")))
        driver.find_element(By.ID, "password").send_keys(TRACKER_PASSWORD)
        logging.info(Fore.BLUE + "Entered password.")

        login_button = driver.find_element(By.XPATH, '//button[contains(text(), "Login")]')
        logging.info(Fore.BLUE + "Clicking login button.")
        login_button.click()

        WebDriverWait(driver, 20).until(lambda d: d.current_url != login_url)
        logging.info(Fore.GREEN + f"Login successful, current URL: {driver.current_url}")

        WebDriverWait(driver, 60).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "ul.chatroom__messages"))
        )
        logging.info(Fore.GREEN + "Chat messages container loaded.")
        return driver
    except Exception as e:
        logging.error(Fore.RED + f"Login failed: {e}")
        driver.quit()
        raise

# ---------------------
# Curses Main Function
# ---------------------
def curses_main(stdscr):
    # Initialize curses and enable color support.
    curses.curs_set(1)
    curses.start_color()
    curses.use_default_colors()
    # Initialize color pairs:
    # Pair 1: for usernames (cyan)
    # Pair 2: for timestamps (white, dimmed to simulate gray)
    curses.init_pair(1, curses.COLOR_CYAN, -1)
    curses.init_pair(2, curses.COLOR_WHITE, -1)
    
    stdscr.nodelay(True)
    stdscr.clear()
    height, width = stdscr.getmaxyx()
    chat_height = height - 3

    chat_win = curses.newwin(chat_height, width, 0, 0)
    chat_win.scrollok(True)
    chat_win.idlok(True)
    input_win = curses.newwin(3, width, chat_height, 0)
    input_win.nodelay(True)
    input_buffer = ""

    driver = login_and_get_driver()
    monitor = ChatMonitor(driver, chat_queue)
    monitor_thread = threading.Thread(target=monitor.monitor_live, daemon=True)
    monitor_thread.start()

    while True:
        # Update the input window.
        input_win.clear()
        input_win.addstr(0, 0, "Type your message (Enter to send):")
        input_win.addstr(1, 0, input_buffer)
        input_win.refresh()

        # Handle keyboard input.
        try:
            ch = input_win.getch()
            if ch != -1:
                if ch in (curses.KEY_ENTER, 10, 13):
                    if input_buffer.strip():
                        send_message(driver, input_buffer)
                        input_buffer = ""
                elif ch in (curses.KEY_BACKSPACE, 127):
                    input_buffer = input_buffer[:-1]
                elif 0 <= ch <= 255:
                    input_buffer += chr(ch)
        except Exception:
            pass

        # Display new chat messages.
        try:
            while True:
                display_time, username, content = chat_queue.get_nowait()
                # Build the full timestamp string (including brackets) and display it in dim white.
                timestamp_str = f"[ {display_time} ]"
                chat_win.addstr(timestamp_str, curses.color_pair(2) | curses.A_DIM)
                # Build the username string (including parentheses) and display it in cyan.
                username_str = f" ( {username} )"
                chat_win.addstr(username_str, curses.color_pair(1))
                # Add separator and the message content.
                chat_win.addstr(" : ", curses.A_NORMAL)
                chat_win.addstr(content + "\n", curses.A_NORMAL)
                chat_win.refresh()
        except queue.Empty:
            pass

        time.sleep(0.05)

# ---------------------
# Main Function
# ---------------------
def main():
    try:
        curses.wrapper(curses_main)
    except KeyboardInterrupt:
        logging.info(Fore.RED + "Exiting chat application.")
    except Exception as e:
        logging.error(Fore.RED + f"An error occurred: {e}")

if __name__ == "__main__":
    main()
