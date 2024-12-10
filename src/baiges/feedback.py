import os
import openai

def get_museum_route_feedback(group_size, group_type, group_description, art_knowledge_level, preferred_periods,
                              preferred_authors, preferred_themes, time_coefficient,
                              proposed_paintings, route_score):
    """
    Get a numeric and textual feedback about an art museum route using the OpenAI GPT API.
    
    Parameters
    ----------
    group_size : int
        The size of the group visiting the museum.
    group_type : str
        The type of group (e.g., 'school', 'family', 'casual').
    art_knowledge_level : int
        An integer from 1 to 4 indicating the level of artistic knowledge of the group.
    preferred_periods : list of str
        A list of artistic periods preferred by the group (e.g., ['Renaissance', 'Baroque']).
    preferred_authors : list of str
        A list of authors/artists preferred by the group (e.g., ['Picasso', 'Dalí']).
    preferred_themes : list of str
        A list of thematic preferences (e.g., ['landscapes', 'portraits']).
    time_coefficient : float
        A coefficient representing time constraints or preferences.
    proposed_paintings : list of str
        The list of paintings included in the proposed route.
    route_score : float
        A guiding score for the route's interest or quality.
    
    Returns
    -------
    str
        A string containing two lines:
        - First line: "Evaluation: n/5"
        - Second line: "Feedback: ..." where ... is a brief feedback text.
    """
    
    openai.api_key = os.getenv("OPENAI_API_KEY")
    
    # Base prompt to guide GPT
    prompt = f"""
    You are an expert in visitor experiences in art museums. Based on the following characteristics of the group and the proposed route, provide an experience evaluation on a scale of 1 to 5, followed by brief feedback reflecting the group's satisfaction.

    Before providing the format, consider the following examples to guide your response:

    - If the group consists of elderly visitors and the route is very long, the feedback might mention fatigue, such as "The route was too exhausting due to its length."
    - If the proposed paintings align well with the group's interests, the feedback might be: "The route was very enjoyable, perfectly aligned with our preferences."
    - If the paintings did not match their interests but the mismatch was not too significant, the feedback could focus on the overall experience, such as: "The visit was enjoyable, though not all paintings resonated with us."
    - If the mismatch is substantial, the feedback might be: "The visit was uninteresting as the artworks did not align with our preferences."
    - If some paintings felt unnecessary and disrupted the flow, the feedback might mention: "Certain paintings could have been omitted to focus on more relevant ones."
    - If the group finds the route too slow: "The visit was too slow; we would have preferred to see more paintings in the same time."

    Note: Most comments should be either generally positive or negative, focusing on the overall satisfaction with the experience. Specific mentions of paintings that did not align should only be included if the mismatch was very significant compared to ther other artworks. The comments related to the route's pace should be based on the group's preferences and the time coefficient provided.

    Now, using the following group and route details, generate your evaluation and feedback:

    **Group characteristics:**
    - Group size: {group_size}
    - Group type: {group_type}
    - Group description: {group_description}
    - Artistic knowledge level: {art_knowledge_level} (1-4) were 1 is low and 4 is high.
    - Preferred periods: {preferred_periods}
    - Preferred authors: {preferred_authors}
    - Preferred themes: {preferred_themes}
    - Time coefficient: {time_coefficient} were 1 is normal speed, <1 is faster, and >1 is slower.

    **Proposed route:**
    - Paintings to visit: {proposed_paintings}
    - Guiding score for the route: {route_score}

    Consider that group satisfaction may be influenced by factors such as perceived quality of the works, emotions experienced during the visit, and the arrangement of exhibitions. Provide a numeric evaluation followed by brief feedback reflecting the group's experience.

    The format of the response must be:

    Evaluation: n/5
    Feedback: 
    """

    # Call to GPT model
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )
    
    # Extract the content of the response
    feedback = response.choices[0].message.content.strip()
    return feedback
