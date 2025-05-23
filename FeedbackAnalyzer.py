import os
import re
import asyncio
from openai import AsyncAzureOpenAI
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

async def EvaluateLeadershipFeedback(TalentFeedback: str, AttributeName: str, AttributeDefinition: str):
    """Evaluate feedback relevance and tone using a single Azure OpenAI call.

    The function checks whether ``TalentFeedback`` is relevant to ``AttributeName``
    using the provided ``AttributeDefinition`` for context and extracts the most
    relevant sentence. It also classifies that sentence as either a compliment or
    feedback for development.

    Parameters
    ----------
    TalentFeedback : str
        Raw talent feedback text.
    AttributeName : str
        Name of the leadership attribute.
    AttributeDefinition : str
        Definition of the leadership attribute.

    Returns
    -------
    tuple[bool, str, bool]
        ``IsRelevant`` (``True`` if relevant, otherwise ``False``), the
        ``RelevantSubstring`` extracted from the feedback, and ``IsCompliment``
        (``True`` for compliment, ``False`` for development).
    """
    AzureClient = AsyncAzureOpenAI(
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    )
    DeploymentName = os.getenv("AZURE_OPENAI_DEPLOYMENT")

    CombinedSystemMessage = (
        "You must answer with the exact fields shown and nothing else. "
        "Do not add greetings, explanations, or punctuation."
    )

    CombinedPrompt = (
        f"You are assessing whether the following feedback is relevant to a leadership attribute and classifying the tone.\n\n"
        f"Leadership Attribute: {AttributeName}\n"
        f"Definition: {AttributeDefinition}\n\n"
        f"Feedback:\n{TalentFeedback}\n\n"
        "Respond only with these lines:\n"
        "Relevant: <Yes or No>\n"
        "Substring: <complete sentence or 'N/A'>\n"
        "Classification: <Compliment or Feedback for Development or 'N/A'>"
    )

    for OverallAttempt in range(25):
        try:
            CombinedResponse = None
            CombinedContent = 'Default Message'
            IsRelevant = False
            RelevantSubstring = ""
            IsCompliment = False

            for CombinedAttempt in range(25):
                try:
                    CombinedResponse = await AzureClient.chat.completions.create(
                        messages=[
                            {"role": "system", "content": CombinedSystemMessage},
                            {"role": "user", "content": CombinedPrompt},
                        ],
                        model=DeploymentName,
                        temperature=0.2,
                    )
                    CombinedContent = CombinedResponse.choices[0].message.content

                    RelevantMatch = re.search(
                        r"(?im)^Relevant\s*:\s*(Yes|No)\b",
                        CombinedContent,
                    )
                    SubstringMatch = re.search(
                        r"(?im)^Substring\s*:\s*(.+)",
                        CombinedContent,
                    )
                    ClassificationMatch = re.search(
                        r"(?im)^Classification\s*:\s*(Compliment|Feedback for Development|N/A)\b",
                        CombinedContent,
                    )
                    if not RelevantMatch or not SubstringMatch or not ClassificationMatch:
                        raise ValueError("Parsing failed")

                    IsRelevant = RelevantMatch.group(1).strip().lower() == "yes"
                    RelevantSubstring = SubstringMatch.group(1).strip()
                    ClassificationValue = ClassificationMatch.group(1).strip().lower()
                    IsCompliment = ClassificationValue == "compliment"
                    break
                except Exception as Error:
                    if CombinedAttempt == 24:
                        return 'Error', 'Error', 'Error', Error
                    await asyncio.sleep(2)
            return IsRelevant, RelevantSubstring, IsCompliment, CombinedContent
        except Exception as Error:
            if OverallAttempt == 24:
                return 'Error', 'Error', 'Error', Error
            await asyncio.sleep(2)

    return 'Error', 'Error', 'Error', Error
