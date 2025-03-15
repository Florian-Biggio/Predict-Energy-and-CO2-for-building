# Prediction-besoins-energie-des-batiments

cd C:\Users\Dev\Desktop\OpenClassrooms\Project6\Energy Co2\Predict-Energy-and-CO2-for-building\API
set BENTOML_HOME=C:\Users\Dev\Desktop\OpenClassrooms\Project6\Energy Co2\Predict-Energy-and-CO2-for-building\bentoml_store\

bentoml serve service.py:svc

bentoml build
"""
Successfully built Bento(tag="xgb_prediction_service:myu7qlqbsoyswaaz").
"""
Keep the tag for next step

bentoml serve xgb_prediction_service:myu7qlqbsoyswaaz
#To test if the bento build went well

bentoml containerize xgb_prediction_service:myu7qlqbsoyswaaz --debug

docker run --rm -p 3000:3000 xgb_prediction_service:myu7qlqbsoyswaaz


docker tag xgb_prediction_service:myu7qlqbsoyswaaz europe-west1-docker.pkg.dev/exalted-cell-452502-u7/my-repo/xgb_prediction_service

docker push europe-west1-docker.pkg.dev/exalted-cell-452502-u7/my-repo/xgb_prediction_service







docker tag xgb_prediction_service:myu7qlqbsoyswaaz 985539791615.dkr.ecr.eu-north-1.amazonaws.com/openclassroom/xgb_prediction_service:myu7qlqbsoyswaaz

aws ecr create-repository --repository-name openclassroom/xgb_prediction_service --region eu-north-1

aws ecr get-login-password --region eu-north-1 | docker login --username AWS --password-stdin 985539791615.dkr.ecr.eu-north-1.amazonaws.com

docker tag xgb_prediction_service:myu7qlqbsoyswaaz 985539791615.dkr.ecr.eu-north-1.amazonaws.com/openclassroom/xgb_prediction_service:myu7qlqbsoyswaaz

docker push 985539791615.dkr.ecr.eu-north-1.amazonaws.com/openclassroom/xgb_prediction_service:myu7qlqbsoyswaaz
