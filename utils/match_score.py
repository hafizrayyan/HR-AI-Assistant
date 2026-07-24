from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field
from dotenv import load_dotenv
import os


class MatchScoreOutput(BaseModel):
    match_percentage: int = Field(description="Match score percentage between 0 and 100")


parser = JsonOutputParser(pydantic_object=MatchScoreOutput)


def match_score(summery, job_description):

    System_prompt = ChatPromptTemplate.from_messages([
        ("system", """You are an expert AI recruitment assistant.

    Compare the candidate's summary with the job description.

    Instructions:
    1. Compare the summary with the job description.
    2. Consider skills, education, projects, and experience.
    3. Calculate an overall match percentage between 0 and 100.
    4. Do NOT explain the score.

    Return ONLY valid JSON.
    {format_instructions}

    Only return valid JSON. No extra text, no markdown, no explanations."""),
        ("human", "Candidate Summary:\n{resume}\n\nJob Description:\n{job_description}")
    ])

    load_dotenv()

    llm = ChatGroq(
        api_key=os.getenv("LLM_API_KEY"),
        model="openai/gpt-oss-120b"
    )

    System_prompt = System_prompt.partial(
        format_instructions=parser.get_format_instructions()
    )

    score_chain = (
        System_prompt
        | llm
        | parser
    )

    result = score_chain.invoke({
        "resume": str(summery),
        "job_description": job_description
    })

    return result
