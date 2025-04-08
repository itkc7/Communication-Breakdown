#!/bin/bash

chmod +x build.sh

#update homebrew
brew update
brew upgrade deeplx          
brew services restart owo-network/brew/deeplx


# Install Python dependencies
pip install -r requirements.txt