# List all objects related to Q Business applications
import boto3
from datetime import date

# Create an Amazon Q client
q_client = boto3.client('qbusiness','us-east-1')


# List Amazon Q Business applications
def list_applications():
    response = q_client.list_applications()
    for app in response['applications']:
        print("\n")
        print("ApplicationId: " + app['applicationId'])
        print("Display Name: " + app['displayName'])
        print("Application Status: " + app['status'])
        list_indices(app['applicationId'])
        list_retrievers(app['applicationId'])
    return response


# List Amazon Q Business Indices
def list_indices(application_id):
    response = q_client.list_indices(applicationId=application_id)
    for index in response['indices']:
        print("Index Id:", index['indexId'])
        print("Index Name:", index['displayName'])
        print("Index Status:", index['status'])
    return response


# List Amazon Q Business retrievers
def list_retrievers(application_id):
    response = q_client.list_retrievers(applicationId=application_id)
    for retriever in response['retrievers']:
        print("Retriever Id:", retriever['retrieverId'])
        print("Retriever Name:", retriever['displayName'])
        print("Retriever Status:", retriever['status'])
    return response


# List Amazon Q Business Conversations
def list_conversations(application_id, user_id):
    response = q_client.list_conversations(applicationId=application_id, userId=user_id)
    print(response)
    for conv in response['conversations']:
        print("Conversation Id:", conv['conversationId'])
        print("Conversation Title:", conv['title'])
        list_messages(application_id, conv['conversationId'], user_id)
        print("\n")
    return response


# List Amazon Q Business Messages
def list_messages(application_id, conversation_id, user_id):
    response = q_client.list_messages(applicationId=application_id, conversationId=conversation_id, userId=user_id)
    for message in response['messages']:
        print("Message Id:", message['messageId'])
        print("Message Body:", message['body'])
        print("Message Type: ", message['type'])
    return response


# print list of Q Objects
#list_q_objects = list_applications()


def current_date():
    today = date.today()
    # Format the date as Textual month, day and year
    date_today = today.strftime("%B %d, %Y")
    return date_today
