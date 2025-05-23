import os
import asyncio
from openai import AsyncAzureOpenAI
import pandas as pd
import numpy as np
import random
import re
from tqdm.asyncio import tqdm as atqdm
from tqdm import tqdm
import warnings
from typing import Tuple
from FeedbackAnalyzer import EvaluateLeadershipFeedback
from AttributeRater import _LoadRatingDefinitions, GetLeadershipAttributeRating
from DataGeneration import GenerateDummyData
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

warnings.filterwarnings("ignore")
tqdm.pandas()

client = AsyncAzureOpenAI(
  azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT"), 
  api_key = os.getenv("AZURE_OPENAI_API_KEY"),  
  api_version = "2024-05-01-preview"
)

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


Data = GenerateDummyData(dict_27Attributes)


async def EvaluateRow(Row: dict) -> Tuple[bool, str, bool]:
    return await EvaluateLeadershipFeedback(
        Row["feedback_extracted"], Row["AttributeName"], Row["AttributeDefinition"]
    )


async def RateRow(Row: dict) -> Tuple[int, str]:
    return await GetLeadershipAttributeRating(
        Row["feedback_extracted"],
        Row["AttributeName"],
        Row["IsRelevant"],
        Row["RelevantSubstring"],
        Row["IsCompliment"],
    )


async def ProcessData():
    # Process evaluation phase
    EvaluationTasks = [EvaluateRow(Row) for Row in Data.to_dict("records")]
    EvaluationResults = await atqdm.gather(*EvaluationTasks, desc="Evaluating feedback")
    
    Data[["IsRelevant", "RelevantSubstring", "IsCompliment", 'ModelContent']] = pd.DataFrame(
        EvaluationResults,
        columns=["IsRelevant", "RelevantSubstring", "IsCompliment", 'ModelContent'],
    )
    
    _RATING_DATA = _LoadRatingDefinitions()
    
    # Process rating phase
    RatingTasks = [RateRow(Row) for Row in Data.to_dict("records")]
    RatingResults = await atqdm.gather(*RatingTasks, desc="Rating feedback")
    
    Data[["Rating", "Justification"]] = pd.DataFrame(
        RatingResults, columns=["Rating", "Justification"]
    )

    Data.to_csv('output/TalentData.csv', index = False)
    
    return Data


# Run the async processing
if __name__ == "__main__":
    asyncio.run(ProcessData())
