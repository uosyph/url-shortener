# Shorten

A URL shortener aims to solve the problem of long and cumbersome URLs by providing a simple and convenient way to shorten and manage URLs.

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Environment Configuration](#environment-configuration)
- [License](#license)
- [Author](#author)

## Features

It includes the following features:

- **User management**: Users can create accounts, log in, and generate tokens to be used in the API. This allows them to access additional functionality, such as creating permanent or time-limited short URLs.
- **Dashboard and analytics**: Logged-in users have access to a personalized dashboard where they can view analytics for their URLs and manage their shortened URLs, including click-through rates and referral sources.
- **QR code generation**: Users can generate QR codes for their shortened URLs for easy sharing.
- **URL Management**: Logged-in users can manage their URLs by deleting them or changing their expiration date if they no longer wish to keep them active or want to extend their lifespan.
- **Limited functionality for non-logged-in users**: Non-logged-in users can still use the URL shortening service, but their shortened URLs have a lifespan of 7 days before being automatically deleted.
- **User interface**: The service has a visually appealing index page and a dashboard page for logged-in users to manage their URLs and view analytics. A custom 404 page is also implemented to handle invalid URLs.
- **API**: The project also includes an API that allows users to send requests and receive responses programmatically, enabling integration with other applications and services. Tokens generated in the "User management" section will be used in many of the API operations.

In summary, the URL Shortener project provides a comprehensive solution for shortening, managing, and tracking URLs, with features to suit both logged-in and non-logged-in users. Users can also generate tokens for API access, and these tokens will play a significant role in various API operations.

## Installation

**Clone the Repository:**

```sh
git clone https://github.com/yousafesaeed/url-shortener.git && cd url-shortener
```

**Install the Required Libraries:**

```sh
pip install -r requirements.txt
```

**Build the Database:**

```sh
python database.py
```

**Run the App:**

```sh
python app.py
```

## Environment Configuration

In this repository, you will find a file named `.env`. This file contains sensitive configuration information and is typically not included in version control systems. However, I've included it here for your convenience to help you get started quickly without having to create it yourself.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Author

**Yousef Saeed**
