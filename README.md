--------
CSC 210 Project 2
Authors: Gaurav Sarangi, Austin Shilling
--------

# Saxopedia

## Purpose
Saxopedia is an encyclopedia of standard classical saxophone repertoire, in which users can access information on pieces, save programs, and have a running list of the repertiore they have studied.

## Navigation


## Key URLs


## Additional Requirements

### User Authentication
Users can log in and and have personalized saved data, further explained below


### Additional Database Interactions
Users will implement personalized databases for:
- repetoire studied lists
- programs

### Front-End Application
Display will be filtered using JS. Possible filters include:
- Composer name
- Style
- Time Period


### JSON Parsing
Saxopedia accesses:
- OpenOpus: an open source API of composers and their information outputed as a JSON source
- sax-repertoire: a personal JSON file of repertoire information, hosted on github, accessible via raw data.

## Setup Instructions
```bash
# 1. Ensure location is correct
cd Saxopedia

# 2. Activate Virtual Environmnet
venv/Scripts/activate

# 3. Run the app
python app/app.py