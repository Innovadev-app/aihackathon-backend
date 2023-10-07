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
    query = requestBody.replace("query=", "")
    print(query)

    # If prompt is empty, return with an error
    if len(query) == 0:
        return {"statusCode": 200, "body": "Please enter your question and try again"}

    kendra = boto3.client("kendra")

    # Provide the index ID
    index_id = "0abb1751-862d-4add-bc36-74db23ff0560"
    # Provide the query text
    query = "query text"

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
    return {"statusCode": 200, "body": json.dumps(query_result)}
