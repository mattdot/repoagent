# Use the .NET SDK image for building and running
FROM mcr.microsoft.com/dotnet/sdk:8.0

# Install TPM tools for comprehensive TPM operations
RUN apt-get update && apt-get install -y \
    tpm2-tools \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy source files
COPY src/ ./src/

# Copy entrypoint script
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Set the entrypoint
ENTRYPOINT ["/entrypoint.sh"]