from langchain_core.prompts import  ChatPromptTemplate
from langchain_groq import ChatGroq
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field
from dotenv import load_dotenv
import os


class SummaryOutput(BaseModel):
    name: str = Field(description="Candidate's full name")
    summary: str = Field(description="2-3 sentence summary of their background")

parser = JsonOutputParser(pydantic_object = SummaryOutput)

def resume_summery(text):

    summary_prompt = ChatPromptTemplate.from_messages([
        ("system","""You are an expert AI recruitment assistant. " \
        Your task is to extract candidate name and analyze a candidate's resume and produce a concise professional summary for recruiters.Instructions:" \
        1. Read the entire resume.
        2. Extract only the most important information.
        3. Ignore personal details such as name, email, phone number, address, LinkedIn, GitHub, references, hobbies, and profile photos unless explicitly requested.
        4. Prioritize:
            - Highest education (degree and major)
            - Total professional experience (e.g., "3 years experience")
            - Primary technical skills (maximum 8)
            - Key domains or specializations (e.g., NLP, Computer Vision, Data Science, Generative AI)
            - Most significant project or achievement (maximum 3 items)
        5. If information is missing, omit it instead of guessing.
        6. Use clear, recruiter-friendly wording.
        7. Do not write paragraphs.
        8. Do not add explanations or introductory text.
        9. Keep the summary under 12 lines.
        10. Preserve the original meaning of the resume.
        Note : Return only in json format 

        Return ONLY valid JSON.
    {format_instructions}

    Only return valid JSON. No extra text, no markdown, no explanations."""),
        ("human", "Resume:\n{resume}")
    ])

    load_dotenv()

    llm = ChatGroq(
        api_key = os.getenv("LLM_API_KEY"),
        model = "openai/gpt-oss-safeguard-20b")

    summary_prompt = summary_prompt.partial(
    format_instructions=parser.get_format_instructions()
    )

    summery_chain =(
    summary_prompt
    | llm
    | parser
    )
    
    
    result = summery_chain.invoke({"resume" : text})
    return result
