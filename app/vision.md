# Project Vision: Building a Surveillance Analytics System <br>

#### What this project set out to achieve
This project is a guard patrol coverage analyzer, which is built with FastAPI, NumPy, and Docker. It works as a spatial-temporal analytics system that processes guard patrol routes, computes surveillance coverage across a facility grid, and visualizes risk zones on an interactive map.

### Standing Up the Development Environment
Project structure and dependencies
We will begin by creating the project directory, and setting up the virtual environment and install all dependencies. We will then verify the setup by running a minimal FastAPI health check endpoint.
<img width="558" height="73" alt="image" src="https://github.com/user-attachments/assets/67c7d358-ffbc-4743-a8a3-ac95047b8e3c" />



#### Role of init.py in the app module
The init.py file makes sure /app is considered as a proper package from which you can import later.


## Designing the Data Models and Patrol Scenarios
Pydantic models and sample data generation
We will then define all the necessary data models through pydantic, for patrol routes, facility config, analysis. We will then verify the state by building a sample data generator with threee guards patrolling a 50x50 grid facility, and verify the models performance by generating and inspecting the sample data.

<img width="690" height="212" alt="image" src="https://github.com/user-attachments/assets/99eb0cb9-7f87-4b12-b0b3-ebb82059cbc9" />


How risk thresholds drive the analysis
The risk threshold field plays a crucial role in highlighting the risky/danger zones that are prone to being left uncovered during patrols.

## Implementing the Grid-Based Coverage Analysis Engine
NumPy broadcasting and spatial coverage computation
This section will focus on building the brain of the system: a coverage analysis engine that highlights the patrols routes, and then computes which areas of the facility is being watched. We will build a poisiton interpolation helper that locates any guard at any point in time, implementing a grid-based coverage algorithm using NumPy broadcasting. Risk zones detected will be then classified by severity using matrix.

<img width="593" height="60" alt="image" src="https://github.com/user-attachments/assets/13645bfd-3d5a-43e5-81a3-f6a3089c836d" />


#### Coverage matrix normalization and risk zone detection
The coverage matrix serves to normalize coverage scores in the range 0-1, with 1 being significant of the highest covered cell. This will be used to identify all the risk zones, classifying them by their severity based on their value.

## Generating the Interactive Folium Map
#### Building the visualization layer
Now that the analysis engine had produced a coverage matrix, alongside the number of risk zones, the next process involves developing the interactive map through folium. This will render patrol routes as coloured lines, and paint heatmaps over weak coverage areas and marking the risk zones deemed critical by the analysis engine.

#### From analysis results to browser-ready heatmap
The generate_map function basically requests data of the facility and its coordinates, before creating a map via folium. It uses a selection of markers and polyline to plot the path taken by the guards. It then marks risk_zones with critical severity as detected by the analysis results with red markers on a heatmap.

## Wiring Up the FastAPI Endpoints
REST API design with Pydantic validation and Swagger docs
We will create a FastAPI application with a health check endpoint. We will also tie up the endpoints as to be able to run the analysis, and serve the interactive map as an HTML response.




## Containerizing and Deploying with Docker
#### Dockerfile and docker-compose for one-command deployment
We will focus on delivering the application through containerization using Docker.

#### Production healthcheck strategy
Healthcheck is a great way to ensure systems are operational. It pings the /health endpoint every 30 seconds to confirm the API is responsive.

#### What temporal analysis reveals beyond aggregate coverage
Aggregate analysis (what your engine currently does) sums up all observations across all 100 time_steps and normalizes them into a single score per cell. It answers: "Overall, how often was this cell observed?"

<img width="443" height="435" alt="image" src="https://github.com/user-attachments/assets/9e32a396-10df-4c00-9e4f-7bba74aac7c8" />
