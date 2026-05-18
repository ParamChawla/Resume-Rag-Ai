from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

from langchain_google_genai import ChatGoogleGenerativeAI

from dotenv import load_dotenv

import os

load_dotenv()

# =========================================
# CONFIG
# =========================================

CHROMA_PATH = "chromadb"

embedding_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

llm = ChatGoogleGenerativeAI(
    model="models/gemini-flash-latest",
    google_api_key=os.getenv("GEMINI_API_KEY")
)

# =========================================
# PROCESS RESUME
# =========================================

def process_resume(pdf_path):

    # DELETE OLD CHROMADB

    if os.path.exists(CHROMA_PATH):

        import shutil

        shutil.rmtree(CHROMA_PATH)

    loader = PyPDFLoader(pdf_path)

    documents = loader.load()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )

    chunks = splitter.split_documents(documents)

    vectordb = Chroma.from_documents(
        documents=chunks,
        embedding=embedding_model,
        persist_directory=CHROMA_PATH
    )

    return vectordb

# =========================================
# GET RETRIEVER
# =========================================

def get_retriever():

    vectordb = Chroma(
        persist_directory=CHROMA_PATH,
        embedding_function=embedding_model
    )

    return vectordb.as_retriever(
        search_kwargs={"k": 10}
    )

# =========================================
# EXTRACT FULL RESUME TEXT
# =========================================

def get_full_resume_text():

    retriever = get_retriever()

    docs = retriever.invoke(
        "skills projects experience education technologies achievements"
    )

    context = "\n\n".join(
        [doc.page_content for doc in docs]
    )

    return context

# =========================================
# AI CHAT
# =========================================

def ask_question(query):

    retriever = get_retriever()

    docs = retriever.invoke(query)

    context = "\n\n".join(
        [doc.page_content for doc in docs]
    )

    prompt = f"""
    You are an expert AI Resume Analyzer.

    Your tasks:
    - Analyze resumes professionally
    - Give concise responses
    - Use markdown formatting
    - Use bullet points
    - Highlight strengths
    - Mention missing skills if relevant
    - Be ATS-aware
    - Sound professional and recruiter-friendly

    Resume Context:
    {context}

    Question:
    {query}
    """

    response = llm.invoke(prompt)

    clean_response = response.content

    if isinstance(clean_response, list):

        first_item = clean_response[0]

        if isinstance(first_item, dict):

            clean_response = first_item.get(
                "text",
                str(first_item)
            )

        else:

            clean_response = str(first_item)

    return str(clean_response)

# =========================================
# RULE-BASED ATS SCORE
# =========================================

def real_ats_score(resume_text):

    score = 0

    strengths = []

    missing = []

    resume_text = resume_text.lower()

    # =========================================
    # TECH SKILLS
    # =========================================

    tech_skills = [
        "python",
        "javascript",
        "react",
        "node",
        "machine learning",
        "ai",
        "sql",
        "mongodb",
        "fastapi",
        "django",
        "express",
        "html",
        "css",
        "tailwind",
        "git",
        "github"
    ]

    matched_skills = 0

    for skill in tech_skills:

        if skill in resume_text:

            matched_skills += 1

    skills_score = (
        matched_skills / len(tech_skills)
    ) * 30

    score += skills_score

    if matched_skills >= 5:

        strengths.append(
            "Strong technical skillset detected"
        )

    # =========================================
    # PROJECTS
    # =========================================

    if "project" in resume_text:

        score += 15

        strengths.append(
            "Projects section present"
        )

    else:

        missing.append(
            "Add projects section"
        )

    # =========================================
    # EXPERIENCE
    # =========================================

    if (
        "internship" in resume_text
        or "experience" in resume_text
    ):

        score += 20

        strengths.append(
            "Internship/experience present"
        )

    else:

        missing.append(
            "Add experience section"
        )

    # =========================================
    # EDUCATION
    # =========================================

    if (
        "b.tech" in resume_text
        or "bachelor" in resume_text
    ):

        score += 10

        strengths.append(
            "Education details present"
        )

    # =========================================
    # AI / ML
    # =========================================

    aiml_keywords = [
        "machine learning",
        "artificial intelligence",
        "tensorflow",
        "pytorch",
        "deep learning",
        "ai/ml",
        "nlp"
    ]

    matched_ai = 0

    for keyword in aiml_keywords:

        if keyword in resume_text:

            matched_ai += 1

    if matched_ai >= 1:

        score += 10

        strengths.append(
            "AI/ML knowledge detected"
        )

    # =========================================
    # FULL STACK
    # =========================================

    fullstack_keywords = [
        "react",
        "node",
        "express",
        "mongodb",
        "full stack",
        "mern",
        "api"
    ]

    matched_fullstack = 0

    for keyword in fullstack_keywords:

        if keyword in resume_text:

            matched_fullstack += 1

    if matched_fullstack >= 3:

        score += 10

        strengths.append(
            "Full-stack development skills present"
        )

    # =========================================
    # RESUME LENGTH
    # =========================================

    if len(resume_text) > 1500:

        score += 5

        strengths.append(
            "Good resume content length"
        )

    else:

        missing.append(
            "Resume content too short"
        )

    # =========================================
    # LIMIT SCORE
    # =========================================

    if score > 100:
        score = 100

    return {
        "score": round(score),
        "strengths": strengths,
        "missing": missing
    }

# =========================================
# ATS ANALYSIS
# =========================================

def calculate_ats_score():

    context = get_full_resume_text()

    ats_data = real_ats_score(context)

    prompt = f"""
    You are an expert ATS evaluator.

    ATS Score:
    {ats_data['score']}/100

    Strengths:
    {ats_data['strengths']}

    Missing:
    {ats_data['missing']}

    Explain this ATS evaluation professionally.

    Include:
    - Resume strengths
    - Missing keywords
    - Improvements
    - Hiring chances
    - ATS optimization tips

    Use markdown formatting.
    """

    response = llm.invoke(prompt)

    clean_response = response.content

    if isinstance(clean_response, list):

        first_item = clean_response[0]

        if isinstance(first_item, dict):

            clean_response = first_item.get(
                "text",
                str(first_item)
            )

        else:

            clean_response = str(first_item)

    return f"""
# ATS Score: {ats_data['score']}/100

{str(clean_response)}
"""