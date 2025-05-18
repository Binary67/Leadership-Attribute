import os
import re
from openai import AzureOpenAI


def EvaluateLeadershipFeedback(TalentFeedback: str, AttributeName: str, AttributeDefinition: str):
    """Evaluate feedback relevance and classify the tone using Azure OpenAI.

    This function covers Stage 1 and Stage 2 of the project's workflow. It first
    checks whether ``TalentFeedback`` is relevant to ``AttributeName`` using the
    provided ``AttributeDefinition`` for context and extracts the most relevant
    sentence. It then classifies the extracted sentence as either a compliment or
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
    AzureClient = AzureOpenAI(
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    )
    DeploymentName = os.getenv("AZURE_OPENAI_DEPLOYMENT")

    StageOnePrompt = (
        f"You are assessing whether the following feedback is relevant to a leadership attribute.\n\n"
        f"Leadership Attribute: {AttributeName}\n"
        f"Definition: {AttributeDefinition}\n\n"
        f"Feedback:\n{TalentFeedback}\n\n"
        "Respond in this format:\n"
        "Relevant: <Yes or No>\n"
        "Substring: <complete sentence or 'N/A'>"
    )

    StageOneResponse = AzureClient.chat.completions.create(
        messages=[{"role": "user", "content": StageOnePrompt}],
        model=DeploymentName,
        temperature=0.2,
    )
    StageOneContent = StageOneResponse.choices[0].message.content

    RelevantMatch = re.search(r"Relevant:\s*(Yes|No)", StageOneContent, re.IGNORECASE)
    SubstringMatch = re.search(r"Substring:\s*(.+)", StageOneContent, re.IGNORECASE)

    IsRelevant = False
    RelevantSubstring = ""

    if RelevantMatch:
        IsRelevant = RelevantMatch.group(1).strip().lower() == "yes"
    if SubstringMatch:
        RelevantSubstring = SubstringMatch.group(1).strip()

    IsCompliment = False

    if IsRelevant and RelevantSubstring:
        StageTwoPrompt = (
            "Classify the following sentence from talent feedback as a compliment or feedback for development.\n\n"
            f"Sentence: {RelevantSubstring}\n\n"
            "Respond in this format:\n"
            "Classification: <Compliment or Feedback for Development>"
        )
        StageTwoResponse = AzureClient.chat.completions.create(
            messages=[{"role": "user", "content": StageTwoPrompt}],
            model=DeploymentName,
            temperature=0.2,
        )
        StageTwoContent = StageTwoResponse.choices[0].message.content

        ClassificationMatch = re.search(
            r"Classification:\s*(Compliment|Feedback for Development)",
            StageTwoContent,
            re.IGNORECASE,
        )
        if ClassificationMatch:
            IsCompliment = ClassificationMatch.group(1).lower() == "compliment"

    return IsRelevant, RelevantSubstring, IsCompliment
