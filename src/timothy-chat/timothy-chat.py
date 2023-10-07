import json
import boto3
import urllib.parse


def lambda_handler(event, context):
    print("Event Body:")
    print(json.dumps(event["body"]))

    # Get prompt text string from event
    print("Decoded Body")
    requestBody = urllib.parse.unquote(event["body"])
    print(requestBody)
    prompt = requestBody.replace("prompt=", "")
    print(prompt)

    # Create S3 client and build request body.
    s3 = boto3.client(service_name="s3")

    # Set the region where your S3 bucket is located
    # s3.meta.region_name = "us-east-2"

    # Set the name of your S3 bucket and object
    bucket_name = "timothy-aihackathon-data"
    object_key = "json-questions/questions.json"

    # Get the S3 object
    obj = s3.get_object(Bucket=bucket_name, Key=object_key)

    # Load the S3 object into a JSON object
    json_object = json.loads(obj.get()["Body"].read())

    print(json.dumps(json_object))

    # If prompt is empty, return with an error
    if len(prompt) == 0:
        return {"statusCode": 200, "body": "Please enter your question and try again"}

    # print(answer)

    # Check answer or set response if no answer
    # if len(answer) == 0:
    # answer = "Unable to answer your question at this time.  Please try again later or ask another question."

    # Return anser to user.
    answer = "End Test"
    return {"statusCode": 200, "body": json.dumps(answer)}
