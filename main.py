import streamlit as st
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from anthropic import Anthropic

st.title("Chatbot Interviewer")
st.write("This chatbot will interview you and generate a compelling story based on your responses.")

# Anthropic API key and email credentials (stored as Streamlit secrets)
anthropic_api_key = st.secrets["ANTHROPIC_API_KEY"]
email_user = st.secrets["EMAIL_USER"]
email_password = st.secrets["EMAIL_PASSWORD"]
email_server = st.secrets["EMAIL_SERVER"]
email_port = st.secrets["EMAIL_PORT"]

# Validate static values immediately after they're defined
assert isinstance(anthropic_api_key, str), "API key must be a string"
assert isinstance(email_user, str), "Email user must be a string"
# Assertions for email_password, email_server, and email_port could be added here as needed

# Initialize Anthropic client
client = Anthropic(api_key=anthropic_api_key)

# Initialize 'messages' in session_state if it doesn't exist
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello! I'm here to interview you. Let's start!"}
    ]

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("What would you like to share?"):
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)

    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        # Stream the response from Anthropic API
        response_text = ""
        try:
            for data in client.messages.stream(
                model="claude-3-opus-20240229",
                max_tokens=1000,
                temperature=1,
                messages=st.session_state.messages,
            ):
                response_text += data.content[0].text
                st.markdown(response_text)
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")

    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response_text})

# Function to send email with transcript and generated story
def send_email(transcript, story, recipient):
    msg = MIMEMultipart()
    msg["From"] = email_user
    msg["To"] = recipient
    msg["Subject"] = "Chatbot Interview Transcript and Story"
    msg.attach(MIMEText(f"Interview Transcript:\n\n{transcript}\n\nGenerated Story:\n\n{story}"))
    server = smtplib.SMTP(email_server, email_port)
    server.starttls()
    server.login(email_user, email_password)
    server.send_message(msg)
    server.quit()