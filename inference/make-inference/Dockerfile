FROM ubuntu:20.04
ARG DEBIAN_FRONTEND=noninteractive
ENV APP_ENV=make_inference

SHELL ["/bin/bash", "-c"]

# Define the default user
ARG USERNAME=neo
ARG USER_GID=1000

# Update package lists and install necessary utilities

RUN apt-get update && apt-get install -y \
    curl \
    tar \
    bzip2 \
    libexpat1 \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Create a non-root user
RUN groupadd --gid $USER_GID $USERNAME && \
    useradd --uid $USER_GID --gid $USER_GID --create-home $USERNAME

# Install micromamba
RUN curl -Ls https://micro.mamba.pm/api/micromamba/linux-64/latest -o /tmp/micromamba.tar.bz2 && \
    bzip2 -t /tmp/micromamba.tar.bz2 && \
    tar -xvjf /tmp/micromamba.tar.bz2 -C /tmp && \
    mv /tmp/bin/micromamba /bin/micromamba

# Initialize micromamba
RUN micromamba shell init -s bash

# Set up the environment
ENV MAMBA_ROOT_PREFIX=/home/$USERNAME/conda
ENV PATH=$PATH:/home/$USERNAME/conda/envs/$APP_ENV/bin:/home/$USERNAME/conda/envs/$APP_ENV/snap/bin

# Change ownership of /home/$USERNAME
RUN chown -R $USERNAME:$USER_GID /home/$USERNAME

# Copy application files with correct ownership
COPY --chown=$USERNAME:$USER_GID . /tmp

# Create the environment and install dependencies
RUN micromamba create -f /tmp/environment.yml && \
    cd /tmp && \
    $MAMBA_ROOT_PREFIX/envs/$APP_ENV/bin/python setup.py install

# Set user to non-root for security
USER $USERNAME

# Set working directory
WORKDIR /home/$USERNAME

CMD ["/bin/bash"]
