""" COVERAGE ANALYSIS ENGINE """


import numpy as np
from shapely.geometry import Point
from colorama import init, Fore, Style
from app.models import AnalysisRequest, AnalysisResult, RiskZone, GuardRoute


""" 
The listed function will take the guards full route, and a specific time, then figures out exactly where the guard is
positioned in that moment. 
"""


def position_interpolation(route: GuardRoute, time: float) -> tuple[float, float]:
    """ Find a guards exact position at any given time by linear interpolation"""
    waypoints = route.waypoints
    
    # If the time is before the first waypoint, guard hasnt moved yet
    if time <= waypoints[0].timestamp:
        return waypoints[0].x, waypoints[0].y
    # if the time after the last waypoint, guard has finished the route
    if time >= waypoints[-1].timestamp:
        return waypoints[-1].x, waypoints[-1].y
    
    # Find which 2 waypoints the guard is between
    for i in range(len(waypoints) - 1):
        t0 = waypoints[i].timestamp
        t1 = waypoints[i + 1].timestamp
        if t0 <= time <= t1:
            # Calculate the difference between the 2 waypoints (0 to 1)
            # Ratio of 0.5 means the guard is halfway between the two waypoints, t0 and t1
            ratio = (time - t0) / (time - t1) 
            x = waypoints[i].x + ratio * (waypoints[i + 1].x - waypoints[i].x)
            y = waypoints[i].y + ratio * (waypoints[i + 1].y - waypoints[i].y)
            return x, y
        
    # Fallback, return last known position
    return waypoints[-1].x, waypoints[-1].y

""" Main Brunt of computation: 
Build the grid and compute the full coverage grid now, dividing the facility into a grid 
and then simulating the time passing in discrete steps, with each step being checked as to which 
grid cells fall into each guards observation radius using NumPy as to avoid slow python nested loops."""

 
def run_coverage_analysis(request: AnalysisRequest) -> AnalysisResult: 
    """ Compute coveragescores for every cell in facility grid"""
    facility = request.facility
    grid_res = facility.grid_resolution
    # Caclulate grid dimensions of the facility
    cols = int(facility.width/ grid_res)
    rows = int(facility.height-grid_res)

    #Build arrays of cell center coordinates
    cell_centers_x = np.arange(cols) * grid_res + grid_res / 2
    cell_centers_y = np.arange(rows) * grid_res + grid_res / 2
    
    # Create the 2d grids
    grid_x, grid_y = np.meshgrid(cell_centers_x, cell_centers_y)
    # Initialize coverage matrix 
    coverage_matrix = np.zeros((rows, cols), dtype=np.float64)
    
    # time range for all patrol routes (routes and waypoints)
    max_time = max(wp.timestamp for route in request.routes for wp in route.waypoints) 
    time_points = np.linspace(0, max_time, request.time_steps)

    # Loop to simulate each time step,  and receive the interpolated position of the guard at time (t) 
    # Compute Euclidean distance from the guard to every cell simultaneously
    # from guard to every cell center at one. Mark cells within guards obsv. radius
    for t in time_points:
        for route in request.routes:
            gx, gy = position_interpolation(route, t)
            distances = np.sqrt((grid_x - gx) ** 2 + (grid_y - gy) ** 2)
            # Mark cells within guards observation radius
            visible = distances <= route.observation_radius
            coverage_matrix += visible.astype(np.float64)

     
    # Normalize coverage scores to 0-1 range, so the highest covered cell has a score of 1.0
    if coverage_matrix.max() > 0:
        coverage_matrix = coverage_matrix / coverage_matrix.max()

        """ Then Identify risk zones from the covrage matrix """       
        # Count total cells and find those below the risk threshold
        total_cells = rows * cols
        risk_zones = []
        for r in range(rows):
            for c in range(cols):
             score = coverage_matrix[r, c]
             if score < request.risk_threshold:
                
                # SEVERITY CLASSIFICATION THRESHOLD
                severity = (f"{Fore.RED}{Style.BRIGHT}CRITICAL{Style.RESET_ALL}") if score < request.risk_threshold / 2 else (f"{Fore.YELLOW}{Style.NORMAL}HIGH{Style.RESET_ALL}")
                # each flagged cell becomes a risk zone object with both its grid coordinates and real world center position, so it can be plotted
                risk_zones.append( RiskZone (
                     cell_x=c,
                     cell_y=r,
                     center_x=cell_centers_x[c],
                     center_y=cell_centers_y[r],
                     coverage_score=round(float(score), 4),
                     severity=severity,
                ))
        # calculate summary statistics
        covered_cells = total_cells - len(risk_zones)
        covered_percentage = round((covered_cells / total_cells) * 100, 2)

        return AnalysisResult(
            total_cells=total_cells,
            covered_cells=covered_cells,
            risk_zones=risk_zones,
            coverage_percentage=covered_percentage,
            risk_zone_count=len(risk_zones),
        )


"""
Temporal Analysis Function
 - Important in turning a static safe or unsafe map into depicting an animated threat timeline. The temporal analysis will
reuse the existing grid mth, but run it once per time window. 
"""

def run_temporal_analysis(request: AnalysisRequest, window_duration: float = 60.0) -> list[dict]:
 """Produce per window coverage to identify WHEN the risk zones appear"""
 facility = request.facility
 grid_res = facility.grid_resolution
 cols = int(facility.width / grid_res)
 rows = int(facility.height / grid_res)

 # Grid build
 cell_centers_x = np.arange(cols) * grid_res + grid_res / 2
 cell_centers_y = np.arange(rows) * grid_res + grid_res / 2
 grid_x, grid_y = np.meshgrid(cell_centers_x, cell_centers_y)

 # Time patrol time duration
 max_time = max(wp.timestamp for route in request.routes for wp in route.waypoints)
 
 # Split into windows (60 seconds each) and sample 10 time points within each
 num_windows = int(max_time / window_duration)
 temporal_results = []
 for w in range(num_windows):
    window_start = w * window_duration
    window_end = (w + 1) * window_duration
    time_points = np.linspace(window_start, window_end, 10)

    window_coverage = np.zeros((rows, cols), dtype=np.float64)

    # Accumulate coverage only for this time window
    for t in time_points:
       for route in request.routes:
          gx, gy = position_interpolation(route, t)
          distances = np.sqrt((grid_x - gx) ** 2 + (grid_y - gy) ** 2)
          visible = distances <= route.observation_radius
          window_coverage += visible.astype(np.float64)

    # normalize like in the coverage function
    if window_coverage.max() > 0:
       window_coverage = window_coverage / window_coverage.max()

    # Identify risk cells for the window
    risk_cells = []
    for r in range(rows):
       for c in range(cols):
          if window_coverage[r, c] < request.risk_threshold:
             risk_cells.append({
                "cell_x": c,
                "cell_y": r,
                "center_x": float(cell_centers_x[c]), 
                "center_y": float(cell_centers_y[r]),
                "coverage_score": round(float(window_coverage[r, c]), 4), 
             })
    # Window objects, with each containing its own set of risk cells
    temporal_results.append({
       "window_index": w,
       "window_start": window_start,
       "window_end": window_end,
       "risk_zone_count": len(risk_cells),
       "risk_cells": risk_cells
    })

    return temporal_results






""" 
python -c "from app.analysis import run_coverage_analysis; from app.sample_data import generate_sample_patrol; 
result = run_coverage_analysis(generate_sample_patrol()); print(f'Coverage: {result.coverage_percentage}%, 
Risk zones: {result.risk_zone_count}')" """