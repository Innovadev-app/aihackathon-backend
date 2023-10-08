import json
import boto3
import urllib.parse

# Load the AWS clients globally for reuse
# Load the Bedrock Client
bedrock = boto3.client(service_name="bedrock-runtime")
modelId = "ai21.j2-ultra-v1"
accept = "application/json"
contentType = "application/json"

# Load the Kendra Client
kendra = boto3.client("kendra")

# Provide the index ID
index_id = "0abb1751-862d-4add-bc36-74db23ff0560"

# Load the DynamoDB Client
dynamodb = boto3.client("dynamodb")


def saveRecommendation(classification, recommendation, question):
    item = {
        "Classification": {"S": classification},
        "ProfileID": {"S": "df078db0-ca6c-4187-b5f0-4cc3c7fbb2db"},
        "QuestionID": {"S": question},
        "Recommendation": {"S": recommendation},
    }
    print(item)
    response = dynamodb.put_item(TableName="TimothyRecommendationTable", Item=item)
    print("UPLOADING ITEM")
    print(response)


def bedrockInvoke(lengthIncrements, Temperature, topP, ans, prompt):
    maxTokens = int(lengthIncrements) * int(ans)
    temp = float(Temperature)
    topP = float(topP)
    body = json.dumps(
        {"prompt": prompt, "maxTokens": maxTokens, "temperature": temp, "topP": topP}
    )

    # Sent request and get response from BedRock
    response = bedrock.invoke_model(
        body=body, modelId=modelId, accept=accept, contentType=contentType
    )

    # Load the body from the response object
    response_body = json.loads(response.get("body").read())

    # Get and log the answer
    bedrockAnswer = response_body.get("completions")[0].get("data").get("text")
    # print(bedrockAnswer)
    return bedrockAnswer


def kendraSearch(query):
    response = kendra.query(QueryText=query, IndexId=index_id)

    print("\nSearch results for query: " + query + "\n")

    for query_result in response["ResultItems"]:
        print("-------------------")
        print("Type: " + str(query_result["Type"]))

        if (
            query_result["Type"] == "ANSWER"
            or query_result["Type"] == "QUESTION_ANSWER"
        ):
            answer_text = query_result["DocumentExcerpt"]["Text"]
            print(answer_text)

        if query_result["Type"] == "DOCUMENT":
            if "DocumentTitle" in query_result:
                document_title = query_result["DocumentTitle"]["Text"]
                print("Title: " + document_title)
            document_text = query_result["DocumentExcerpt"]["Text"]
            print(document_text)

        print("------------------\n\n")

    # Check answer or set response if no answer
    if len(query_result) == 0:
        query_result = "Unable to answer your question at this time.  Please try again later or ask another question."

    # Return anser to user.
    return json.dumps(query_result)


def lambda_handler(event, context):
    print("Event Body:")
    print(json.dumps(event["body"]))

    # Get prompt text string from event
    # requestBody = urllib.parse.unquote(event["body"])
    requestBody = event["body"]
    print(requestBody)
    # answers = requestBody.split("&")

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
    prompts = json_content["Prompts"]

    # If prompt is empty, return with an error
    if len(prompts) == 0:
        return {"statusCode": 200, "body": "Please enter your question and try again"}
    post = json.loads(requestBody)

    for answer in post:
        print(answer)
        quest = answer
        ans = post[answer]
        # print(quest)
        # print(answer)

        print(quest)
        prompt = prompts[quest]
        print(json.dumps(prompt))
        for ref in prompt:
            if ref == "Prayer" and prompt[ref]["Processor"] == "Bedrock":
                print("Search Bedrock for Prayer: " + prompt[ref]["Prompt"])
                bedrockAnswer = bedrockInvoke(
                    prompt[ref]["LengthIncrements"],
                    prompt[ref]["Temperature"],
                    prompt[ref]["TopP"],
                    ans,
                    prompt[ref]["Prompt"],
                )
                print(json.dumps(bedrockAnswer))
                saveRecommendation(ref, bedrockAnswer, quest)

            if ref == "Scripture" and prompt[ref]["Processor"] == "Bedrock":
                print("Search Bedrock for Scripture: " + prompt[ref]["Prompt"])
                bedrockAnswer = bedrockInvoke(
                    prompt[ref]["LengthIncrements"],
                    prompt[ref]["Temperature"],
                    prompt[ref]["TopP"],
                    ans,
                    prompt[ref]["Prompt"],
                )
                print(json.dumps(bedrockAnswer))
                saveRecommendation(ref, bedrockAnswer, quest)

            if ref == "Sermon" and prompt[ref]["Processor"] == "Kendra":
                print("Search Kendra for Sermon: " + prompt[ref]["Prompt"])
                kendraResponse = kendraSearch(prompt[ref]["Prompt"])
                print(kendraResponse)
                saveRecommendation(ref, kendraResponse, quest)

    # Return anser to user.
    answer = "End Test"
    return {"statusCode": 200, "body": "Completed Successfully"}
