import json
import boto3
import urllib.parse


def lambda_handler(event, context):
    print("Event Body:")
    print(json.dumps(event["body"]))

    # Get prompt text string from event
    # print("Decoded Body")
    # requestBody = urllib.parse.unquote(event["body"])
    # print(requestBody)

    query_result = {}

    dynamodb = boto3.client("dynamodb")
    tableName = "TimothyRecommendationTable"

    response = dynamodb.query(
        TableName=tableName,
        KeyConditionExpression="Classification = :classification",
        ExpressionAttributeValues={":classification": {"S": "Prayer"}},
    )
    print(response["Items"])
    query_result["Prayers"] = response["Items"]

    response = dynamodb.query(
        TableName=tableName,
        KeyConditionExpression="Classification = :classification",
        ExpressionAttributeValues={":classification": {"S": "Scripture"}},
    )
    print(response["Items"])
    query_result["Scripture"] = response["Items"]

    # Create S3 client and build request body.
    s3 = boto3.client(service_name="s3")

    # Set the name of your S3 bucket and object
    bucket_name = "timothy-aihackathon-data"
    object_key = "json-questions/questions.json"

    # Get the S3 object
    obj = s3.get_object(Bucket=bucket_name, Key=object_key)

    # Load the S3 object into a JSON object
    file_content = obj["Body"].read().decode("utf-8")
    json_content = json.loads(file_content)
    prompts = json_content["PromptQuestions"]

    responseObject = {}

    for prayer in query_result["Prayers"]:
        prayerQuestId = prayer["QuestionID"]["S"]
        responseObject[prayerQuestId] = {
            "Title": prompts[prayerQuestId],
            "Body": prayer["Recommendation"]["S"],
        }

    for scripture in query_result["Scripture"]:
        quest = scripture["QuestionID"]["S"]

        if len(responseObject[quest]) == 0:
            responseObject[quest] = {
                "Title": prompts[quest],
                "Body": scripture["Recommendation"]["S"],
            }
        else:
            responseObject[quest]["Body"] = (
                responseObject[quest]["Body"] + scripture["Recommendation"]["S"]
            )

    # print (json.dumps(responseObject))

    # Check answer or set response if no answer
    # if len(query_result) == 0:
    #     query_result = "Unable to answer your question at this time.  Please try again later or ask another question."

    print(json.dumps(responseObject))

    # Return anser to user.
    return {"statusCode": 200, "body": json.dumps(responseObject)}
