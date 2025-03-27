FROM python:3.12-slim

# Set the working directory
WORKDIR /app

# Copy the spider.py file into the container
COPY spider/spider.py requirements.txt /app/

# Install required dependencies
RUN pip install -r requirements.txt

# Set the command to run the script
ENTRYPOINT ["python", "spider.py"]
