import os
from concurrent.futures import ThreadPoolExecutor
from openai import AzureOpenAI
import pandas as pd
import numpy as np
import random
import re
from tqdm import tqdm
import warnings
from typing import Tuple
from FeedbackAnalyzer import EvaluateLeadershipFeedback
from AttributeRater import _LoadRatingDefinitions, GetLeadershipAttributeRating

warnings.filterwarnings("ignore")
tqdm.pandas()

Data = pd.read_csv('your_data.csv')

dict_27Attributes = {
    'Ambiguity & Tolerance': 'Comfortable with uncertainty, unpredictability, conflicting directions, and multiple demands. May be challenged to work in a structured environment.',
    'Risk Tolerant': 'Experiments with work in unfamiliar terrain while enduring variability & volatility. May be perceived as adventurous',
    'Ambition': 'Career oriented and desires to be successful by undertaking great efforts. May be perceived as self-centered.',
    'Collaborative': 'Forms social & emotional bonds and desires to help others without the use of authority or force. May be drawn in different directions in trying to meet everyones needs',
    'Commercially Oriented': 'Acts and prioritizes work as per customer requirements. Understands business and revenue drivers. May be challenged to decide basis qualitative inputs.',
    'Dependable': 'Reliable and focused on task completion. May be challenged to multitask.',
    'Dominance': 'Likes to be In- control & power over others. May be perceived as inflexible & micro-managing.',
    'Driven': 'Target driven and likes challenges. May experience burn out.',
    'Empathetic': 'Recognizes and is sensitive to others feelings & thoughts and understands their point of view. May get overly involved in others problems and experience personal distress impairing judgement.',
    'Expressive': 'Speaks the mind and openly expresses feelings. May come across blunt and direct.',
    'Forward Thinking': 'Looks beyond the "now", anticipate implications and consequences by creating scenarios before decision. May find it challenging catering to immediate requirement.',
    'Problem Solving': 'Provides a clear and sound reasoning, narrows down the problem and addresses them in a logical manner. May be perceived as intruding into others problems',
    'Innovative': 'Challenges status quo and produces new ideas, methods, techniques or practices at workplace. May be challenged to accept existing practices and conventions.',
    'Judgement': 'Makes considered decisions using various factors and comes to a sensible conclusion. May be perceived as being rigid.',
    'Evaluative': 'Judges the quality, importance, amount or value by weighing the pros and cons before decision. May be challenged to decide with limited information.',
    'Structured': 'Plans and organizes work in a methodical & efficient manner. May be perceived as inflexible or resist frequent changes.',
    'Conceptual': 'Identifies patterns, enjoys discussing abstract concepts and integrates various factors to draw insights. May be challenged to view the practical aspects.',
    'Reactive': 'Responds to any situation and acts depending on the circumstances. May be seen as impulsive.',
    'Quality Focused': 'Promotes and maintains high standards at work, is detail oriented and produces error free work. May be over-worked',
    'Learning Agility': 'Learns, un-learns, re- learns new things with speed. May be perceived as causing unnecessary disruptions',
    'Mood Stability': 'Maintains consistent emotional appearance even in difficult situations. May be seem as cold and distant.',
    'Motivating': 'Driving force responsible for the initiation behind goal directed behavior. May be perceived as being pushy.',
    'Openness': 'Receptive to new & unfamiliar ideas and experiences. May be perceived as being inconsistent with ones own views.',
    'Persuasive': 'Influence others to own views and likes to negotiate. May be perceived as opinionated.',
    'Service Orientation': 'Focus on satisfying others needs. May be challenged to say no.',
    'Sociable': 'Comfortable interacting with strangers in formal situations. May be perceived as distractible',
    'Trusting': 'Believes in others and what they say. May be perceived as easily deceivable.',
    }

def ExpandTalentFeedback(DataFrameInput: pd.DataFrame,
                          AttributeDict: Dict[str, str]) -> pd.DataFrame:
    """
    Take a one-column dataframe (column name: 'talent_feedback') and
    a dictionary of leadership attributes → definition, then

    1. Add two new columns: AttributeName and AttributeDefinition.
    2. Replicate each feedback row 27 times (once per attribute),
       so every piece of feedback is paired with every attribute.
    3. Return the expanded dataframe.

    Parameters
    ----------
    DataFrameInput : pd.DataFrame
        Must contain a column called 'talent_feedback'.
    AttributeDict : Dict[str, str]
        Keys are attribute names, values are attribute definitions.
        Expected length: 27, but the function works for any size.

    Returns
    -------
    pd.DataFrame
        Original columns + AttributeName + AttributeDefinition,
        with len(DataFrameInput) × len(AttributeDict) rows.
    """

    AttributeNames = list(AttributeDict.keys())
    AttributeDefinitions = list(AttributeDict.values())

    ExpandedDF = (
        DataFrameInput.copy()
        .assign(
            AttributeName=[AttributeNames] * len(DataFrameInput),
            AttributeDefinition=[AttributeDefinitions] * len(DataFrameInput)
        )
        # explode will replicate rows: one per list element
        .explode(["AttributeName", "AttributeDefinition"], ignore_index=True)
    )

    return ExpandedDF
  

Data = ExpandTalentFeedback(Data, dict_27Attributes)


def EvaluateRow(Row: dict) -> Tuple[bool, str, bool]:
    return EvaluateLeadershipFeedback(
        Row["feedback_extracted"], Row["AttributeName"], Row["AttributeDefinition"]
    )


def RateRow(Row: dict) -> Tuple[int, str]:
    return GetLeadershipAttributeRating(
        Row["feedback_extracted"],
        Row["AttributeName"],
        Row["IsRelevant"],
        Row["RelevantSubstring"],
        Row["IsCompliment"],
    )


with ThreadPoolExecutor() as Executor:
    EvaluationResults = list(
        tqdm(Executor.map(EvaluateRow, Data.to_dict("records")), total=len(Data))
    )

Data[["IsRelevant", "RelevantSubstring", "IsCompliment"]] = pd.DataFrame(
    EvaluationResults,
    columns=["IsRelevant", "RelevantSubstring", "IsCompliment"],
)

_RATING_DATA = _LoadRatingDefinitions()

with ThreadPoolExecutor() as Executor:
    RatingResults = list(
        tqdm(Executor.map(RateRow, Data.to_dict("records")), total=len(Data))
    )

Data[["Rating", "Justification"]] = pd.DataFrame(
    RatingResults, columns=["Rating", "Justification"]
)
