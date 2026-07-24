from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field
from typing import List
from dotenv import load_dotenv
import os


class SkillMatchOutput(BaseModel):
    matching_skills: List[str] = Field(description="Up to 3 matching technical skills")
    missing_skills: List[str] = Field(description="Up to 3 missing technical skills")
    extra_skills: List[str] = Field(description="Up to 5 extra technical skills candidate has")


parser = JsonOutputParser(pydantic_object=SkillMatchOutput)


def skill_match(summery, job_description):

    System_prompt = ChatPromptTemplate.from_messages([
        ("system", """You are an expert AI recruitment assistant.

    Your task is to compare a candidate's resume summary with a job description.

    Instructions:
    1. Extract only the most important technical skills.
    2. Prioritize core technologies over supporting tools.
    3. Ignore generic or broad terms if more specific skills are present.
    4. Show a maximum of:
       - 8 Matching Skills
       - 8 Missing Skills
       - 5 Extra Skills
    5. Remove duplicates.
    6. Do not explain your reasoning.
    7. Do not add notes or introductory text.

    Return ONLY valid JSON.
    {format_instructions}

    Only return valid JSON. No extra text, no markdown, no explanations."""),
        ("human", "Candidate Summary:\n{resume}\n\nJob Description:\n{job_description}")
    ])

    load_dotenv()

    llm = ChatGroq(
        api_key=os.getenv("LLM_API_KEY"),
        model="llama-3.3-70b-versatile"
    )

    System_prompt = System_prompt.partial(
        format_instructions=parser.get_format_instructions()
    )

    skill_chain = (
        System_prompt
        | llm
        | parser
    )

    result = skill_chain.invoke({
        "resume": str(summery),
        "job_description": job_description
    })

    return result
