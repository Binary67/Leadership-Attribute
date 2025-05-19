# Implementation of rating evaluation for leadership feedback
import os
import re
import time
from typing import Tuple
from openai import AzureOpenAI


def _LoadRatingDefinitions(FilePath: str = "AttributeRatingSystem.yaml") -> dict:
    """Parse rating definitions from YAML-like file."""
    RatingData = {}
    AttributeName = None
    RatingKey = None
    with open(FilePath, "r") as File:
        for Line in File:
            if not Line.strip():
                continue
            if not Line.startswith(" "):
                AttributeName = Line.strip().rstrip(":")
                RatingData[AttributeName] = {}
                RatingKey = None
            elif Line.strip().startswith("Rating"):
                Parts = Line.strip().split(":", 1)
                RatingKey = Parts[0]
                RatingData[AttributeName][RatingKey] = Parts[1].strip()
            else:
                if AttributeName and RatingKey:
                    RatingData[AttributeName][RatingKey] += " " + Line.strip()
    return RatingData


_RATING_DATA = _LoadRatingDefinitions()


def GetLeadershipAttributeRating(
    CompleteFeedback: str,
    AttributeName: str,
    IsRelevant: bool,
    RelevantSubstring: str,
    IsCompliment: bool,
) -> Tuple[int, str]:
    """Determine rating for a feedback substring using Azure OpenAI.

    Parameters
    ----------
    CompleteFeedback : str
        Entire feedback text.
    AttributeName : str
        Leadership attribute name.
    IsRelevant : bool
        Whether the feedback relates to the attribute.
    RelevantSubstring : str
        The substring from feedback relevant to the attribute.
    IsCompliment : bool
        ``True`` if the substring is a compliment, ``False`` if it is feedback for development.

    Returns
    -------
    tuple[int, str]
        Numeric rating (1-5) and justification text.
    """
    if not IsRelevant:
        return 0, "Feedback not relevant to the attribute."

    AttributeDefinitions = _RATING_DATA.get(AttributeName)
    if not AttributeDefinitions:
        raise ValueError(f"Attribute '{AttributeName}' not found in rating system.")

    if IsCompliment:
        RatingKeys = ["Rating 3", "Rating 4", "Rating 5"]
    else:
        RatingKeys = ["Rating 1", "Rating 2"]

    SelectedDefinitions = "\n".join(
        f"{Key}: {AttributeDefinitions[Key]}" for Key in RatingKeys if Key in AttributeDefinitions
    )

    Prompt = (
        "Evaluate the leadership feedback snippet and assign a rating.\n\n"
        f"Attribute: {AttributeName}\n"
        f"Complete Feedback: {CompleteFeedback}\n"
        f"Snippet: {RelevantSubstring}\n\n"
        "Rating Definitions:\n"
        f"{SelectedDefinitions}\n\n"
        "If any behavior from 'Rating 5' appears, rate it a 5. "
        "If any behavior from 'Rating 1' appears, rate it a 1.\n\n"
        "Respond only with these lines:\n"
        "Rating: <number>\n"
        "Justification: <why this rating fits>"
    )

    SystemMessage = (
        "You must answer with exactly the two fields shown and nothing else. "
        "Do not add greetings, explanations, or punctuation around the rating."
    )

    AzureClient = AzureOpenAI(
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    )
    DeploymentName = os.getenv("AZURE_OPENAI_DEPLOYMENT")

    Response = None
    for Attempt in range(25):
        try:
            Response = AzureClient.chat.completions.create(
                messages=[
                    {"role": "system", "content": SystemMessage},
                    {"role": "user", "content": Prompt},
                ],
                model=DeploymentName,
                temperature=0,
            )
            break
        except Exception as Error:
            if Attempt == 24:
                raise
            time.sleep(1)
    Content = Response.choices[0].message.content

    RatingMatch = re.search(r"(?im)Rating\s*[:=\-]*\s*([1-5])", Content)
    JustificationMatch = re.search(
        r"(?im)Justification\s*[:=\-]*\s*(.+)", Content, re.DOTALL
    )

    RatingValue = int(RatingMatch.group(1)) if RatingMatch else 0
    JustificationText = (
        JustificationMatch.group(1).strip(" \n\t.;:") if JustificationMatch else ""
    )

    return RatingValue, JustificationText
