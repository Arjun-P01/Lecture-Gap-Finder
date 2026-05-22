import streamlit as st
import os
from parsers import parse_pdf_as_string, parse_transcript
from nlp_core import extract_topics, compute_gap
from gpt_analysis import get_gap_analysis


st.title("Lecture Gap Finder")
st.write("Upload your syllabus and lecture transcript to find what was skipped.")

syllabus_file = st.file_uploader("Upload Syllabus", type=["pdf"])
transcript_file = st.file_uploader("Upload Transcript", type=["pdf", "txt"])

if st.button("Find Gaps"):

    try:
        if syllabus_file and transcript_file:
            os.makedirs("tempDir", exist_ok=True)
        
            save_syllabus = os.path.join("tempDir", syllabus_file.name)
            save_transcript = os.path.join("tempDir", transcript_file.name)
        
            with open(save_syllabus, "wb") as f:
                f.write(syllabus_file.getbuffer())
        
            with open(save_transcript, "wb") as f:
                f.write(transcript_file.getbuffer())
        
            st.success("Files uploaded successfully.")

            with st.spinner("Analyzing gaps..."):
                syllabus_text = parse_pdf_as_string(save_syllabus)
                transcript_text = parse_transcript(save_transcript)
                syllabus_topics = extract_topics(syllabus_text)
                lecture_topics = extract_topics(transcript_text)
                gap = compute_gap(syllabus_topics, lecture_topics)
                analysis = get_gap_analysis(gap["missing"])

                for item in analysis:
                    if item["importance"] == "high":
                        color = "red"
                    elif item["importance"] == "mid":
                        color = "orange"
                    else:
                        color = "green"

                    st.markdown(f'<p style="color: {color}"><b>{item["topic"]}</b> - {item["importance"]}</p>', unsafe_allow_html=True)
                    st.write(item["explanation"])

        else:
            st.warning("Please upload both syllabus and transcript files.")

    except ValueError as e:
        st.error(f"Could not read file: {e}")
    except Exception as e:
        st.error(f"Something went wrong: {e}")