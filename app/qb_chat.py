import time
import streamlit as st
import qb_datastores
import qb_config
from qb_helpers import print_query_results_df
import uuid
import qb_auth_utils
import jwt

# Init configuration
config = qb_auth_utils.retrieve_config_from_agent()
AMAZON_Q_APP_ID = config['AmazonQAppId']
ATHENA_DB_NAME = config["AthenaDbName"]
ATHENA_S3_LOC = config["AthenaS3Loc"]
# create Streamlit app
st.title('Data-Insights-with-Q-Business')
st.sidebar.title('Data Insights with Amazon Q Business')
st.caption('Query your structured data. Powered by :orange[Amazon Q Business]')
options = ["Athena(CUR Data)", "Placeholder A", "Placeholder B"]
# LLM Options
selector = st.sidebar.selectbox("Which datastore do you want to query?", options, index=0)
st.sidebar.divider()


def _submit_feedback(state):
    """
    Submits feedback for the relevant message.
    :return: None.
    :rtype: None.
    """
    st.toast(f""" :orange[FEEDBACK RECORDED: ] {st.session_state.fb_k} """)
    st.chat_message("user").write(f""" :orange[FEEDBACK RECORDED: ] {st.session_state.fb_k} """)
    # write feedback to csv file
    with open('app/feedback/feedback.csv', 'a', encoding='utf-8') as f:
        f.write(
            f"{st.session_state.fb_k},{question},{answer},{state}\n")
        f.close()
        st.session_state.fb_k = ""
    return


def athena_query_execution(query_exec_id, st_obj):
    """
    Waits for the query to finish and prints the results.
    :param query_exec_id: The ID of the query execution.
    :type query_exec_id: str
    :param st_obj: The Streamlit object to write the results to.
    :type st_obj: streamlit.Streamlit
    :return: None.
    :rtype: None.
    """
    while True:
        response = qb_datastores.athena.get_query_execution(QueryExecutionId=st_query_execution_id)
        # print("Query state is: " + response['QueryExecution']['Status']['State'])
        st.write(f""" :blue[Query state is:] {response['QueryExecution']['Status']['State']} """)
        state = response['QueryExecution']['Status']['State']
        if state == 'SUCCEEDED':
            return
        elif state == 'FAILED':
            st.write(f""" :red[Query error is:] {response['QueryExecution']['Status']['StateChangeReason']} """)
            return
        else:
            time.sleep(5)


def clear_chat_history():
    """
     Clears the questions, answers, input, and chat history from the session state.
     :return: None
     """
    st.session_state.messages = [
        {"role": "assistant", "content": "What questions do you have about your structured data?"}]


st.sidebar.button('Clear Chat History', type="primary", on_click=clear_chat_history)

# Create an Amazon Q client
#q_client = boto3.client('qbusiness')


def ask_question_with_attachment(prompt, filename=None, schema=None, services=None, access_token=None):
    """
    Sends a question to Q and returns the answer.
    :param prompt: The prompt to send to Q.
    :type prompt: str
    :param filename: The name of the file to attach to the question.
    :type filename: str
    :param services: The name of the file to attach to the question.
    :type services: str
    :return: The answer from Q.
    :rtype: str
    """
    q_client=qb_auth_utils.get_qclient(access_token)
    if services is None:
        if filename is None:
            qb_answer = q_client.chat_sync(
                applicationId=AMAZON_Q_APP_ID,
                userMessage=prompt,
                attachments=[
                    {
                        'data': schema,
                        'name': 'sample'
                    }
                ],
            )
        else:
            with open(filename, 'rb') as data:
                qb_answer = q_client.chat_sync(
                    applicationId=AMAZON_Q_APP_ID,
                    userMessage=prompt,
                    attachments=[
                        {
                            'data': data.read(),
                            'name': filename
                        }
                    ],
                )
        return qb_answer['systemMessage']
    else:
        with open(filename, 'rb') as data:
            with open(services, 'rb') as service_mappings:
                qb_answer = q_client.chat_sync(
                    applicationId=AMAZON_Q_APP_ID,
                    userMessage=prompt,
                    attachments=[
                        {
                            'data': data.read(),
                            'name': filename
                        },
                        {
                            'data': service_mappings.read(),
                            'name': services
                        }
                    ],
                )
    return qb_answer['systemMessage']

oauth2 = qb_auth_utils.configure_oauth_component()
if 'token' not in st.session_state:
    # If not, show authorize button
    redirect_uri = f"https://{qb_auth_utils.OAUTH_CONFIG['ExternalDns']}/component/streamlit_oauth.authorize_button/index.html"
    result = oauth2.authorize_button("Connect with Cognito",scope='openid', pkce='S256', redirect_uri=redirect_uri)
    if result and 'token' in result:
        # If authorization successful, save token in session state
        st.session_state.token = result.get('token')
        st.experimental_rerun()
else:
    # If token exists in session state, show the token
    token = st.session_state['token']
    user_email = jwt.decode(token['id_token'], options={"verify_signature": False})['email']
    if st.button("Refresh Token"):
        # If refresh token button is clicked, refresh the token
        token = oauth2.refresh_token(token)
        st.session_state.token = token
        st.experimental_rerun()
    col1, col2 = st.columns([1,1])

    st.write('Welcome: ', user_email)

    if "access_token" not in st.session_state:
        st.session_state['access_token'] = qb_auth_utils.get_iam_oidc_token(token['id_token'])['idToken']
    # configuring values for session state
    if "messages" not in st.session_state:
        st.session_state.messages = []
    # Check if the user ID is already stored in the session state
    if 'user_id' in st.session_state:
        user_id = st.session_state['user_id']

    # If the user ID is not yet stored in the session state, generate a random UUID
    else:
        user_id = str(uuid.uuid4())
        st.session_state['user_id'] = user_id

    if 'conversationId' not in st.session_state:
        st.session_state['conversationId'] = ''

    if 'parentMessageId' not in st.session_state:
        st.session_state['parentMessageId'] = ''

    if 'chat_history' not in st.session_state:
        st.session_state['chat_history'] = []

    if "questions" not in st.session_state:
        st.session_state.questions = []

    if "answers" not in st.session_state:
        st.session_state.answers = []

    if "input" not in st.session_state:
        st.session_state.input = ""
    # writing the message that is stored in session state
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if selector == options[0]:
        if question := st.chat_input("What questions do you have about your billing data?"):
            # with the user icon, write the question to the front end
            with st.chat_message("user"):
                st.markdown(question)
            # append the question and the role (user) as a message to the session state
            st.session_state.messages.append({"role": "user",
                                              "content": question})
            # respond as the assistant with the answer
            with st.chat_message("assistant"):
                # making sure there are no messages present when generating the answer
                message_placeholder = st.empty()
                # putting a spinning icon to show that the query is in progress
                with st.status("Getting answer...", expanded=True) as status:
                    # passing the question into the ask_question_with_attachment function, which invokes Q
                    answer = ask_question_with_attachment(qb_config.prompt_cur['cur_prompt_builder'] + question,
                                                          qb_config.schemas['cur_schema'],None,
                                                          qb_config.schemas['service_mappings'],st.session_state['access_token'])
                    # if answer is not "Sorry, I could not find relevant information to complete your request." end
                    if answer == "Sorry, I could not find relevant information to complete your request.":
                        st.write(f""" :red[Sorry, I could not find relevant information to complete your request.] """)
                        status.update(label="Error returning data", state="complete", expanded=True)
                    elif answer == "I do not know about this. Please fix your input.":
                        st.write(f""" :red[Sorry, I don't know about this. Please fix your input!] """)
                        status.update(label="Invalid Query", state="complete", expanded=True)
                    else:
                        # writing prompt used to front end
                        st.session_state["answer"] = answer
                        st.session_state["question"] = question
                        st.write(f""" :green[Prompt entered:] """)
                        st.write(f""" {qb_config.prompt_cur['cur_prompt_builder'] + question} """)
                        st.write(f""" :blue[Response from Q:] """)
                        st.code(answer, language="sql")
                        st.write(f""" :gray[Sending to Athena for execution...] """)
                        st_athena_response = qb_datastores.send_query(answer, ATHENA_DB_NAME, ATHENA_S3_LOC)
                        if st_athena_response:
                            st_query_execution_id = st_athena_response['QueryExecutionId']
                            st.markdown("Query Execution Id: " + st_query_execution_id)
                            athena_query_execution(st_query_execution_id, st)
                            st_query_results = qb_datastores.get_query_results(st_query_execution_id)
                            # convert athena results to
                            if st_query_results:
                                df = print_query_results_df(st_query_results)
                                tab_titles=["Data","Description"]
                                tabs=st.tabs(tab_titles)
                                with tabs[0]:
                                    st.write(f""" :green[Results:] """)
                                    st.dataframe(df, hide_index=True)
                                with tabs[1]:
                                    q_response=ask_question_with_attachment(qb_config.prompt_txt['txt_prompt_builder'],None,df.to_string(),None,st.session_state['access_token'])
                                    print(q_response)
                                    escaped_q_response = q_response.replace("$", r"\$")
                                    st.write(f""" :green[Summary:] """)
                                    st.write(f""" {escaped_q_response} """)
                                col1, col2 = st.columns([1, 12])
                                with st.form('buttons'):
                                    feedback_key = str(uuid.uuid4())
                                    st.session_state["fb_k"] = f"{feedback_key}"
                                    with col1:
                                        st.button('👍', on_click=_submit_feedback, args=['positive'])

                                    with col2:
                                        st.button('👎', on_click=_submit_feedback, args=['negative'])
                            else:
                                st.write(f""" :red[Verify your input. No valid query could be created.] """)
                        # showing a completion message to the front end
                        else:
                            st.write(f""" :red[Hi! I need your help to steer me in the right direction. Try to modify your prompt. Sorry, No valid query could be created.] """)
                        status.update(label="Results returned...", state="complete", expanded=True)

                        # appending the results to the session state
                        st.session_state.messages.append({"role": "assistant", "content": answer})