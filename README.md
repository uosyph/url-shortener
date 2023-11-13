<a name="readme-top"></a>

# Shorten

In a world cluttered with lengthy and cumbersome URLs, a lone developer,
driven by the frustration of sharing convoluted web addresses,
embarked on a quest to simplify the digital landscape.
This is the tale of "Shorten," a URL shortener born out of necessity.

[Try it here](http://54.236.51.83/)

## Table of Contents

- [Features](#features)
- [Screenshots](#screenshots)
- [Installation](#installation)
- [Environment Configuration](#environment-configuration)
- [Contributing](#contributing)
- [License](#license)
- [Author](#author)

## Features

Shorten isn't just a mere URL shortener;
it's a comprehensive solution tailored for both casual users and those seeking advanced functionality.
Let's delve into its features:

### User Management
Users can create accounts, log in, and generate tokens for API access,
unlocking a realm of possibilities like creating permanent or time-limited short URLs.

### Limited Functionality for Non-Logged-In Users
Even without an account, users can still benefit from URL shortening, but with a 7-day lifespan for their links.

### Dashboard and Analytics
Logged-in users are treated to a personalized dashboard, providing insights into URL analytics,
click-through rates, and referral sources.

### API Integration
Shorten goes beyond the browser with a robust API, allowing programmatic URL management.
Tokens obtained by users enable secure API operations.

### URL Management
Fine-tune control with the ability to delete URLs or adjust their expiration date.

### QR Code Generation
Simplify sharing further with QR codes generated effortlessly for shortened URLs.

### User Interface
An aesthetically pleasing index page, a feature-rich dashboard,
and a custom 404 page showcase Shorten's commitment to a seamless user experience.

In summary, the URL Shortener project provides a comprehensive solution for shortening, managing,
and tracking URLs, with features to suit both logged-in and non-logged-in users.

## Screenshots

### Shortener
![Shortener Page Preview](/screenshots/shortener.png)

### Dashboard
![Dashboard Page Preview](/screenshots/dashboard.png)

### Account
![Account Page Preview](/screenshots/account.png)

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

In this repository, you will find a file named `.env`.
This file contains sensitive configuration information and is typically not included in version control systems.
However, I've included it here for your convenience to help you get started quickly without having to create it yourself.

## Contributing

### Development

To fix a bug or enhance an existing feature, follow these steps:

- Fork the repo
- Create a new branch (`git checkout -b improve-feature`)
- Make the necessary changes
- Add changes to reflect updates
- Commit your changes (`git commit -am 'Improve feature'`)
- Push to the branch (`git push origin improve-feature`)
- Create a Pull Request

### Bug/Feature Request

If you find a bug or want to request a new feature:

- For bugs, open an issue with details about the problem.
- For feature requests, open an issue with your suggestions.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Author

**Yousef Saeed**:
[GitHub](https://github.com/yousafesaeed)
[LinkedIn](https://linkedin.com/in/yousafesaeed)
[X](https://twitter.com/yousafesaeed)

<p align="right"><a href="#readme-top">Back to Top</a></p>
