import os
from dotenv import load_dotenv
import openai

def get_museum_route_feedback(group_size, group_type, group_description, art_knowledge_level, preferred_periods,
                              preferred_authors, preferred_themes, time_coefficient,
                              proposed_paintings, route_score, perfect_route_score=10, textual_feedback='full'):
    """
    Get a numeric and textual feedback about an art museum route using the OpenAI GPT API.
    
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
        Determines the level of textual feedback in addition to the numeric evaluation.
        Options:
        - 'None': Only numeric evaluation and empty feedback line.
        - 'short': Numeric evaluation + very short good/bad feedback sentence.
        - 'full': Numeric evaluation + brief but more detailed feedback (original prompt style).

    Returns
    -------
    str
        A string containing two lines:
        - First line: "Evaluation: n/5"
        - Second line: "Feedback: ..." according to the chosen textual_feedback style.
    """
    # Load the OpenAI API key from the .env file
    load_dotenv()
    client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    if textual_feedback == 'None':
        # Only numeric evaluation, empty feedback
        prompt = f"""
        You are an expert in visitor experiences in art museums. Based on the following characteristics of the group and the proposed route, provide only a numeric evaluation on a scale of 1 to 5 (with one decimal point), and leave the feedback line empty.

        Now, using the following group and route details, generate your evaluation and feedback:

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
        Feedback: ''
        """
    elif textual_feedback == 'short':
        # Numeric evaluation + very short good or bad sentence
        prompt = f"""
        You are an expert in visitor experiences in art museums. Based on the following characteristics of the group and the proposed route, provide a numeric evaluation on a scale of 1 to 5 (with one decimal point), followed by a very short (one sentence) feedback that is either positive or negative, reflecting the group's overall satisfaction. You must speak for the group meaning as if you were part of it and visited the museum.

        Now, using the following group and route details, generate your evaluation and feedback:

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
        """
    else:
        # Full detailed feedback (original prompt)
        prompt = f"""
        You are an expert in visitor experiences in art museums. Based on the following characteristics of the group and the proposed route, provide an experience evaluation on a scale of 1 to 5 (with one decimal point), followed by brief feedback reflecting the group's satisfaction as if you were part of it and visited the museum.

        Now, using the following group and route details, generate your evaluation and feedback:

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
        """

    # Call to GPT model
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )

    # Extract the content of the response
    feedback = response.choices[0].message.content.strip()
    return feedback


# Example usage
if __name__ == "__main__":
    group_size = 4
    group_type = "family"
    group_description = "A family with two children, aged 8 and 12, interested in art and enjoy to ride bicycles."
    art_knowledge_level = 2
    preferred_periods = ["Impressionism", "Surrealism"]
    preferred_authors = ["Van Gogh", "Magritte"]
    preferred_themes = ["nature", "dreams"]
    time_coefficient = 0.8
    proposed_paintings = ["Starry Night", "The Persistence of Memory", "The Treachery of Images", "Water Lilies", "The Dream", "The Scream", "Guernica", "The Kiss", "The Birth of Venus", "The Last Supper", "Mona Lisa", "The Starry Night", "The Night Watch", "The Creation of Adam"]
    route_score = 7.5

    # Full feedback
    full_feedback = get_museum_route_feedback(
        group_size, group_type, group_description, art_knowledge_level, preferred_periods, preferred_authors,
        preferred_themes, time_coefficient, proposed_paintings, route_score, textual_feedback='full'
    )
    print("Full Feedback:\n", full_feedback)

    # Short feedback
    short_feedback = get_museum_route_feedback(
        group_size, group_type, group_description, art_knowledge_level, preferred_periods, preferred_authors,
        preferred_themes, time_coefficient, proposed_paintings, route_score, textual_feedback='short'
    )
    print("\nShort Feedback:\n", short_feedback)

    # None feedback
    none_feedback = get_museum_route_feedback(
        group_size, group_type, group_description, art_knowledge_level, preferred_periods, preferred_authors,
        preferred_themes, time_coefficient, proposed_paintings, route_score, textual_feedback='None'
    )
    print("\nNone Feedback:\n", none_feedback)