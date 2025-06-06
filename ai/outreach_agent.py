import json
import sqlite3
from ai.openai_client import get_openai_client, get_openai_model
from ai.outreach_prompt import outreach_prompt
from ai.outreach_response_model import OutreachResponse

MODEL          = get_openai_model()
client         = get_openai_client()
VECTOR_STOREID = "vs_682541f450b08191b838bf9515acf5f5"

# ──────────────────────────────────────────────────────────────────────────────
def generate_outreach(job_title: str, company: str, job_description: str, instructions: str = "", return_prompt=False):
    user_prompt = (
        f"job_title: {job_title}\n"
        f"company: {company or 'Unknown'}\n\n"
        f"job_description:\n{job_description.strip()}\n\n"
        f"application_instructions:\n{instructions.strip()}\n\n"
        "Return the response in JSON format."
    )

    try:
        resp = client.responses.create(
            model=MODEL,
            instructions=outreach_prompt,
            input=[{
                "role": "user",
                "content": [{"type": "input_text", "text": user_prompt}]
            }],
            tools=[{
                "type": "file_search",
                "vector_store_ids": [VECTOR_STOREID]
            }],
            text={"format": {"type": "json_object"}},
            tool_choice="auto",
        )

        assistant_msg = next(it for it in resp.output if getattr(it, "role", None) == "assistant")
        result = OutreachResponse.model_validate_json(assistant_msg.content[0].text)

        if return_prompt:
            return user_prompt, result
        return result

    except json.JSONDecodeError:
        raise RuntimeError("❌ Assistant returned invalid JSON.")
    except StopIteration:
        raise RuntimeError("❌ No assistant message in response.")
    except Exception as exc:
        raise RuntimeError(f"❌ OpenAI request failed: {exc}")


