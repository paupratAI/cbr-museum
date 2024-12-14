import os
import re
from dotenv import load_dotenv
import openai

def generate_and_parse_museum_feedback(group_size, group_type, group_description, art_knowledge_level, preferred_periods,
                                       preferred_authors, preferred_themes, time_coefficient,
                                       proposed_paintings, route_score, perfect_route_score=10, textual_feedback='full'):
    """
    Generate numeric and textual feedback for a museum route and parse the result.
    
    Parameters
    ----------
    group_size : int
        The size of the group visiting the museum.
    group_type : str
        The type of group (e.g., 'school', 'family', 'casual').
    group_description : str
        A description of the group composition and interests.
    art_knowledge_level : int
        An integer from 1 to 4 indicating the level of artistic knowledge of the group (1=low, 4=high).
    preferred_periods : list of str
        A list of artistic periods preferred by the group (e.g., ['Renaissance', 'Baroque']).
    preferred_authors : list of str
        A list of authors/artists preferred by the group (e.g., ['Picasso', 'Dalí']).
    preferred_themes : list of str
        A list of thematic preferences (e.g., ['landscapes', 'portraits']).
    time_coefficient : float
        A coefficient representing time constraints or preferences (1=normal speed, <1=faster, >1=slower).
    proposed_paintings : list of str
        The list of paintings included in the proposed route.
    route_score : float
        A guiding score for the route's interest or quality.
    perfect_route_score : float, optional
        The score considered as perfect. Default is 10.
    textual_feedback : str
        Determines the level of textual feedback ('None', 'short', or 'full').
    
    Returns
    -------
    dict
        A dictionary with the following keys:
        - 'evaluation': float (numeric feedback score)
        - 'feedback': str (textual feedback)
    """
    # Load the OpenAI API key from the .env file
    load_dotenv()
    client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    # Create the appropriate prompt based on the textual_feedback parameter
    if textual_feedback == 'None':
        prompt = f"""
        You are an expert in visitor experiences in art museums. Based on the following characteristics of the group and the proposed route, provide only a numeric evaluation on a scale of 1 to 5 (with one decimal point), and leave the feedback line empty.
        After completing the evaluation, answer these questions:
        Elevator Usage: Would the group prefer only elevators? (True / False).
        Time Coefficient: Should the visit pace change? (faster, equal, slower).
        Artwork Removal: Is there one artwork to remove? Provide the exact name or None.
        Guide Preference: Would you like a guided visit? (True / False).

        Now, using the following group and route details, generate your evaluation, textual feedback and answer the questions:

        **Group characteristics:**
        - Group size: {group_size}
        - Group type: {group_type}
        - Group description: {group_description}
        - Artistic knowledge level: {art_knowledge_level} (1-4) where 1 is low and 4 is high.
        - Preferred periods: {preferred_periods}
        - Preferred authors: {preferred_authors}
        - Preferred themes: {preferred_themes}
        - Time coefficient: {time_coefficient} where 1 is normal speed, <1 is faster, and >1 is slower.

        **Proposed route:**
        - Paintings to visit: {proposed_paintings}
        - Guiding score for the route: {route_score} where {perfect_route_score} is a perfect score.

        The format of the response must be:

        Evaluation: n.n/5
        Feedback:
        Only Elevator: Yes/No
        Time Coefficient: Shorter/Equal/Longer
        Artwork to Remove: Artwork Name
        Guided visit: Yes/No
        """
    elif textual_feedback == 'short':
        prompt = f"""
        You are an expert in visitor experiences in art museums. Based on the following characteristics of the group and the proposed route, provide a numeric evaluation on a scale of 1 to 5 (with one decimal point), followed by a very short (one sentence) feedback that is either positive or negative, reflecting the group's overall satisfaction. You must speak for the group meaning as if you were part of it and visited the museum.
        After completing the evaluation, answer these questions:
        Elevator Usage: Would the group prefer only elevators? (True / False).
        Time Coefficient: Should the visit pace change? (faster, equal, slower).
        Artwork Removal: Is there one artwork to remove? Provide the exact name or None.
        Guide Preference: Would you like a guided visit? (True / False).

        Now, using the following group and route details, generate your evaluation, textual feedback and answer the questions:

        **Group characteristics:**
        - Group size: {group_size}
        - Group type: {group_type}
        - Group description: {group_description}
        - Artistic knowledge level: {art_knowledge_level} (1-4) where 1 is low and 4 is high.
        - Preferred periods: {preferred_periods}
        - Preferred authors: {preferred_authors}
        - Preferred themes: {preferred_themes}
        - Time coefficient: {time_coefficient} where 1 is normal speed, <1 is faster, and >1 is slower.

        **Proposed route:**
        - Paintings to visit: {proposed_paintings}
        - Guiding score for the route: {route_score} where {perfect_route_score} is a perfect score.

        The format of the response must be:

        Evaluation: n.n/5
        Feedback:
        Only Elevator: Yes/No
        Time Coefficient: Shorter/Equal/Longer
        Artwork to Remove: Artwork Name
        Guided visit: Yes/No
        """
    else:
        prompt = f"""
        You are an expert in visitor experiences in art museums. Based on the following characteristics of the group and the proposed route, provide an experience evaluation on a scale of 1 to 5 (with one decimal point), followed by brief feedback reflecting the group's satisfaction as if you were part of it and visited the museum.
        After completing the evaluation, answer these questions:
        Elevator Usage: Would the group prefer only elevators? (True / False).
        Time Coefficient: Should the visit pace change? (faster, equal, slower).
        Artwork Removal: Is there one artwork to remove? Provide the exact name or None.
        Guide Preference: Would you like a guided visit? (True / False).

        Now, using the following group and route details, generate your evaluation, textual feedback and answer the questions:

        **Group characteristics:**
        - Group size: {group_size}
        - Group type: {group_type}
        - Group description: {group_description}
        - Artistic knowledge level: {art_knowledge_level} (1-4) where 1 is low and 4 is high.
        - Preferred periods: {preferred_periods}
        - Preferred authors: {preferred_authors}
        - Preferred themes: {preferred_themes}
        - Time coefficient: {time_coefficient} where 1 is normal speed, <1 is faster, and >1 is slower.

        **Proposed route:**
        - Paintings to visit: {proposed_paintings}
        - Guiding score for the route: {route_score} where {perfect_route_score} is a perfect score.

        Provide a numeric evaluation and concise textual feedback:

        The format of the response must be:

        Evaluation: n.n/5
        Feedback:
        Only Elevator: Yes/No
        Time Coefficient: Shorter/Equal/Longer
        Artwork to Remove: Artwork Name
        Guided visit: Yes/No
        """

    # Call to GPT model
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )

    # Extract the content of the response
    feedback = response.choices[0].message.content.strip()

    # Regular expressions to extract evaluation and feedback
    evaluation_match = re.search(r"Evaluation: (\d\.\d)/5", feedback)
    textual_feedback_match = re.search(r"Feedback: (.+)", feedback)
    only_elevator_match = re.search(r"Only Elevator: (Yes|No)", feedback)
    time_coefficient_match = re.search(r"Time Coefficient: (Shorter|Equal|Longer)", feedback)
    artwork_to_remove_match = re.search(r"Artwork to Remove: (.+)", feedback)
    guided_visit_match = re.search(r"Guided visit: (Yes|No)", feedback)

    evaluation = float(evaluation_match.group(1)) if evaluation_match else 3.0 # Default evaluation score
    textual_feedback = textual_feedback_match.group(1).strip() if textual_feedback_match else '' # Default feedback
    only_elevator_match = True if only_elevator_match and only_elevator_match.group(1) == 'Yes' else False
    time_coefficient = time_coefficient_match.group(1).strip() if time_coefficient_match else 'equal'
    artwork_to_remove = artwork_to_remove_match.group(1).strip() if artwork_to_remove_match else 'None'
    guided_visit = True if guided_visit_match and guided_visit_match.group(1) == 'Yes' else False

    return {
        "evaluation": evaluation,
        "feedback": textual_feedback,
        "only_elevator": only_elevator_match,
        "time_coefficient": time_coefficient,
        "artwork_to_remove": artwork_to_remove,
        "guided_visit": guided_visit
    }


"""# Example usage
if __name__ == "__main__":
    group_size = 4
    group_type = "family"
    group_description = "A family with two children, aged 8 and 12, interested in art and enjoy to ride bicycles."
    art_knowledge_level = 2
    preferred_periods = ["Impressionism", "Surrealism"]
    preferred_authors = ["Van Gogh", "Magritte"]
    preferred_themes = ["nature", "dreams"]
    time_coefficient = 0.8
    proposed_paintings = ["Starry Night", "The Persistence of Memory", "Water Lilies", "The Scream"]
    route_score = 7.5

    feedback_data = generate_and_parse_museum_feedback(
        group_size, group_type, group_description, art_knowledge_level, preferred_periods, preferred_authors,
        preferred_themes, time_coefficient, proposed_paintings, route_score, textual_feedback='full'
    )
    
    print("Full Feedback Data:", feedback_data)

    feedback_data_short = generate_and_parse_museum_feedback(
        group_size, group_type, group_description, art_knowledge_level, preferred_periods, preferred_authors,
        preferred_themes, time_coefficient, proposed_paintings, route_score, textual_feedback='short'
    )

    print("Short Feedback Data:", feedback_data_short)

    feedback_data_none = generate_and_parse_museum_feedback(
        group_size, group_type, group_description, art_knowledge_level, preferred_periods, preferred_authors,
        preferred_themes, time_coefficient, proposed_paintings, route_score, textual_feedback='None'
    )

    print("No Textual Feedback Data:", feedback_data_none)"""