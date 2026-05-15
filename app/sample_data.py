""" SAMPLE PATROL DATA GENERATOR """

import math

from app.models import AnalysisRequest, FacilityConfig, GuardRoute, Waypoint


def generate_sample_patrol() -> AnalysisRequest:
    # Define a 50x50 unit facility with 1-unit grid cells
    facility = FacilityConfig(width=50.0, height=50.0, grid_resolution=1.0)

    # Guard ALPHA patrol details: Left side and counter
    guard_alpha = GuardRoute(
        guard_id="ALPHA",
        waypoints=[
            Waypoint(x=5.0, y=5.0, timestamp=0.0),
            Waypoint(x=5.0, y=25.0, timestamp=60.0),
            Waypoint(x=5.0, y=45.0, timestamp=120.0),
            Waypoint(x=25.0, y=45.0, timestamp=180.0),
            Waypoint(x=25.0, y=25.0, timestamp=240.0),
            Waypoint(x=5.0, y=5.0, timestamp=300.0),
        ],
        observation_radius=6.0,
    )

    # Guard BRAVO patrol: right side and center
    guard_bravo = GuardRoute(
        guard_id="BRAVO",
        waypoints=[
            Waypoint(x=45.0, y=45.0, timestamp=0.0),
            Waypoint(x=45.0, y=25.0, timestamp=60.0),
            Waypoint(x=45.0, y=5.0, timestamp=120.0),
            Waypoint(x=25.0, y=5.0, timestamp=180.0),
            Waypoint(x=25.0, y=25.0, timestamp=240.0),
            Waypoint(x=45.0, y=45.0, timestamp=300.0),
        ],
        observation_radius=6.0,
    )

    # Guard CHARLIE patrol:  inner quadrants
    guard_charlie = GuardRoute(
        guard_id="CHARLIE",
        waypoints=[
            Waypoint(x=25.0, y=25.0, timestamp=0.0),
            Waypoint(x=15.0, y=15.0, timestamp=75.0),
            Waypoint(x=35.0, y=15.0, timestamp=150.0),
            Waypoint(x=35.0, y=35.0, timestamp=225.0),
            Waypoint(x=15.0, y=35.0, timestamp=300.0),
        ],
        observation_radius=5.0,
    )
    # Route leaves corner areas undercovered as to produce risk for the analysis engine to detect 

    # Bundle everything into a complete analysis request
    
    return AnalysisRequest(
        facility=facility,
        routes=[guard_alpha, guard_bravo, guard_charlie],
        risk_threshold=0.2,
        time_steps=100,
    )

""" 
Full JSON Schema is printed by running in bash cmd:
python -c "from app.models import AnalysisRequest; import json; print(json.dumps(AnalysisRequest.model_json_schema(), indent=2))"

Note : If an attribute error is detected, verify if the correct version of pydantic is installed by running "pip show pydantic"
"""


