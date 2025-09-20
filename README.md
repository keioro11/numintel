# numintel
Reverse lookup on any phone number

## About
This tool allows to get information about phone numbers from different number validation services

## Features
The project is new and uses only 3 API-s:
numverify, abstract and twilio

## Configuration
To use **numintel**, add your API keys to **config.json** file

## How to use
First install python and pip:
`sudo apt update && sudo apt install -y python3 python3-pip`

Install requirements:
`pip install -r requirements.txt --break-system-packages`

Example:
`python3 numintel.py +7395541XXXX`

Including region:
`python3 numintel.py +7395541XXXX --region RU`

Output in json structure:
`python3 numintel.py +7395541XXXX --json`

## To do list
- [] Integrate more APIs
- [] Add search engine dorks with different number formats
