#!/bin/bash

# Update Homebrew (if installed)
if command -v brew &> /dev/null; then
    brew update
    brew upgrade deeplx          
    brew services restart owo-network/brew/deeplx
fi

# Install Python dependencies
pip install -r requirements.txt