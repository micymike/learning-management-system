import streamlit as st
import os
import replicate
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()
from utils import debounce_replicate_run

REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN")
REPLICATE_MODEL_ENDPOINTS = {
    'LLaMA2-7B': os.getenv('REPLICATE_MODEL_ENDPOINT7B', default=''),
    'LLaMA2-13B': os.getenv('REPLICATE_MODEL_ENDPOINT13B', default=''),
    'LLaMA2-70B': os.getenv('REPLICATE_MODEL_ENDPOINT70B', default='')
}


print("The API TOKEN IS",REPLICATE_API_TOKEN)
print("The MODEL ENDPOINTS ARE",REPLICATE_MODEL_ENDPOINTS)

# Set Pre-prompt
PRE_PROMPT = "You are a helpful assistant. You do not respond as 'User' or pretend to be 'User'. You only respond once as Assistant."

# Set initial page configuration
st.set_page_config(page_title="LLaMA2 Chatbot", page_icon=":left_speech_bubble:", layout="wide")

def render_app():
    # Set up containers
    response_container = st.container()
    container = st.container()

    # Set up Session State variables
    st.session_state.setdefault('chat_dialogue', [])
    st.session_state.setdefault('llm', REPLICATE_MODEL_ENDPOINTS['LLaMA2-70B'])
    st.session_state.setdefault('temperature', 0.1)
    st.session_state.setdefault('top_p', 0.9)
    st.session_state.setdefault('max_seq_len', 512)
    st.session_state.setdefault('pre_prompt', PRE_PROMPT)
    st.session_state.setdefault('string_dialogue', '')

    # Set up left sidebar
    st.sidebar.header("Blog Chatbot 💬")
   
     #container for the chat history
    response_container = st.container()
    #container for the user's text input
    container = st.container()
    #Set up/Initialize Session State variables:
    if 'chat_dialogue' not in st.session_state:
        st.session_state['chat_dialogue'] = []
    if 'llm' not in st.session_state:
        #st.session_state['llm'] = REPLICATE_MODEL_ENDPOINT13B
        st.session_state['llm'] = 'LLaMA2-70B'
    if 'temperature' not in st.session_state:
        st.session_state['temperature'] = 0.1
    if 'top_p' not in st.session_state:
        st.session_state['top_p'] = 0.9
    if 'max_seq_len' not in st.session_state:
        st.session_state['max_seq_len'] = 512
    if 'pre_prompt' not in st.session_state:
        st.session_state['pre_prompt'] = PRE_PROMPT
    if 'string_dialogue' not in st.session_state:
        st.session_state['string_dialogue'] = ''

    #Dropdown menu to select the model edpoint:
    selected_option = st.sidebar.selectbox('Choose a LLaMA2 model:', ['LLaMA2-70B', 'LLaMA2-13B', 'LLaMA2-7B'], key='model')
    if selected_option == 'LLaMA2-7B':
        st.session_state['llm'] = 'LLaMA2-7B'
    elif selected_option == 'LLaMA2-13B':
        st.session_state['llm'] = 'LLaMA2-13B'
    else:
        st.session_state['llm'] = 'LLaMA2-70B'
    #Model hyper parameters:
    st.session_state['temperature'] = st.sidebar.slider('Temperature:', min_value=0.01, max_value=5.0, value=0.1, step=0.01)
    st.session_state['top_p'] = st.sidebar.slider('Top P:', min_value=0.01, max_value=1.0, value=0.9, step=0.01)
    st.session_state['max_seq_len'] = st.sidebar.slider('Max Sequence Length:', min_value=64, max_value=4096, value=2048, step=8)

    NEW_P = st.sidebar.text_area('Prompt before the chat starts. Edit here if desired:', PRE_PROMPT, height=60)
    if NEW_P != PRE_PROMPT and NEW_P != "" and NEW_P != None:
        st.session_state['pre_prompt'] = NEW_P + "\n\n"
    else:
        st.session_state['pre_prompt'] = PRE_PROMPT

    btn_col1, btn_col2 = st.sidebar.columns(2)

     # Acknowledgment button
    if st.sidebar.button("Ack"):
        st.write("[Go back to the blogging app](https://bloggy-s8e5.onrender.com/)")

   
    # Display chat history
    for message in st.session_state.chat_dialogue:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # User input
    if prompt := st.chat_input("Ask a question here to LLaMA2"):
        st.session_state.chat_dialogue.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
       
        # Assistant response
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            string_dialogue = st.session_state['pre_prompt']
            for dict_message in st.session_state.chat_dialogue:
                speaker = "User" if dict_message["role"] == "user" else "Assistant"
                try:
                    string_dialogue += f"{speaker}: {dict_message['content']}\n\n"
                except KeyError:
                # Handle the case where 'content' key is missing (optional: log a message)
                    pass

            output = debounce_replicate_run(
                st.session_state['llm'],
                string_dialogue + "Assistant: ",
                st.session_state['max_seq_len'],
                st.session_state['temperature'],
                st.session_state['top_p'],
                REPLICATE_API_TOKEN,
                REPLICATE_MODEL_ENDPOINTS[st.session_state['llm']]
            )
            for item in output:
                full_response += item
                message_placeholder.markdown(full_response + "▌")
            message_placeholder.markdown(full_response)
        st.session_state.chat_dialogue.append({"role": "assistant", "content": full_response})

def main():
    render_app()

if __name__ == "__main__":
    main()

