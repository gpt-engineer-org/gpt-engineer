import streamlit as st

# Title
st.title("LLM Answer Engine Demo")

# Description
st.write("This is a simple demo app to test your LLM Answer Engine.")

# User input
user_input = st.text_input("Enter your question:")

# Button to submit
if st.button("Get Answer"):
    if user_input.strip() == "":
        st.warning("Please enter a question first.")
    else:
        # Here you would integrate your LLM / backend logic
        st.success(f"Your question: '{user_input}' was received!")
        st.info("This is where your AI-generated answer would appear.")