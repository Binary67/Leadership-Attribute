# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an AI-powered leadership attribute rating system that analyzes talent feedback using Azure OpenAI. The system processes feedback through a three-stage pipeline to identify leadership attributes and assign ratings.

## Architecture

The system follows a sequential pipeline pattern:

1. **FeedbackAnalyzer.py**: Determines relevance and classifies feedback as strength/development
2. **AttributeRater.py**: Assigns numerical ratings (1-5) based on YAML-defined rubrics
3. **main.py**: Orchestrates the pipeline and handles data flow

Key configuration files:
- **Attribute-Definition.yaml**: Defines 27 leadership attributes
- **AttributeRatingSystem.yaml**: Contains detailed rating rubrics for each attribute

## Commands

Run the complete pipeline:
```bash
python main.py
```

This will:
1. Generate test data using DataGeneration.py
2. Process feedback through all three stages
3. Output results with ratings and justifications

## Key Development Patterns

### API Integration
- Uses Azure OpenAI with retry logic (25 attempts)
- Structured prompts with regex parsing for responses
- Temperature set to 0-0.2 for consistency

### Processing
- Parallel execution using ThreadPoolExecutor
- Pandas DataFrames for data manipulation
- Progress tracking with tqdm

### Response Format
Each feedback produces:
- `IsRelevant`: Boolean
- `RelevantSubstring`: Extracted text
- `IsCompliment`: Strength/development indicator
- `Rating`: 0-5 score
- `Justification`: Reasoning

## Important Notes

- API credentials are currently hardcoded in source files
- Rating logic differs for strengths (3-5) vs development areas (1-3)
- System processes all 27 attributes for each feedback item

## Coding Guidelines

- Name all variables, functions, and classes in Pascal Case

## Claude Instructions

- Strictly follow the instructions. Only implement what is instructed by the user and do not add additional features that are not in the instructions.
- Remove unnecessary codes. Only keep the codes that are required for the project.