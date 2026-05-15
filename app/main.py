""""
FAST API Application
- Create the endpoint
"""
###############
### IMPORTS ###
###############

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse

from app.analysis import run_coverage_analysis, run_temporal_analysis
from app.models import AnalysisRequest, AnalysisResult
from app.sample_data import generate_sample_patrol
from app.visualization import generate_map, generate_temporal_map

# Creation of FastAPI application instance. 
app = FastAPI(
    title = "Stealth Surveillance Analysis System",
    description = "Analyze guard patrol data and detect risk zones with weak coverage.", 
    version="1.0.0",
)

# In memory storage (results can be used as reference)
last_analysis: dict = {} 

# Register a GET endpoint path using "/health"
@app.get("/health")
# FastAPI calls this function and returns the dictionary as JSON as to confirm the service is running
def health_check():
    return{"status": "operational", "system": "SSAS", "version": "1.0.0"}


""" ENDPOINTS
- response model paramter tells FastAPI to validate response against the Pydantic model, as to autogenerate the 
response schema
- POSTendpoint accepts a full AnalysisRequest body 
- GET endpoint is a shortcut, that uses the patrol generator to test the workflow without using a JSON payload.
- map endpoint serves the folium HTML directly using the response class.  
"""

# Post
@app.post("/analyze", response_model=AnalysisResult)
def analyse_patrols(request: AnalysisRequest):
    # Run the coverage analysis engine on the submitted patrol data
    result = run_coverage_analysis(request)
    # store for later use by /map endpoint
    last_analysis["request"] = request
    last_analysis["result"] = result
    return result

# Get (sample data)
@app.get("/analyze/sample", response_model=AnalysisResult)
def analyze_sample():
    # generate sample patrol data and run analysis for testing
    request = generate_sample_patrol()
    result = run_coverage_analysis(request)
    last_analysis["request"] = request
    last_analysis["result"] = result
    return result

# Get (map)
@app.get("/map", response_class=HTMLResponse)
def get_map():
    # Check that an analysis has been run before trying to render, if not raise an statuscode404
    if "request" not in last_analysis or "result" not in last_analysis:
        raise HTTPException(
            status_code=404, detail="No analysis has been run yet. Call /analyze or /analyze/sample first.", 
            )
    # Generate and serve the interactive Folium map as raw HTML
    html = generate_map(last_analysis["request"], last_analysis["result"])
    return HTMLResponse(content=html)

# Get (temporal risk)
@app.get("/temporal-risk")
def get_temporal_risk(window_duration: float = 60.0):
    """Return a timeline of risk zone activity per time window, in JSON"""
    if "request" not in last_analysis:
        raise HTTPException(
            status_code = 404,
            detail="No analysis has been run yet. Call /analyze or /analyze/sample first to receive data.",
            )
    # Use  last_analysis dictionary
    results = run_temporal_analysis(last_analysis["request"], window_duration)
    return {"windows": results, "window_count": len(results)}

# get (temporal map)
@app.get("/temporal-map", response_class=HTMLResponse) 
def get_temporal_map(window_duration: float = 60.0):
    """ Deliver an animated heatmap with risk zones showing/disappearing overtime in HTML"""
    if "request" not in last_analysis:
        raise HTTPException(
            status_code=404,
            detail="No analysis has been run yet. Call /analyze or /analyze/sample first.",
             )
    # Reuse last_analysis dictionary
    results = run_temporal_analysis(last_analysis["request"],
                                    window_duration)
    html = generate_temporal_map(last_analysis["request"], results)
    return HTMLResponse(content=html)




# Start server with command "uvicorn app.main:app --reload" (bash cmd)