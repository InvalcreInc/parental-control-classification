#!/bin/bash

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m'

#
function error_exit {
    error_msg "$1" 1>&2
    exit 1
}

function header_msg {
    echo -e ""
    echo -ne "${GREEN}$1${NC}"
}

function success_msg {
    echo -e "${GREEN}$1${NC}"
}

function warning_msg {
    echo -e "${YELLOW}$1${NC}"
}

function info_msg {
    echo -e "${BLUE}$1${NC}"
}

function error_msg {
    echo -e "${RED}$1${NC}"
}


# get the path
header_msg "Enter the path to the script: "
read path

# cd to the path
cd $path

# check for venv
if [[ -z "$VIRTUAL_ENV" ]]; then
    info_msg "No venv found"
    python3 -m venv venv 
    success_msg "venv created"
    source venv/bin/activate
    success_msg "venv activated"
fi

# check for required packages
if [ ! -f "requirements.txt" ]; then
    error_msg "requirements.txt not found"
    exit 1
fi

while IFS= read -r line; do
    if [[ -z "$line" || "$line" == "#"* ]]; then
        continue
    fi

    if pip3 show "$line" > /dev/null 2>&1; then
        success_msg "$line already installed"
    else
        pip3 install "$line" 
        success_msg "$line installed"
    fi
done < requirements.txt

# run the script
header_msg "Enter the script to run (with .py): "
read script

if [ ! -f "$script" ]; then
    error_exit "$script not found"
fi

python3 "$script"