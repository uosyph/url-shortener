<a name="readme-top"></a>

# Shorten

In a world cluttered with lengthy and cumbersome URLs, a lone developer,
driven by the frustration of sharing convoluted web addresses,
embarked on a quest to simplify the digital landscape.
This is the tale of "Shorten," a URL shortener born out of necessity.

## Table of Contents

- [Features](#features)
- [Screenshots](#screenshots)
- [API Usage](#api-usage)
- [Environment Configuration](#environment-configuration)
- [Local Development](#local-development)
- [Production Deployment](#production-deployment)
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

## API Usage

### Authentication

All API endpoints require authentication using JWT tokens.
Include the token in the header of your requests as follows:

```
Header: x-access-token: YOUR_JWT_TOKEN
```

### Endpoints

#### Shorten a URL

- Endpoint: `/api/shorten`
- Method: `POST`
- Request Body:

```json
{
  "url": "YOUR_LONG_URL",
  "is_permanent": true,   // Optional
  "exp_date": "dd-mm-yyyy.HH:MM"   // Optional
}
```

#### Retrieve Orignal URL

- Endpoint: `/api/get`
- Method: `GET`
- Request Body:

```json
{
  "url": "SHORTENED_URL"   // Optional
}
```

#### Retrieve URL Statistics

- Endpoint: `/api/stats`
- Method: `GET`
- Request Body:

```json
{
  "url": "SHORTENED_URL"   // Optional
}
```

#### Update URL Settings

- Endpoint: `/api/update`
- Method: `PUT`
- Request Body:

```json
{
  "url": "SHORTENED_URL",
  "is_permanent": true,   // Optional
  "exp_date": "dd-mm-yyyy.HH:MM"   // Optional
}
```

#### Delete a URL

- Endpoint: `/api/delete`
- Method: `DELETE`
- Request Body:

```json
{
  "url": "SHORTENED_URL"
}
```

## Environment Configuration

To run this project, you need to set up your environment variables.

Create a file named `.env` in the root of the project and add the following configuration:

```env
DB=database_name
TEST_DB=test_database_name
ENV=your_environment
SECRET_KEY=your_secret_key
```

## Local Development

**Clone the Repository:**

```sh
git clone https://github.com/uosyph/url-shortener.git && cd url-shortener
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

## Production Deployment

### Prerequisites

Ensure the following prerequisites are installed on the server:

- `Nginx`, `Python`, and `pip`.
- The `venv` module for Python.
- A WSGI server like `Gunicorn`.
- A terminal multiplexer like `tmux`.

### Configure Nginx

**Create a Configuration File:**

```bash
sudo vi /etc/nginx/sites-available/shorten
```

**Add the Following Configuration:**

```nginx
server {
    listen 80;
    server_name 0.0.0.0;  # Use the actual domain or IP address

    location / {
        proxy_pass http://127.0.0.1:5000;  # Match the Gunicorn host and port
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    location /static/ {
        alias /home/ubuntu/shorten/static/;
    }

    location /favicon.ico {
        alias /home/ubuntu/shorten/static/images/favicon.ico;
    }

    error_page 404 /404.html;
    location /404.html {
        root /home/ubuntu/shorten/templates/;
    }
}
```

**Create a Symbolic Link to Enable the Configuration:**

```bash
sudo ln -s /etc/nginx/sites-available/shorten /etc/nginx/sites-enabled/
```

**Test Nginx Configuration:**

```bash
sudo nginx -t
```

**Restart Nginx:**

```bash
sudo systemctl restart nginx
```

### Deploy the Application

**Clone the Repository on the Server:**

```bash
git clone https://github.com/uosyph/url-shortener.git shorten
```

**Create a Virtual Environment:**

```bash
python -m venv shorten && source shorten/bin/activate && cd shorten/
```

**Install Production Requirements:**

```bash
pip install -r requirements.txt
```

**Deactivate the Virtual Environment:**

```bash
deactivate
```

**Build the Database:**

```sh
python database.py
```

**Run the App with Gunicorn (Inside a tmux Session):**

```bash
tmux new-session -d 'gunicorn -b 127.0.0.1:5000 app:app'
```

## Contributing

### Development

To fix a bug or enhance an existing feature, follow these steps:

- [Fork the repo](https://github.com/uosyph/url-shortener/fork)
- Create a new branch (`git checkout -b improve-feature`)
- Make the necessary changes
- Add changes to reflect updates
- Commit your changes (`git commit -am 'Improve feature'`)
- Push to the branch (`git push origin improve-feature`)
- [Create a Pull Request](https://github.com/uosyph/url-shortener/compare)

### Bug/Feature Request

If you find a bug or want to request a new feature:

- For bugs, [open an issue](https://github.com/uosyph/url-shortener/issues/new/choose) with details about the problem.
- For feature requests, [open an issue](https://github.com/uosyph/url-shortener/issues/new/choose) with your suggestions.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Author

**Yousef Saeed**:
[GitHub](https://github.com/uosyph)
[LinkedIn](https://linkedin.com/in/uosyph)
[X](https://twitter.com/uosyph)

<p align="right"><a href="#readme-top">Back to Top</a></p>
