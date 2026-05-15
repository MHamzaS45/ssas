"""
CREATION OF PYDANTIC DATA MODELS
"""
################################

"""SPATIAL ANALYSIS"""

from pydantic import BaseModel, Field

# Represents a single point on a guards route in the x/y graph , alongside a timestamp marking when the guard arrives there
class Waypoint(BaseModel):
    x: float = Field(description="X coordinate in facility units")
    y: float = Field(description="Y coordinate in facility units")
    timestamp: float = Field(description="Time in seconds from initiation of patrol")

# Group a series of waypoints into a single patrol path.
class GuardRoute(BaseModel):
    guard_id: str = Field(description="Unique guard identifer")
    # utilize list as the values are mutable
    waypoints: list[Waypoint] = Field(description = "Ordered list of patrol waypoints")
    observation_radius: float = Field(description = "Guard visibility radius in facility " \
    "units"
    )


""" TEMPORAL ANALYSIS """

# Define the physical space beign monitored
class FacilityConfig(BaseModel):
    width: float = Field(description = "Facility Width in facility units")
    height: float = Field(description = "Facility Height in facility units")

    """Control how finely the space is 
    divided into cells for analysis"""
    grid_resolution: float = Field(default = 1.0, description = 
                                   "The size of each grid in units"
                                   )

# Top level input model that packages everything together. 
class AnalysisRequest(BaseModel):
    facility: FacilityConfig
    routes: list[GuardRoute]

    """ Set the coverage score cutoff."""
    risk_threshold: float = Field(
        default = 0.2, # anything below this will be flagged as a risk zone
        description = "Coverage score below which a cell is flagged as a risk zone (0-1)",
        )
    time_steps: int = Field(default=100, description = "Number of time steps to simulate")

""" Describe Analysis Results"""

# Represents a signel cell that is flagged as underwatched.
class RiskZone(BaseModel):
    cell_x: int
    cell_y: int
    center_x: float
    center_y: float
    coverage_score: float
    severity: str 

# Summarizes the full analysis output with aggregate stats and the list of flagged risk zones
class AnalysisResult(BaseModel):
    total_cells: int 
    covered_cells: int 
    risk_zones: list[RiskZone]
    coverage_percentage: float
    risk_zone_count: int
