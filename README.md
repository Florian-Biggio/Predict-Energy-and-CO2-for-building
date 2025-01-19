# Prediction-besoins-energie-des-batiments

cd C:\Users\Dev\Desktop\OpenClassroom\Projet6\Anticipez les besoins en consommation de bâtiments\Predict-Energy-and-CO2-for-building\API

bentoml serve service2.py:svc

bentoml build
"""
Successfully built Bento(tag="dummy_prediction_service:55wgbiwwc6vfbgc7").
"""
Keep the tag for next step

bentoml serve dummy_prediction_service:55wgbiwwc6vfbgc7
#To test if the bento build went well

bentoml containerize dummy_prediction_service:55wgbiwwc6vfbgc7 --debug

docker run --rm -p 3000:3000 dummy_prediction_service:55wgbiwwc6vfbgc7


docker tag dummy_prediction_service:55wgbiwwc6vfbgc7 985539791615.dkr.ecr.eu-north-1.amazonaws.com/openclassroom/dummy_prediction_service:55wgbiwwc6vfbgc7








aws ecr create-repository --repository-name openclassroom/dummy_prediction_service --region eu-north-1

aws ecr get-login-password --region eu-north-1 | docker login --username AWS --password-stdin 985539791615.dkr.ecr.eu-north-1.amazonaws.com

docker tag dummy_prediction_service:55wgbiwwc6vfbgc7 985539791615.dkr.ecr.eu-north-1.amazonaws.com/openclassroom/dummy_prediction_service:55wgbiwwc6vfbgc7

docker push 985539791615.dkr.ecr.eu-north-1.amazonaws.com/openclassroom/dummy_prediction_service:55wgbiwwc6vfbgc7
