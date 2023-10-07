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
    bucket = "timothy-aihackathon-data"

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
