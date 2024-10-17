import logging

# Create a custom logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Create handlers
console_handler = logging.StreamHandler()  # For printing to terminal
file_handler = logging.FileHandler('execution.log')  # For logging to a file

# Create formatters and add it to handlers
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)

# Add handlers to the logger
logger.addHandler(console_handler)
logger.addHandler(file_handler)

# Example logging
logger.info("This message will be logged to both console and file.")
logger.error("This error will be logged to both console and file.")