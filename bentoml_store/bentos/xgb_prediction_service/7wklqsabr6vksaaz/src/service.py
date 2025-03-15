import os
os.environ["BENTOML_HOME"] = "../bentoml_store" # must be ran from inside the API folder
# while starting the script with bash, it seems like this variable change isn't used
# set BENTOML_HOME=C:\Users\Dev\Desktop\OpenClassrooms\Project6\Energy Co2\Predict-Energy-and-CO2-for-building\bentoml_store\
import bentoml
from bentoml.io import JSON
import pandas as pd
from pydantic import BaseModel, Field
from typing import Literal
# Define the BentoML service with metadata
from bentoml import Service
import joblib
import re

model_ref = bentoml.xgboost.get("xgb_model_with_features:latest")

encoder_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../encoder/one_hot_encoder.pkl")
OH_encoder = joblib.load(encoder_path)
scaler_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../encoder/std_scaler.pkl")
scaler = joblib.load(scaler_path)
xgb_runner = model_ref.to_runner()

svc = Service(
    name="xgb_prediction_service",
    runners=[xgb_runner]
)

# Access custom_objects from the model_ref
columns_to_scale = model_ref.custom_objects["columns_to_scale"]
categories = model_ref.custom_objects["categories"]
categorial_columns = list(categories.keys())
column_names = model_ref.custom_objects["feature_names"]

# Define Property Types
PropertyTypes = list(model_ref.custom_objects["categories"]['LargestPropertyUseType'])
BuildingTypes = list(model_ref.custom_objects["categories"]["BuildingType"])
CouncilDistrictCodes = list(model_ref.custom_objects["categories"]["CouncilDistrictCode"])

# Define the input schema using Pydantic
class InputSchema(BaseModel):
    PropertyGFAWithParking: float = Field(..., ge=0, description="Total Gross Floor Area (GFA) must not be negative, include parking if relevant.")
    PropertyParking: bool = Field(..., ge=0, description="True if the building includes a parking.") #to be renamed with GFA
    PropertyGFABuilding: float = Field(..., ge=0, description="Building Gross Floor Area (GFA) must not be negative, do not include parking.")
    ENERGYSTARScore: float = Field(..., ge=0, le=100, description="Energy Star score (0-100).")
    SteamUse: bool = Field(..., description="True if Steam is used, False otherwise.")
    ElectricityUse: bool = Field(..., description="True if Electricity is used, False otherwise.")
    NaturalGasUse: bool = Field(..., description="True if Natural Gas is used, False otherwise.")
    Age: int = Field(..., ge=0, description="Building age must be non-negative.")
    BuildingType: Literal[*BuildingTypes] = Field(..., description="Building type.")
    NumberofFloors: int = Field(..., ge=1, le=11, description="Number of floors, between 1 and 11")
    CouncilDistrictCode: Literal[*CouncilDistrictCodes] = Field(..., description="City council code between 1 and 7.")
    LargestPropertyUseType: Literal[*PropertyTypes] = Field(..., description="Main use type of the property.")

def preprocess_input(input_data: pd.DataFrame) -> pd.DataFrame:
    prepro_data = input_data.copy()
    prepro_data['PropertyAreaTimesFloorWithParking'] = (prepro_data['PropertyGFAWithParking']*prepro_data['NumberofFloors']).astype(int)
    prepro_data = prepro_data.drop("NumberofFloors", axis=1)
    prepro_data = prepro_data.drop("PropertyGFAWithParking", axis=1)

    col_order = ["PropertyGFABuilding", "ENERGYSTARScore", "PropertyParking", "SteamUse", "ElectricityUse", "NaturalGasUse", 
                    "Age", "PropertyAreaTimesFloorWithParking", "BuildingType",  "CouncilDistrictCode", "LargestPropertyUseType"]
    prepro_data = prepro_data.reindex(columns=col_order)
    prepro_data['CouncilDistrictCode'] = prepro_data['CouncilDistrictCode'].astype(str)

    # prepro_data.rename(columns={"LargestPropertyUseType" : "LargestPropertyUseType"}, inplace=True)
    return(prepro_data)

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
    df = preprocess_input(df)
    df[columns_to_scale] = scaler.transform(df[columns_to_scale])

    encoded_data = OH_encoder.transform(df[categorial_columns])
    encoded_df = pd.DataFrame(
        encoded_data,
        columns=OH_encoder.get_feature_names_out(categorial_columns),
        index= df.index).astype(int)
    df = pd.concat(
        [df.drop(columns=categorial_columns), encoded_df],
        axis=1
    )
    with pd.option_context('display.max_rows', None, 'display.max_columns', None):  # more options can be specified also
        print(df)
    print()
    df.columns = column_names
    with pd.option_context('display.max_rows', None, 'display.max_columns', None):  # more options can be specified also
        print(df)
    print()

    # Make predictions
    prediction = xgb_runner.run(df)
    return {"prediction": prediction}
