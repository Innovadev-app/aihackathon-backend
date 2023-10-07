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

    # If prompt is empty, return with an error
    if len(prompt) == 0:
        return {"statusCode": 200, "body": "Please enter your question and try again"}

    # Create BedRock client and build request body.
    bedrock = boto3.client(service_name="bedrock-runtime")
    body = json.dumps(
        {"prompt": prompt, "maxTokens": 500, "temperature": 0.8, "topP": 1.0}
    )

    # Set Model ID to AI21 Labs Jurrasic Ultra and content types
    modelId = "ai21.j2-ultra-v1"
    accept = "application/json"
    contentType = "application/json"

    # Sent request and get response from BedRock
    response = bedrock.invoke_model(
        body=body, modelId=modelId, accept=accept, contentType=contentType
    )

    # Load the body from the response object
    response_body = json.loads(response.get("body").read())

    # Get and log the answer
    answer = response_body.get("completions")[0].get("data").get("text")
    print(answer)

    # Check answer or set response if no answer
    if len(answer) == 0:
        answer = "Unable to answer your question at this time.  Please try again later or ask another question."

    # Return anser to user.
    return {"statusCode": 200, "body": json.dumps(answer)}
