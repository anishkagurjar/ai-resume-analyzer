import ollama

from utils.prompts import resume_prompt


def analyze_resume(resume_text, job_description):

    prompt = f"""
    {resume_prompt}

    RESUME:
    {resume_text}

    JOB DESCRIPTION:
    {job_description}
    """

    response = ollama.chat(
        model="tinyllama",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response["message"]["content"]