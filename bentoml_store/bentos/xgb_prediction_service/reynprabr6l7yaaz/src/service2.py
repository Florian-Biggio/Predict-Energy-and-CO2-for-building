import os
import bentoml
from bentoml import Service, Runnable, Runner
from bentoml.io import JSON
import pandas as pd
from pydantic import BaseModel, Field
from typing import Literal

# Set BentoML home directory
os.environ["BENTOML_HOME"] = "../bentoml_store"

# Define a dummy model that always predicts 10
class DummyModelRunnable(Runnable):
    SUPPORTED_RESOURCES = ("cpu",)  # Define supported resources for the runner
    SUPPORTS_CPU_MULTI_THREADING = False  # Define threading behavior

    @bentoml.Runnable.method(batchable=True)  # Correct usage of BentoML Runnable
    def run_batch(self, input_data):
        # Always return a list of 10s with the same length as the input
        return [10] * len(input_data)

# Initialize the dummy runner
dummy_runner = Runner(DummyModelRunnable)

# Define the BentoML service for the dummy model
svc = Service(
    name="dummy_prediction_service",
    runners=[dummy_runner]
)

# Define the input schema using Pydantic
class InputSchema(BaseModel):
    PropertyGFATotal: float = Field(..., ge=0, description="Total GFA must not be negative.")
    PropertyGFAParking: float = Field(..., ge=0, description="Parking GFA must not be negative.")
    PropertyGFABuilding_s_: float = Field(..., ge=0, description="Building GFA must not be negative.")
    ENERGYSTARScore: float = Field(..., ge=0, le=100, description="Energy Star score (0-100).")
    SteamUse: bool = Field(..., description="True if Steam is used, False otherwise.")
    Electricity: bool = Field(..., description="True if Electricity is used, False otherwise.")
    NaturalGas: bool = Field(..., description="True if Natural Gas is used, False otherwise.")
    Age: int = Field(..., ge=0, description="Building age must be non-negative.")
    BuildingType: str = Field(..., description="Building type.")
    Floors: int = Field(..., ge=1, le=11, description="Number of floors, between 1 and 10")
    CouncilDistrictCode: str = Field(..., description="City council code.")
    LargestPropertyUseType: str = Field(..., description="Property use type.")

# Define the API endpoint
@svc.api(input=JSON(pydantic_model=InputSchema), output=JSON(), doc="Make predictions based on property data.")
def predict(input_data: InputSchema):
    """
    Predict the energy efficiency score for a property based on input data.

    Args:
        input_data (InputSchema): The property data for prediction.

    Returns:
        dict: A dictionary containing the prediction result.
    """
    # Convert input data to a DataFrame
    df = pd.DataFrame([input_data.dict()])

    # Dummy prediction always returns 10
    prediction = dummy_runner.run(df)
    return {"prediction": prediction}
