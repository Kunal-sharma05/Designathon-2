import os
from typing import List, Optional
from schema.ConsultantProfile import ConsultantProfileSchema
from dotenv import load_dotenv
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import AzureChatOpenAI
from schema.JobDescription import JobDescriptionRequest

load_dotenv()


# Initialize the LLM
llm = AzureChatOpenAI(
    azure_deployment=os.getenv("model_name"),
    azure_endpoint=os.getenv("azure_endpoint"),
    api_key=os.getenv("openai_api_key"),
    api_version=os.getenv("openai_api_version"),
    temperature=0.1,
)


def extract_information(cleaned_text: str) -> JobDescriptionRequest:
    """
    Extracts information from cleaned resume text using an LLM.

    Args:
        cleaned_text: The cleaned resume text as a string.

    Returns:
        A dictionary with the extracted and structured consultant profile.
    """
    parser = JsonOutputParser(pydantic_object=JobDescriptionRequest)

    format_instructions = parser.get_format_instructions()

    prompt = ChatPromptTemplate.from_template(
        template="""
Extract information from the resume provided below.
Follow the formatting instructions precisely.

{format_instructions}

Resume:
{cleaned_text}
""",
        partial_variables={"format_instructions": format_instructions},
    )

    chain = prompt | llm | parser

    extracted_data = chain.invoke({"cleaned_text": cleaned_text})

    # Create the full consultant profile with the extracted data
    job_description = JobDescriptionRequest(**extracted_data)

    return job_description


if __name__ == "__main__":
    # Example usage:
    sample_resume = """
    John Doe
    Senior Software Engineer

    Contact:
    - Email: john.doe@email.com
    - Phone: (123) 456-7890
    - Location: San Francisco, CA

    Summary:
    A highly motivated software engineer with over 8 years of experience in developing and maintaining web applications.

    Skills:
    - Python, Java, C++
    - JavaScript, React, Node.js
    - SQL, PostgreSQL, MongoDB
    - Docker, Kubernetes, AWS

    Experience:
    - Lead Software Engineer, TechCorp (2018-Present)
    - Software Engineer, Innovate LLC (2015-2018)
    """

    extracted_profile = extract_information(sample_resume)
    import json

    print(json.dumps(extracted_profile, indent=2, default=str))
