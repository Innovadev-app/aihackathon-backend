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

    query_result = ""

    # Check answer or set response if no answer
    if len(query_result) == 0:
        query_result = "Unable to answer your question at this time.  Please try again later or ask another question."

    # Return anser to user.
    return {"statusCode": 200, "body": json.dumps(query_result)}
