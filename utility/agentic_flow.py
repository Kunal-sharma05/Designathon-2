# agent_flow.py
from langchain_core.runnables import RunnableLambda
import faiss
import os
from langgraph.graph import StateGraph, START, END
from typing import TypedDict, List, Dict, Any
import numpy as np
from datetime import datetime
from dotenv import load_dotenv
import os
from utility.embeddings import get_embedding
from schema.JobDescription import JobDescriptionRequest
from schema.ConsultantProfile import ConsultantProfileSchema
from openai import AzureOpenAI
from model.Notification import Notification
from sqlalchemy.orm import Session
from typing import Any, List
load_dotenv()

api_key = os.getenv("openai_api_key")

# Initialize Azure OpenAI client
client = AzureOpenAI(
    api_version="2024-12-01-preview",  # Use the specified API version
    azure_endpoint="https://openai2525252.openai.azure.com/",  # Replace with your Azure OpenAI endpoint
    api_key=api_key  # Replace with your Azure OpenAI API key
)


# Define state for LangGraph
class MatchState(TypedDict):
    job_description: JobDescriptionRequest
    consultant_profiles: List[ConsultantProfileSchema]
    jd_text: str
    profile_embeddings: List[np.ndarray]
    ranked_profiles: List[Dict[str, Any]]
    top_matches: List[Dict[str, Any]]
    all_matches: List[Dict[str, Any]]


# --- Comparison Agent ---
def compare_profiles(state: MatchState) -> MatchState:
    """
    Generate FAISS embeddings for each consultant profile and compute distances to the job description.
    Returns similarity scores between JD and each profile.
    """
    try:
        # Concatenate JD fields into a single string
        jd = state["job_description"]
        jd_text = f"{jd.title} {jd.department or ''} {jd.location or ''} {jd.experience or ''} {jd.description or ''} " \
                  f"{', '.join(jd.skills) if jd.skills else ''}"
        state["jd_text"] = jd_text
        jd_embedding = get_embedding(jd_text)

        # Generate embeddings for all consultant profiles
        profile_embeddings = []
        for profile in state["consultant_profiles"]:
            profile_text = f"{profile.name} {', '.join(profile.skills) if profile.skills else ''} " \
                           f"{profile.experience or ''} {profile.location or ''}{profile.project or ''} {profile.availability or ''}"
            profile_embeddings.append(get_embedding(profile_text))
            print(profile_embeddings[-1])  # Debug: Print the last profile embedding
        state["profile_embeddings"] = profile_embeddings

        return state

    except Exception as e:
        print(f"⚠️ Error during comparison: {e}")
        return state


# --- Ranking Agent ---
def rank_profiles(state: MatchState) -> MatchState:
    """
    Ranks consultant profiles based on hybrid FAISS + LLM similarity score.
    """
    try:
        jd_embedding = get_embedding(state["jd_text"])
        profile_embeddings = np.array(state["profile_embeddings"], dtype='float32')
        faiss_index = faiss.IndexFlatL2(len(jd_embedding))
        faiss_index.add(profile_embeddings)

        # Search FAISS index
        D, I = faiss_index.search(np.array([jd_embedding], dtype='float32'), len(profile_embeddings))

        # Get LLM-based reranking
        profiles = state["consultant_profiles"]
        snippets = [
            f"{profiles[i].name}, Skills: {', '.join(profiles[i].skills)}, "
            f"Experience: {profiles[i].experience} years, Location: {profiles[i].location}"
            for i in I[0]
        ]
        llm_scores = get_llm_similarity_scores(state["jd_text"], snippets)

        # Combine FAISS and LLM scores
        matches = []
        for idx_in_search, llm_score in zip(I[0], llm_scores):
            faiss_score = float(1 - D[0][idx_in_search])
            hybrid_score = 0.6 * faiss_score + 0.4 * llm_score
            matches.append({
                "profile": profiles[idx_in_search],
                "similarity_score": hybrid_score
            })

        # Sort by hybrid score
        matches.sort(key=lambda x: x["similarity_score"], reverse=True)

        # Assign ranks
        for i, match in enumerate(matches):
            match["rank"] = i + 1

        state["ranked_profiles"] = matches
        state["top_matches"] = matches[:3]
        state["all_matches"] = [m for m in matches if m["similarity_score"] >= 0.2]

        return state

    except Exception as e:
        print(f"⚠️ Error during ranking: {e}")
        return state


# --- Communication Agent ---
def send_notifications(state: MatchState, db: Session) -> None:
    jd = state["job_description"]
    top_matches = state.get("top_matches", [])
    jd_id = jd.id

    if top_matches:
        message = f"Top 3 Matches for Job ID: {jd_id}\n\n"
        for idx, match in enumerate(top_matches):
            profile = match["profile"]
            message += f"{idx + 1}. {profile.name} | Score: {match['similarity_score']:.2f}\n"
    else:
        message = f"No suitable matches found for Job ID: {jd_id}. Please review manually."

    # Save email content to the database
    email_notification = Notification(
        jd_id=jd_id,
        recipient_email="recipient@example.com",  # Replace with actual recipient
        email_content=message,
        status="pending",
        sent_at=datetime.now()
    )
    db.add(email_notification)
    db.commit()

    print(f"📧 Email notification created for Job ID: {jd_id}")


# --- Helper: LLM Similarity Scoring ---
def get_llm_similarity_scores(job_description: str, resumes: List[str]) -> List[float]:
    """
    Uses GPT-4o to generate semantic similarity scores between job description and each resume.
    Scores are from 0 to 1.
    """
    prompt_template = f"""Task :- To rate the match between the {job_description} and the {resumes} on a scale of 0 to 1, you can follow these steps:

                Evaluation Criteria
                    Skills Match: Assess the overlap between the required skills in the job description and the skills listed in the resume.
                    Experience Match: Compare the years of experience required in the job description with the candidate's experience in the resume.
                    Description Match: Compare the candidate's past project experience with the description given in job description
                    Location Match: Check if the candidate's location aligns with the job location or if remote work is acceptable.
                    Availability: Verify if the candidate's availabale or not ("avialable","busy","unavailable")
                    Role/Title Alignment: Evaluate whether the candidate's previous roles align with the job title or responsibilities.
                    Scoring Process
                - Assign a score for each criterion (e.g., skills, experience, location, etc.).
                - Combine the scores into a weighted average or a hybrid score (e.g., 30% skills match, 20% experience match, 30% description match, 10% location match, 10% availability).
                Example
                    Job Description:
                    Title: Software Engineer
                    Skills: Python, Machine Learning, SQL
                    Experience: 3+ years
                    Description: Responsible for developing and deploying machine learning models, optimizing SQL databases, and creating scalable Python-based applications for data-driven decision-making.
                    Location: New York, NY
                Resume:
                    Name: John Doe
                    Skills: Python, SQL, Data Analysis
                    Experience: 4 years
                    Location: Remote (willing to relocate)
                    Projects:
                            Project 1: Developed a Python-based data pipeline to process and analyze 1TB of data daily, improving processing speed by 30%.
                            Project 2: Designed and optimized SQL databases for a fintech company, reducing query time by 40%.
                            Project 3: Built a predictive analytics dashboard using Python and data visualization libraries, enabling real-time decision-making for marketing campaigns.
                    Availability: available
                    
                Match Score:
                    Skills Match: Python (yes), Machine Learning (no), SQL (yes) → 2/3 = 0.67
                    Experience Match: 4 years vs. 3+ years → 1.0
                    Description match: Strong alignment in Python and SQL projects, partial alignment in machine learning responsibilities → 0.9
                    Location Match: Willing to relocate → 0.8
                    Availability: available → 1.0
                    
                Weighted Score:
                    Skills (30%): 0.67 × 0.3 = 0.201
                    Experience (20%): 1.0 × 0.2 = 0.2
                    Description Match (30%): 0.9 × 0.3 = 0.27
                    Location (10%): 0.8 × 0.1 = 0.08
                    Availability (10%): 1.0 × 0.1 = 0.1

                Final Match Score: 0.201 + 0.2 + 0.27 + 0.08 + 0.1 = 0.851:"""

    scores = []
    for resume in resumes:
        try:
            response = client.chat.completions.create(
                model="gtp-4o",
                messages=[
                    {"role": "system",
                     "content": "You are a Human Resource person having 10 years of experience that evaluates how well a resume matches a job description."},
                    {"role": "user", "content": prompt_template.format(
                        job_description=job_description,
                        resume=resume
                    )}
                ],
                temperature=0.2
            )
            content = response.choices[0].message.content.strip()
            score = float(content)
            scores.append(score if 0 <= score <= 1 else 0.0)
        except Exception as e:
            print(f"❌ LLM scoring error: {e}")
            scores.append(0.0)

    return scores


# --- Build Graph ---
workflow = StateGraph(MatchState)

# Add nodes
workflow.add_node("compare", RunnableLambda(compare_profiles))
workflow.add_node("ranking", RunnableLambda(rank_profiles))
workflow.add_node("communication", RunnableLambda(send_notifications))

# Set entry point
workflow.set_entry_point("compare")

# Link processing chain
workflow.add_edge("compare", "ranking")
# workflow.add_edge("ranking", "communication")
workflow.add_edge("ranking", END)

# Compile the agent flow
app = workflow.compile()

print("✅ Multi-Agent Recruitment Matching System is ready.")


# === Public Function to Use in Your CRUD Code ===
def run_agent_matching(db: Any, jd: JobDescriptionRequest, profiles: List[ConsultantProfileSchema]) -> dict:
    """
    Run the agent-based matching flow for a given job description and list of consultant profiles.

    Args:
        db: SQLAlchemy Session (for communication agent if needed)
        jd: The job description object
        profiles: List of consultant profiles

    Returns:
        Dictionary with 'top_matches' and 'all_matches'
    """
    initial_state = {
        "job_description": jd,
        "consultant_profiles": profiles
    }

    result = app.invoke(initial_state)
    return {
        "top_matches": result.get("top_matches"),
        "all_matches": result.get("all_matches")
    }
