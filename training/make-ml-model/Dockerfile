# Stage 1: Build stage
FROM rockylinux:9.3-minimal AS build

# Install necessary build tools
RUN microdnf install -y curl tar

# Download the hatch tar.gz file from GitHub
RUN curl -L https://github.com/pypa/hatch/releases/download/hatch-v1.14.0/hatch-x86_64-unknown-linux-gnu.tar.gz -o /tmp/hatch-x86_64-unknown-linux-gnu.tar.gz

# Extract the hatch binary
RUN tar -xzf /tmp/hatch-x86_64-unknown-linux-gnu.tar.gz -C /tmp/

# Stage 2: Final stage
FROM rockylinux:9.3-minimal

# Set up a default user and home directory
ENV HOME=/home/neo

# Install essential libraries including expat and python3 without `config` commands
RUN microdnf install -y \
    expat \
    libpq \
    curl \
    git \
    wget \
    tar \
    && microdnf install -y python3 \
    && microdnf clean all

# Create a user with UID 1001, group root, and a home directory
RUN useradd -u 1001 -g 100 -m -d ${HOME} -s /sbin/nologin \
         -c "Default Neo User" neo && \
    mkdir -p /code /prod ${HOME}/.cache /home/neo/.local/share/hatch && \
    chown -R neo:100 /code ${HOME} /home/neo/.local/share/hatch && \
    chmod -R 775 /code ${HOME}

# Copy the hatch binary from the build stage
COPY --from=build /tmp/hatch /usr/bin/hatch

# Ensure the hatch binary is executable
RUN chmod +x /usr/bin/hatch

# Switch to the non-root user
USER neo

# Copy the application files into the /code directory
COPY --chown=1001:100 . /code

WORKDIR /code

# Set up virtual environment paths
ENV VIRTUAL_ENV=/code/envs/env_5
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
ENV HATCH_PYTHON_VARIANT_LINUX=v2

# Prune any existing environments and create a new production environment
RUN hatch env prune && \
    hatch env create prod && \
    hatch run prod:tile-based-training --help