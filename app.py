# Research Paper Code Finder -- Powered by Metaphor
# Author: Sreenidhi Iyengar Munimadugu
# email: munimadu [at] usc.edu

import streamlit as st
from metaphor_python import Metaphor
import openai
from googlesearch import search
from paperswithcode import PapersWithCodeClient
import requests
import pandas as pd

# Set up API keys
openai.api_key = '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'
metaphor = Metaphor('9520bf76-9c02-4019-9a49-bd804e1d9b32')

def search_papers(topic):
    search_response = metaphor.search(
        query=f"research papers on {topic}",
        exclude_domains=['github.com'],
        use_autoprompt=True,
    )
    return search_response.results[:10]


def summarize_paper(paper_title, paper_url):
    SYSTEM_MESSAGE = "You are a helpful assistant that summarizes the content of a research paper. Summarize the users input."
    user_message = f"Title: {paper_title}\nURL: {paper_url}"
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": SYSTEM_MESSAGE},
            {"role": "user", "content": user_message},
        ],
    )
    summary = completion.choices[0].message.content
    return summary

def search_code_metaphor(paper_title):
    search_response = metaphor.search(query=f"{paper_title} code implementation")
    return search_response.results[:10]  # Return top 10 results

def display_code_implementations(paper_title):
    code_implementations = search_code_metaphor(paper_title)
    if code_implementations:
        data = {
            "Title": [result.title for result in code_implementations],
            "URL": [result.url for result in code_implementations]
        }
        df = pd.DataFrame(data)
        st.table(df)
    else:
        st.write("No code implementations found.")

def generate_code_idea(paper_summary):
    SYSTEM_MESSAGE = "You are a code generator assistant. Based on the provided summary of a research paper, generate a code idea."
    completion_response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": SYSTEM_MESSAGE},
            {"role": "user", "content": paper_summary},
        ]
    )
    code_idea = completion_response.choices[0].message['content']
    return code_idea  

def extract_important_components(paper_summary):
    SYSTEM_MESSAGE = "You are a knowledgeable assistant who provides important considerations for implementing a given research paper. Provide key points to keep in mind based on the summary provided."
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": SYSTEM_MESSAGE},
            {"role": "user", "content": paper_summary},
        ],
    )
    considerations = completion.choices[0].message.content
    return considerations

def main():
    # Streamlit UI
    st.title("Research Paper to Code")
    topic = st.text_input("Enter a research topic:", "Glaucoma Fundus Deep Learning")

    if st.button("Search"):
        st.session_state.papers = search_papers(topic)
        st.session_state.paper_selection = None  # Reset paper_selection on a new search

    if st.session_state.get('papers', None):
        paper_titles = [f"{i+1}. {paper.title}" for i, paper in enumerate(st.session_state.papers)]
        st.write("Top 10 papers found:")
        st.write("\n".join(paper_titles))
        paper_selection = st.text_input("Enter the number of the paper you want to select (1-10):")

        if st.button("Select Paper"):
            st.session_state.paper_selection = int(paper_selection) - 1
            selected_paper = st.session_state.papers[st.session_state.paper_selection]
            st.write(f"Selected Paper: {selected_paper.title}")
            display_code_implementations(selected_paper.title)  
            summary = summarize_paper(selected_paper.title, selected_paper.url)
            st.write(f"Summary: {summary}")

        if st.button("Generate Code idea from Paper Summary"):
            summary = summarize_paper(st.session_state.papers[st.session_state.paper_selection].title,
                                      st.session_state.papers[st.session_state.paper_selection].url)  # Use the selected paper info from session_state
            with st.spinner('Generating code idea...'):
                code_idea = generate_code_idea(summary)
            st.write(f"Generated Code Idea:\n{code_idea}")
            with st.spinner('Extracting important components...'):
                components = extract_important_components(summary)
            st.write(f"Important components needed to code the paper: {components}")

    else:
        st.write("No papers found.")

if __name__ == '__main__':
    if 'papers' not in st.session_state:
        st.session_state.papers = None
    if 'paper_selection' not in st.session_state:
        st.session_state.paper_selection = None
    main()
