from GraphRAG import GraphRAG
import streamlit as st
import pyperclip

api_key = st.secrets["API_KEY"]

RAG = GraphRAG('my_database.db', 'kb.txt', api_key)

st.info("This app is in testing.")

def get_answer(question):
    gpt_response = RAG.get_gpt_response(question)
    # print("GPT Response : " + gpt_response)
    relevant_relations = RAG.convert_gpt_response_to_list(gpt_response)

    if relevant_relations:
        question_entity = RAG.get_question_entity(question)
        # print("Question Entity : " + question_entity)
        if question_entity:
            answers = RAG.extract_answers(question_entity, relevant_relations)
            if answers:
                return answers
            else:
                return "The model was unable to retrieve any answers. 🥲 There was a possible error in extracting answers from the KG."
        else:
            return "The model was unable to retrieve any answers. 🥲 There was a possible error in extracting entity from question"
    else:
        return "The model was unable to retrieve any answers. 🥲 There was a possible error in API response format"


input = "Write your question here..."
with st.sidebar:
    st.title(r"$\textsf{\Large 🤗💬 GraphQLM}$")
    # r"$\textsf{\🤗💬 Graph RAG<}$"
    # Define sidebar tabs
    tabs = ["Graph Structure", "Sample Questions"]
    # Create sidebar with tabs
    selected_tab = st.sidebar.selectbox("Select Tab", tabs)

    # Define content for each tab
    if selected_tab == "Graph Structure":
        # Display image of the graph structure
        st.sidebar.image("structure.jpg", use_column_width=True)

    elif selected_tab == "Sample Questions":
        # Define sub-tabs for sample questions
        sample_tabs = ["1-hop", "2-hop", "3-hop"]
        # selected_sample_tab = st.sidebar.selectbox(
        #     "Select Sample Question Type", sample_tabs)

        # Define sample questions for each sub-tab
        sample_questions = {
            "1-hop": ["what films did [Shahid Kapoor] act in?", "who starred in [Edge of Tomorrow]", "what is the genre for [The Avengers]"],
            "2-hop": ["who acted together with [Brad Pitt]", "the movies written by [Kundan Shah] starred who", "the screenwriter of [Titanic] also wrote which films"],
            "3-hop": ["what languages are the films that share writers with [The Godfather] in", "the films that share directors with the film [Champion] were in which genres", "who are the directors of the films written by the writer of [The Dark Knight]"]
        }

        # Define sub-tabs for sample question types
        selected_sample_type = st.sidebar.selectbox(
            "Select Question Type", ["1-hop", "2-hop", "3-hop"])
        # Display selected list of questions in main area
        if selected_sample_type:
            st.write("Here are a few sample questions that you can copy:")
            for question in sample_questions[selected_sample_type]:
                st.text_area("", question, height=40)
    

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Ask me any questions from MetaQA Knowledge Graph!"}]

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# React to user input
if prompt := st.chat_input("Write your question here..."):
    # Display user message in chat message container
    st.chat_message("user").markdown(prompt)
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    if prompt.count('[') != 1 and prompt.count(']') != 1:
        error_message = "Please include the primary entity of the question in square brackets, like [entity]."
        # Display error message in chat message container
        with st.chat_message("error"):
            st.markdown(error_message)
        # Add error message to chat history
        st.session_state.messages.append(
            {"role": "error", "content": error_message})
    else:
        answer = get_answer(prompt)

        if type(answer) == list:
            if len(answer) == 0:
                response = "The model was unable to retrieve any answers. 🥲"
            else:
                response = f"Following is the list of answers retrieved: {answer}"
        else:
            response = answer
        # Display assistant response in chat message container
        with st.chat_message("assistant"):
            st.markdown(response)
        # Add assistant response to chat history
        st.session_state.messages.append(
            {"role": "assistant", "content": response})
