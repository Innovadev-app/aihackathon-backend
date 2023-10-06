import json
import boto3


def lambda_handler(event, context):
    # TODO implement
    prompt = "I am a Christian and I am feeling guilty about my sins this morning.  What does the ESV bible say about how I seek God's forgiveness?"
    bedrock = boto3.client(service_name='bedrock-runtime')
    body = json.dumps({"prompt": prompt, "maxTokens": 500, "temperature": 0.8,"topP": 1.0})

    modelId = 'ai21.j2-ultra-v1'
    accept = 'application/json'
    contentType = 'application/json'
    
    response = bedrock.invoke_model(body=body, modelId=modelId, accept=accept, contentType=contentType)
    
    response_body = json.loads(response.get('body').read())
    
    # text
    answer = response_body.get("completions")[0].get("data").get("text")
    print(answer)
    return {
        'statusCode': 200,
        'body': json.dumps(answer)
    }
