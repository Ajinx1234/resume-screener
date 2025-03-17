from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def rank_resume(resume_text, job_description):
    """Calculates similarity score between resume & job description."""
    documents = [resume_text, job_description]

    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(documents)

    score = cosine_similarity(tfidf_matrix[0], tfidf_matrix[1])[0][0] * 100
    return round(score, 2)
