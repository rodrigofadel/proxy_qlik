# Simple Proxy for Client and Qlik Cloud Communication

This repository contains a simple proxy developed in **Python** using **FastAPI**, designed to intermediate communication between a **client** and **Qlik Cloud**. The main goal is to avoid the need for using **third-party cookies** in the client application, ensuring that cookies are mediated by the proxy as needed.

## Features

- **Simple Proxy**: Mediates communications between an application client and Qlik Cloud.
- **No Third-Party Cookies**: Eliminates the need for third-party cookies in your application by managing authentication cookies within the proxy.
- **Dockerized Setup**: Includes a Docker configuration to build and run the proxy along with **Nginx**.
- **WebSocket Support**: Example configurations for handling WebSocket requests via **Nginx**.
- **Built with Python and FastAPI**: Designed for simplicity and efficiency.

---

## Technologies Used

- **Python 3.12**
- **FastAPI**
- **Docker**
- **Nginx**


---

## Getting Started

### Prerequisites

- [Docker](https://www.docker.com/)
- [Docker Compose](https://docs.docker.com/compose/)

### Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/rodrigofadel/proxy_qlik.git
    cd your_repository
    ```

2. Build and run the Docker containers:
    ```sh
    docker-compose up --build
    ```

3. Set environment variables in docker-compose.yml

### Usage

- The proxy will be available at `https://localhost/proxy`
- Configure your application to use this proxy for all communications with **Qlik Cloud**.

---

## Project Structure

```
/
├── nginx/
│   ├── Dockerfile
│   ├── generate_cert.sh
│   ├── nginx.conf
│
├── proxy/
│   ├── app
│   |   ├── main.py
│   ├── Dockerfile
│   ├── requirements.txt
│
├── docker-compose.yml
├── README.md
```

---

## Contribution

Feel free to open **issues** and **pull requests** if you have improvements or fixes to suggest.