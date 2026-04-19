from groq import Groq
import os
from dotenv import load_dotenv

# Load .env
load_dotenv()

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)


def generate_summary(confidence, old_name, new_name):
    print("\n🚀 LLM Agent Running...")

    try:
        prompt = f"""
        You are a KYC verification assistant.

        Old Name: {old_name}
        New Name: {new_name}
        Confidence Score: {confidence}

        Classify the request into:
        - VALID (high confidence)
        - REVIEW (medium confidence)
        - REJECT (low confidence)

        Also provide a short explanation.
        """

        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        result = response.choices[0].message.content.strip()

        print("LLM Response:", result)

        return result

    except Exception as e:
        print("LLM ERROR:", e)

        # Fallback (VERY IMPORTANT)
        if confidence > 90:
            return "High confidence. Likely valid."
        elif confidence > 70:
            return "Moderate confidence. Needs human review."
        else:
            return "Low confidence. Likely mismatch."