import os
os.environ["BENTOML_HOME"] = "../bentoml_store" # must be ran from inside the API folder
# while starting the script with bash, it seems like this variable change isn't used
# set BENTOML_HOME=C:\Users\Dev\Desktop\OpenClassroom\Projet6\Anticipez les besoins en consommation de bâtiments\Predict-Energy-and-CO2-for-building\bentoml_store
import bentoml
from bentoml.io import JSON
import pandas as pd
from pydantic import BaseModel, Field
from typing import Literal
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
scaler = model_ref.custom_objects["scaler"]
categories = model_ref.custom_objects["categories"]

# Define Property Types
PropertyTypes = list(model_ref.custom_objects["categories"]["PropertyTypes"])
BuildingTypes = list(model_ref.custom_objects["categories"]["BuildingType"])
CouncilDistrictCodes = list(model_ref.custom_objects["categories"]["CouncilDistrictCode"])

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
    BuildingType: Literal[*BuildingTypes] = Field(..., description="Building type.")
    Floors: int = Field(..., ge=1, le=11, description="Number of floors, between 1 and 10")
    CouncilDistrictCode: Literal[*CouncilDistrictCodes] = Field(..., description="City council code.")
    LargestPropertyUseType: Literal[*PropertyTypes] = Field(..., description="Property use type.")

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

    for col, cat in categories.items():
        one_hot = pd.get_dummies(df[col], prefix=col)
        for category in cat:
            if f"{col}_{category}" not in one_hot:
                one_hot[f"{col}_{category}"] = 0
        df = pd.concat([df.drop(columns=[col]), one_hot], axis=1)

    # Ensure the DataFrame matches the expected input for the model
    expected_columns = categories["BuildingType"] + categories["LargestPropertyUseType"]
    for col in expected_columns:
        if col not in df.columns:
            df[col] = 0  # Add missing columns with default value (0)

    # Reorder columns to match the model's training order
    df = df[expected_columns + columns_to_scale]

    # Make predictions
    prediction = xgb_runner.run(df)
    return {"prediction": prediction.tolist()}
