# UNIT3D Live Chat Monitor

![REQUIRED](https://img.shields.io/badge/REQUIRED-UNIT3D-blue)
[![Python Version](https://img.shields.io/badge/Python-3.x-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

<p align="center">
  <img src="https://ptpimg.me/c68lfx.png" alt="Chat Monitor Logo" style="width: 100%;">
</p>

_Automated Python live chat monitor with terminal UI for UNIT3D._

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Environment Variables](#environment-variables)
- [Configuration](#configuration)
- [Usage](#usage)
- [Troubleshooting](#troubleshooting)
- [Acknowledgements](#acknowledgements)
- [License](#license)

---

## Overview

This repository provides an automated Python live chat monitor with a terminal-based UI designed specifically for UNIT3D. It leverages Selenium WebDriver for web automation, BeautifulSoup for HTML parsing, and curses for an interactive command-line interface.

---

## Features

- **Real-Time Chat Monitoring:** Utilizes a JavaScript MutationObserver to detect and process new chat messages instantly.
- **Interactive Terminal UI:** Built with the curses library, offering a color-coded and user-friendly interface.
- **Web Automation:** Automates login and chat interactions through Selenium in headless mode.
- **Thread-Safe Messaging:** Processes messages using a thread-safe queue for reliable performance.

---

## Prerequisites

- [Python 3.7 or higher](https://www.python.org/)
- [Selenium](https://www.selenium.dev/)
- [BeautifulSoup4](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)
- [webdriver-manager](https://github.com/SergeyPirogov/webdriver_manager)
- [Colorama](https://pypi.org/project/colorama/)
- [Curses](https://docs.python.org/3/library/curses.html) or [windows-curses](https://pypi.org/project/windows-curses/)

Install the required packages with:

```bash
pip install -r requirements.txt
```

---

## Installation

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/rkeaves/unit3d-terminal-chat.git
   ```

2. **Set Up a Virtual Environment (Optional but Recommended):**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

---

## Environment Variables

For enhanced security and ease of configuration, store sensitive settings in a `.env` file rather than hardcoding them. This file should be located in the project's root directory.

1. **Create a `.env` file** with the following content:

   ```env
   TRACKER_URL=https://your-unit3d-instance.example.com
   TRACKER_USERNAME=YOUR_USERNAME
   TRACKER_PASSWORD=YOUR_PASSWORD
   ```

2. **Install `python-dotenv`:**

   ```bash
   pip install python-dotenv
   ```

3. **Update the code** to load these variables by adding the following lines at the beginning of your script:

   ```python
   from dotenv import load_dotenv
   load_dotenv()  # Loads the variables from the .env file into os.environ

   TRACKER_URL = os.getenv("TRACKER_URL", "https://privatesilverscreen.cc")
   TRACKER_USERNAME = os.getenv("TRACKER_USERNAME", "USERNAME HERE")
   TRACKER_PASSWORD = os.getenv("TRACKER_PASSWORD", "PASSWORD HERE")
   ```

> **Note:** Add the `.env` file to your `.gitignore` to prevent sensitive data from being exposed in public repositories.

---

## Configuration

Before running the application, update the configuration parameters either directly in the code or via the `.env` file as shown above:

- **TRACKER_URL:** Set this to the URL of your UNIT3D instance.
- **TRACKER_USERNAME & TRACKER_PASSWORD:** Provide your tracker login credentials.
- **Debug Mode:** Launch the script with the `--debug` flag to enable verbose logging.

```bash
TRACKER_URL = "https://your-unit3d-instance.example.com"
TRACKER_USERNAME = "YOUR_USERNAME"
TRACKER_PASSWORD = "YOUR_PASSWORD"
```

> **Note:** Keep these sensitive values secure and avoid exposing them in public repositories.

---

## Usage

Run the application using:

```bash
python chat.py
```

The application will automatically:
- Log in to your UNIT3D chat page.
- Monitor live chat messages in real time.
- Display messages in a terminal-based UI with color-coded formatting.

Type your message into the interface and press **Enter** to send.

---

## Troubleshooting

- **Curses Module Error on Windows:**  
  If you encounter an error regarding the curses module, install `windows-curses`:

  ```bash
  pip install windows-curses
  ```
  
> **Note:** *Debug Mode:* Launch the script with the `--debug` flag to enable verbose logging.

- **WebDriver Issues:**  
  Verify that Microsoft Edge WebDriver is installed correctly and matches your browser version.

- **Login Failures:**  
  Double-check the credentials and URL specified in the configuration section.

Review the terminal log output for further troubleshooting information.

---

## Acknowledgements

This project builds upon various open-source libraries including Selenium, BeautifulSoup, and Colorama. Special thanks to the UNIT3D community for their continuous support and inspiration.

---

## License

This project is licensed under the MIT License.
