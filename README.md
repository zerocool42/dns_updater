# DNS Updater

This project is a web application that updates a DNS record to the visitor's IP address using Cloudflare's API. The application is built using Flask and can be run inside a Docker container.

## Usecase
I made this for updating a DNS record to a client to allow be able to allow a FQDN in my firewall to allow connections. 

When I need to log in to my server I can visit a site to update the record to myself and then log in on my server.  

## Prerequisites

- Docker or Python

## Setup

1. Clone the repository:
    ```sh
    git clone https://github.com/zerocool42/dns_updater/
    cd dns_updater
    ```

2. Create a .env file in the root directory of the project and add the following environment variables:
    ```env
    CLOUDFLARE_EMAIL=your_cloudflare_email
    CLOUDFLARE_API_KEY=your_cloudflare_api_key
    CLOUDFLARE_ZONE_ID=your_cloudflare_zone_id
    CLOUDFLARE_NAME_FILTER=your_dns_name_filter
    ADMIN_USERNAME=your_admin_username
    ADMIN_PASSWORD=your_admin_password
    SECRET_KEY=your_flask_secret_key
    ```

## Running the Application

### Using Docker

1. Build the Docker image:
    ```sh
    docker build -t dns_updater .
    ```

2. Run the Docker container:
    ```sh
    docker run -d -p 5000:5000 dns_updater
    ```

### Without Docker

1. Install the required packages:
    ```sh
    pip install -r requirements.txt
    ```

2. Run the application:
    ```sh
    python dns_updater.py
    ```
