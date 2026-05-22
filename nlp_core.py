import spacy
nlp = spacy.load("en_core_web_sm")

# This function uses spaCy to extract key topics from the input text. It looks for named entities and noun chunks, which are likely to represent important concepts in the syllabus or lectures.
def extract_topics(text: str) -> list[str]:
    """
    Extract key topics from the input text using spaCy's named entity recognition.
    Returns a list of unique entities that are likely to be important topics.

    Args:
        text: The input text to analyze.

    Returns:
        A list of unique topic strings.
    """
    
    doc = nlp(text)
    
    # Extract named entities as potential topics
    topics = set()
    for ent in doc.ents:
        if ent.label_ in {"PERSON", "ORG", "GPE", "EVENT", "WORK_OF_ART", "LANGUAGE"}:
            topics.add(ent.text.lower())
    
    # Extract noun chunks as potential topics (e.g. "gradient descent", "neural networks")
    for chunk in doc.noun_chunks:
        if not chunk.root.is_stop:
            topics.add(chunk.text.lower())

    return list(topics)

# For simplicity, this function just compares the sets of topics extracted from the syllabus and lectures.
def compute_gap(syllabus_topics: list[str], lecture_topics: list[str]) -> dict:
    """
    Compute the gap between syllabus topics and lecture topics.
    The gap is defined as the proportion of syllabus topics that are not covered in the lectures.

    Args:
        syllabus_topics: List of topics extracted from the syllabus.
        lecture_topics: List of topics extracted from the lectures.
    """
    s = set(syllabus_topics)
    l = set(lecture_topics)

    return {
        "missing": list(s - l),
        "covered": list(s & l),
        "overemphasized": list(l - s)
    }

if __name__ == "__main__":
    syllabus = "We will cover gradient descent, backpropagation, loss functions, and neural networks."
    lecture = "Today we discussed gradient descent, backpropagation, and PyTorch."

    s_topics = extract_topics(syllabus)
    l_topics = extract_topics(lecture)

    print("Syllabus topics:", s_topics)
    print("Lecture topics:", l_topics)
    print("Gap:", compute_gap(s_topics, l_topics))
