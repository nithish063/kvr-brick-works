## Run with Docker (Windows CMD)

## Prerequisites

Before you start, ensure the following:

* **Docker Desktop** is installed and running on your system.
   [Download Docker Desktop](https://www.docker.com/products/docker-desktop)

##  Steps to Run

###  Step 1: Navigate to the project directory
Open **Command Prompt** and navigate to the `kvr-brick-works` folder:
[cd path\to\kvr-brick-works]
Replace `path\to\` with your actual folder path.

###  Step 2: Build the Docker image
[docker build -t kvr-brick-works .]
This will build a Docker image named `kvr-brick-works` from your current directory (`.`).

###  Step 3: Run the Docker container
[docker run -it --rm -p 5000:5000 kvr-brick-works]

Once successful, you’ll see something like: Running on http://127.0.0.1:5000

###  Step 4: Open the app in your browser

Visit: http://localhost:5000

If that doesn't work, try: http://127.0.0.1:5000

You should see your Flask web app running.
