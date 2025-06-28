import base64
import boto3
import json
import os
import mlflow
import pandas as pd

kinesis_client = boto3.client('kinesis', region_name = 'ca-central-1')

PREDICTIONS_STREAM_NAME = os.getenv('PREDICTIONS_STREAM_NAME', 'ride_predictions')


model = mlflow.sklearn.load_model(model_uri=os.getenv('MODEL_URI'))

TEST_RUN = os.getenv('TEST_RUN', 'False') == 'True'

def predict(features):
    return float(model.predict(features))

def lambda_handler(event, context):

    
    predictions = []

    for record in event['Records']:
        encoded_data = record['kinesis']['data']
        decoded_data = base64.b64decode(encoded_data).decode('utf-8')
        
        ride_event = json.loads(decoded_data)
             
        ride = ride_event['ride']
        ride_id = ride_event['ride_id']

        ride_df = pd.DataFrame([ride])

        categorical_cols = ["PULocationID", "DOLocationID"]
        for col in categorical_cols:
            ride_df[col] = ride_df[col].astype(str)

        prediction = predict(ride_df)

        prediction_event = {
            'model': 'ride_duration_prediction_model',
            'version': '123',
            'prediction': {
                'ride_duration': prediction,
                'ride_id': ride_id
            }
        }

        if not TEST_RUN:
            kinesis_client.put_record(
                StreamName=PREDICTIONS_STREAM_NAME,
                Data=json.dumps(prediction_event),
                PartitionKey=str(ride_id)
            )
        

        predictions.append(prediction_event)

    

    # TODO implement
    return {
        'predictions': predictions
    }
