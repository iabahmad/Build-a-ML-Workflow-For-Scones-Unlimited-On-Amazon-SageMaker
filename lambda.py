############# serialize ################################
import json
import boto3
import base64

s3 = boto3.client('s3')

def lambda_handler(event, context):
    """A function to serialize target data from S3"""

    # Get the s3 address from the Step Function event input
    key = event['s3_key']
    bucket = event["s3_bucket"]
    

    # Download the data from s3 to /tmp/image.png
    ## TODO: fill in
    boto3.resource('s3').Bucket(bucket).download_file(key, "/tmp/image.png")

    # We read the data from a file
    with open("/tmp/image.png", "rb") as f:
        image_data = base64.b64encode(f.read())

    # Pass the data back to the Step Function
    print("Event:", event.keys())
    return {
        'statusCode': 200,
        'body': {
            "image_data": image_data,
            "s3_bucket": bucket,
            "s3_key": key,
            "inferences": []
        }
    }

###########################################################################

######################## classify #######################################

import json
#import sagemaker
import boto3

import base64
#from sagemaker.serializers import IdentitySerializer
#from sagemaker import rpds

# Fill this in with the name of your deployed model
ENDPOINT = 'image-classification-2023-09-11-07-31-02-778'
client_runtime = boto3.client('sagemaker-runtime')

def lambda_handler(event, context):

    # Decode the image data
    image = base64.b64decode(event['body']["image_data"])

    # Make a prediction:
    inferences = client_runtime.invoke_endpoint(EndpointName=ENDPOINT, Body=image, ContentType='image/png')
    
    # We return the data back to the Step Function    
    event['body']["inferences"] = json.loads(inferences['Body'].read().decode('utf-8'))

    return {
        'body': event
        
    }

########################################################################################################
############################## inference #############################################################
import json

THRESHOLD = 0.7

def lambda_handler(event, context):

    # Grab the inferences from the event
    inferences = event['body']['body']['inferences']
    print(inferences)

    # Check if any values in our inferences are above THRESHOLD
    meets_threshold = (max(inferences) > THRESHOLD)

    if meets_threshold:
        pass
    else:
        raise("THRESHOLD_CONFIDENCE_NOT_MET")

    return {
        'statusCode': 200,
        'body': event
    }
########################################################################################################
