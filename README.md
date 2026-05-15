# Spatial Analytics API with FastAPI





## Project Vision: Building a Surveillance Analytics System

Are you a security manager, tired of seeing your bum guards get sneaked upon and taken out by the main character, who is a Sneak 
100 badass, even though they check every blindspot. 


<br> <p align ="center">
  <img src = "funnystealthmeme.gif">
</p>

Well this project might just be for you!
<hr>

### What this project set out to achieve

This project is a guard patrol coverage analyzer, which is built with FastAPI, NumPy, and Docker. It works as a spatial-temporal analytics system that processes guard patrol routes, computes surveillance coverage across a facility grid, and visualizes risk zones on an interactive map.


## Standing Up the Development Environment

### Project structure and dependencies

We will begin by creating the project directory, and setting up the virtual environment and install all dependencies. We will then verify the setup by running a minimal FastAPI health check  endpoint.

content = """# SSAS Project Directory Structure

```text
SSAS/
├── app/
│   ├── __init__.py
│   ├── analysis.py
│   ├── main.py
│   ├── models.py
│   ├── sample_data.py
│   └── visualization.py
├── .gitignore
├── docker-compose.yml
├── Dockerfile
├── funnystealthmeme.gif
├── README.md
└── requirements.txt


### How to run in github 
