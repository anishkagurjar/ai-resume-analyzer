import ollama
from groq import Groq
from utils.prompts import resume_prompt


def analyze_resume(resume_text, job_description, model_choice="Ollama (Local)", api_key=None):

    prompt = f"""
    {resume_prompt}

    RESUME:
    {resume_text}

    JOB DESCRIPTION:
    {job_description}
    """

    # Groq
    if model_choice == "Groq (Cloud)":
        if not api_key:
            return "❌ Please enter your Groq API Key in the sidebar."

        client = Groq(api_key=api_key)

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": "You are a professional ATS Resume Analyzer."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.7,
            max_tokens=1500
        )

        return response.choices[0].message.content

    # Ollama
    else:
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