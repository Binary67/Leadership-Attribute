import pandas as pd
import random

def GenerateDummyData(dict_LeadershipAttribute):
    """
    Generate a DataFrame with dummy talent feedback paired with leadership attributes.
    
    Parameters:
    -----------
    leadership_attributes : dict
        Dictionary where keys are attribute names and values are their definitions.
        Expected to contain 27 leadership attributes.
        
    Returns:
    --------
    pd.DataFrame
        DataFrame with columns 'Talent Feedback', 'Attribute Name', and 'Attribute Definition'.
        Each talent feedback is paired with each attribute, resulting in 27 rows per feedback.
    """
    # Verify we have 27 attributes
    if len(dict_LeadershipAttribute) != 27:
        print(f"Warning: Expected 27 leadership attributes, but got {len(dict_LeadershipAttribute)}")
    
    # Generate dummy talent feedback (compliments and areas for development)
    PositiveFeedbacks = [
        "Demonstrates exceptional capability in leading cross-functional teams",
        "Shows remarkable ability to navigate complex organizational challenges",
        "Consistently delivers results while maintaining strong team morale",
        # "Excellent at developing and mentoring team members",
        # "Displays outstanding strategic thinking and planning abilities"
    ]
    
    DevelopmentFeedbacks = [
        "Could benefit from enhancing delegation skills",
        "Would be more effective with improved conflict resolution approaches",
        "Has opportunity to grow in providing constructive feedback",
        # "Should focus on developing more strategic long-term vision",
        # "Would benefit from more active listening in team discussions"
    ]
    
    # Combine positive and development feedback
    AllFeedbacks = PositiveFeedbacks + DevelopmentFeedbacks
    
    # Create a DataFrame with all combinations of feedback and attributes
    rows = []
    for EachFeedback in AllFeedbacks:
        for AttributeName, AttributeDefinition in dict_LeadershipAttribute.items():
            rows.append({
                'feedback_extracted': EachFeedback,
                'AttributeName': AttributeName,
                'AttributeDefinition': AttributeDefinition
            })
    
    # Create DataFrame
    Data = pd.DataFrame(rows)
    
    return Data
