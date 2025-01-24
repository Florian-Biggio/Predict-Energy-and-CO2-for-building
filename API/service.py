import os
os.environ["BENTOML_HOME"] = "../bentoml_store" # must be ran from inside the API folder
# while starting the script with bash, it seems like this variable change isn't used
# set BENTOML_HOME=C:\Users\Dev\Desktop\OpenClassroom\Projet6\Anticipez les besoins en consommation de bâtiments\Predict-Energy-and-CO2-for-building\bentoml_store
import bentoml
from bentoml.io import JSON
import pandas as pd
from pydantic import BaseModel, Field
from typing import Literal
import numpy as np
from sklearn.preprocessing import OneHotEncoder, StandardScaler
# Define the BentoML service with metadata
from bentoml import Service

model_ref = bentoml.xgboost.get("xgb_model_with_scaler:latest")
xgb_runner = model_ref.to_runner()

svc = Service(
    name="xgb_prediction_service",
    runners=[xgb_runner]
)

# Access custom_objects from the model_ref
columns_to_scale = model_ref.custom_objects["columns_to_scale"]
# scaler = model_ref.custom_objects["scaler"]
categories = model_ref.custom_objects["categories"]

# Define Property Types
PropertyTypes = list(model_ref.custom_objects["categories"]["PropertyTypes"])
BuildingTypes = list(model_ref.custom_objects["categories"]["BuildingType"])
CouncilDistrictCodes = list(model_ref.custom_objects["categories"]["CouncilDistrictCode"])

categorical_columns = ["cat_col1", "cat_col2", "cat_col3"]
columns_to_scale = ['PropertyGFATotal',
    'PropertyAreaTimesFloorWithParking',
    'LargestPropertyUseTypeGFA',
    'ENERGYSTARScore',
    'Age']

# Define the input schema using Pydantic
class InputSchema(BaseModel):
    PropertyAreaTimesFloorWithParking: float = Field(..., ge=0, description="Total Gross Floor Area (GFA) must not be negative, include parking if relevant.")
    PropertyParking: bool = Field(..., ge=0, description="True if the building includes a parking.") #to be renamed with GFA
    PropertyGFABuilding_s_: float = Field(..., ge=0, description="Building Gross Floor Area (GFA) must not be negative, do not include parking.")
    ENERGYSTARScore: float = Field(..., ge=0, le=100, description="Energy Star score (0-100).")
    SteamUse: bool = Field(..., description="True if Steam is used, False otherwise.")
    Electricity: bool = Field(..., description="True if Electricity is used, False otherwise.")
    NaturalGas: bool = Field(..., description="True if Natural Gas is used, False otherwise.")
    Age: int = Field(..., ge=0, description="Building age must be non-negative.")
    BuildingType: Literal[*BuildingTypes] = Field(..., description="Building type.")
    Floors: int = Field(..., ge=1, le=11, description="Number of floors, between 1 and 10")
    CouncilDistrictCode: Literal[*CouncilDistrictCodes] = Field(..., description="City council code.")
    LargestPropertyUseType: Literal[*PropertyTypes] = Field(..., description="Property use type.")

def preprocess_input(input_data):
    try:

        return processed_data
    except Exception as e:
        raise ValueError(f"Error in preprocessing input: {str(e)}")

def HotKeyEncoding(input_data):
    # Specify the categories for each column
    categories = [
        ["cat1", "cat2", "cat3"],  # Categories for column 1
        ["A", "B", "C", "D"],      # Categories for column 2
        ["low", "medium", "high"]  # Categories for column 3
    ]

    # Initialize the OneHotEncoder
    encoder = OneHotEncoder(categories=categories, sparse_output=False)  # Use sparse=False for dense output

    # Fit the encoder (you can fit it on a sample dataset or dummy data)
    encoder.fit([["cat1", "A", "low"], ["cat2", "B", "medium"]])  # Example data




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

    df[columns_to_scale] = scaler.transform(df[columns_to_scale])

    # Make predictions
    prediction = xgb_runner.run(df)
    return {"prediction": prediction.tolist()}
