import os
import re
import time
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

    StageOneSystemMessage = (
        "You must answer with the exact fields shown and nothing else. "
        "Do not add greetings, explanations, or punctuation."
    )

    StageOnePrompt = (
        f"You are assessing whether the following feedback is relevant to a leadership attribute.\n\n"
        f"Leadership Attribute: {AttributeName}\n"
        f"Definition: {AttributeDefinition}\n\n"
        f"Feedback:\n{TalentFeedback}\n\n"
        "Respond only with these lines:\n"
        "Relevant: <Yes or No>\n"
        "Substring: <complete sentence or 'N/A'>"
    )

    for OverallAttempt in range(25):
        try:
            StageOneResponse = None
            StageOneContent = None
            IsRelevant = False
            RelevantSubstring = ""

            for StageOneAttempt in range(25):
                try:
                    StageOneResponse = AzureClient.chat.completions.create(
                        messages=[
                            {"role": "system", "content": StageOneSystemMessage},
                            {"role": "user", "content": StageOnePrompt},
                        ],
                        model=DeploymentName,
                        temperature=0.2,
                    )
                    StageOneContent = StageOneResponse.choices[0].message.content

                    RelevantMatch = re.search(
                        r"(?im)^Relevant\s*:\s*(Yes|No)\b",
                        StageOneContent,
                    )
                    SubstringMatch = re.search(
                        r"(?im)^Substring\s*:\s*(.+)",
                        StageOneContent,
                    )
                    if not RelevantMatch or not SubstringMatch:
                        raise ValueError("Stage one parsing failed")

                    IsRelevant = RelevantMatch.group(1).strip().lower() == "yes"
                    RelevantSubstring = SubstringMatch.group(1).strip()
                    break
                except Exception as Error:
                    if StageOneAttempt == 24:
                        raise
                    time.sleep(1)

            IsCompliment = False

            if IsRelevant and RelevantSubstring:
                StageTwoSystemMessage = (
                    "You must answer with the exact fields shown and nothing else. "
                    "Do not add greetings, explanations, or punctuation."
                )
                StageTwoPrompt = (
                    "Classify the following sentence from talent feedback as a"
                    " compliment or feedback for development.\n\n"
                    f"Sentence: {RelevantSubstring}\n\n"
                    "Respond only with this line:\n"
                    "Classification: <Compliment or Feedback for Development>"
                )
                StageTwoResponse = None

                for StageTwoAttempt in range(25):
                    try:
                        StageTwoResponse = AzureClient.chat.completions.create(
                            messages=[
                                {"role": "system", "content": StageTwoSystemMessage},
                                {"role": "user", "content": StageTwoPrompt},
                            ],
                            model=DeploymentName,
                            temperature=0.2,
                        )
                        StageTwoContent = StageTwoResponse.choices[0].message.content
                        ClassificationMatch = re.search(
                            r"(?im)^Classification\s*:\s*(Compliment|Feedback for Development)\b",
                            StageTwoContent,
                        )
                        if not ClassificationMatch:
                            raise ValueError("Stage two parsing failed")
                        IsCompliment = (
                            ClassificationMatch.group(1).lower() == "compliment"
                        )
                        break
                    except Exception as Error:
                        if StageTwoAttempt == 24:
                            raise
                        time.sleep(1)

            return IsRelevant, RelevantSubstring, IsCompliment
        except Exception as Error:
            if OverallAttempt == 24:
                raise
            time.sleep(1)

    raise RuntimeError("Failed to evaluate leadership feedback after multiple attempts")
