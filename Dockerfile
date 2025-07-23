FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy src folder
COPY src/ /app/src/
# RUN ls -R /app/src
# COPY src/ ./src/
# COPY src/main.py /github/workspace/src/main.py


# Copy entrypoint script
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
# RUN ls -R /github/workspace

# Set the entrypoint
ENTRYPOINT ["/entrypoint.sh"]