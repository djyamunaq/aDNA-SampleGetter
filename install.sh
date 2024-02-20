#!/bin/bash

# Stop script if any command fail
set -e

# Force sudo activation
sudo ls >> /dev/null 2>&1

# Remove temporary loading animation file if it exists
if [ -f "sgetpipe/temp" ] ; then
    sudo rm "sgetpipe/temp" >> /dev/null 2>&1
fi

# Create temporary loading animation file
echo -e "#!/bin/bash\n\n"\$@" &\nwhile kill -0 \$!; do\n\tprintf '.' > /dev/tty\n\tsleep 1\ndone\nprintf '\\n' > /dev/tty" >> sgetpipe/temp 

# Update packages
echo -n "> Updating packages "
sudo ./sgetpipe/temp apt update >> /dev/null 2>&1

# Install beautifulsoup4
echo -n "> Installing beautifulsoup4 "
sudo ./sgetpipe/temp pip install beautifulsoup4 >> /dev/null 2>&1

# Install pandas
echo -n "> Installing pandas "
sudo ./sgetpipe/temp pip install pandas >> /dev/null 2>&1

# Update git submodules
echo -n "> Updating project modules "
sudo ./sgetpipe/temp git submodule update --init --recursive >> /dev/null 2>&1

# pip install sgetpipe package
echo "> Installing sgetpipe\n\n"
if pip install -e .; then
    GREEN='\033[0;32m'
    echo -e "${GREEN}> Successfully installed package sgetpipe"
else
    RED='\033[0;31m'
    echo -e "${RED}> Failed installing package sgetpipe"
fi

# Reset terminal colors
WHITE="\033[0;37m"
echo -ne "${WHITE}"

# Remove temporary loading animation file
rm sgetpipe/temp

