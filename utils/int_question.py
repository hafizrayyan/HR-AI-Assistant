from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field
from typing import List
from dotenv import load_dotenv
import os


class InterviewQuestionsOutput(BaseModel):
    questions: List[str] = Field(description="List of 5 technical and practical interview questions")


parser = JsonOutputParser(pydantic_object=InterviewQuestionsOutput)


def generate_questions(summery, job_description, skill_match, match_score):

    System_prompt = ChatPromptTemplate.from_messages([
        ("system", """You are an expert AI recruitment assistant.
    You are an experienced technical interviewer.

    Generate interview questions for the candidate.

    Instructions:
    1. Generate exactly 5 interview questions.
    2. Base the questions on the candidate's skills, projects, and missing skills.
    3. Ask practical, role-specific questions.
    4. Do not provide answers or explanations.

    Return ONLY valid JSON.
    {format_instructions}

    Only return valid JSON. No extra text, no markdown, no explanations."""),
        ("human", "Summary: {summary}\nSkill Match: {skill_match}\nMatch Score: {match_score}\n\nJob Description: {job_description}")
    ])

    load_dotenv()

    llm = ChatGroq(
        api_key=os.getenv("LLM_API_KEY"),
        model="llama-3.3-70b-versatile"
    )

    System_prompt = System_prompt.partial(
        format_instructions=parser.get_format_instructions()
    )

    int_chain = (
        System_prompt
        | llm
        | parser
    )

    result = int_chain.invoke({
        "summary": str(summery),
        "skill_match": str(skill_match),
        "match_score": str(match_score),
        "job_description": job_description
    })

    return result
