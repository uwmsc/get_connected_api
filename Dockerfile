FROM ubuntu:20.04

# apt-get and system utilities
RUN apt-get update && apt-get install -y \
    gnupg2 \
    curl \
    apt-transport-https \
    debconf-utils \ 
    python3 \
    python3-pip \
    unixodbc-dev \
    && rm -rf /var/lib/apt/lists/*

# adding custom MS repository
RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -
RUN curl https://packages.microsoft.com/config/ubuntu/20.04/prod.list > /etc/apt/sources.list.d/mssql-release.list

# install SQL Server drivers and tools
RUN apt-get update && ACCEPT_EULA=Y apt-get install -y msodbcsql17 mssql-tools
RUN echo 'export PATH="$PATH:/opt/mssql-tools/bin"' >> ~/.bashrc
RUN /bin/bash -c "source ~/.bashrc"

# language and region
RUN apt-get -y install locales
RUN locale-gen en_US.UTF-8
RUN update-locale LANG=en_US.UTF-8

#install python dependencies
COPY requirements.txt .
RUN pip3 install -r requirements.txt

#create working directory
RUN mkdir /src
VOLUME [ "/src" ]
COPY /src/app.py /src
WORKDIR /src

#run the application
CMD python3 app.py