from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field
from typing import List
from dotenv import load_dotenv
import os


class RecommendationOutput(BaseModel):
    decision: str = Field(description="'Hire' or 'Reject'")
    justification: List[str] = Field(description="2-3 concise bullet points explaining the decision")


parser = JsonOutputParser(pydantic_object=RecommendationOutput)


def recommendation(summery, job_description, skill_match, match_score):

    System_prompt = ChatPromptTemplate.from_messages([
        ("system", """You are an expert AI recruitment assistant.
    You are an experienced HR recruiter.

    Based on the information provided, determine whether the candidate should be hired.

    Instructions:
    1. Recommend ONLY one: 'Hire' or 'Reject'
    2. Write exactly 2-3 concise bullet points as justification.

    Return ONLY valid JSON.
    {format_instructions}

    Only return valid JSON. No extra text, no markdown, no explanations."""),
        ("human", "Summary: {summary}\nSkill Match: {skill_match}\nMatch Score: {match_score}\n\nJob Description: {job_description}")
    ])

    load_dotenv()

    llm = ChatGroq(
        api_key=os.getenv("LLM_API_KEY"),
        model="llama-3.1-8b-instant"
    )

    System_prompt = System_prompt.partial(
        format_instructions=parser.get_format_instructions()
    )

    rec_chain = (
        System_prompt
        | llm
        | parser
    )

    result = rec_chain.invoke({
        "summary": str(summery),
        "skill_match": str(skill_match),
        "match_score": str(match_score),
        "job_description": job_description
    })

    return result
