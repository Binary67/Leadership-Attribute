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

Client = AsyncAzureOpenAI(
  azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT"), 
  api_key = os.getenv("AZURE_OPENAI_API_KEY"),  
  api_version = "2024-05-01-preview"
)

def LoadAttributeDefinitions(FilePath: str = "Attribute-Definition.yaml") -> dict:
    """Load leadership attributes from YAML file."""
    AttributeData = {}
    with open(FilePath, "r") as File:
        for Line in File:
            if Line.strip() and ":" in Line:
                AttributeName, AttributeDefinition = Line.strip().split(":", 1)
                AttributeData[AttributeName.strip()] = AttributeDefinition.strip()
    return AttributeData


Dict27Attributes = LoadAttributeDefinitions()
Data = GenerateDummyData(Dict27Attributes)


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
    
    RatingData = _LoadRatingDefinitions()
    
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
