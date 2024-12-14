import os
import openai
from dotenv import load_dotenv

def generate_group_description(num_people: int,
                               favorite_author: str,
                               favorite_period: int,
                               favorite_theme: str,
                               guided_visit: bool,
                               minors: bool,
                               num_experts: int,
                               past_museum_visits: int,
                               model: str = "gpt-3.5-turbo") -> str:
    """
    Generate a first-person English description of a museum visitor group,
    incorporating their hobbies, who they are, and their interests, based on given parameters.

    Parameters
    ----------
    num_people : int
        Total number of people in the group.
    favorite_author : str
        The group's favorite author or artist.
    favorite_period : int
        A representative year of the group's preferred artistic period.
    favorite_theme : str
        The group's preferred artistic theme.
    guided_visit : bool
        Whether the group prefers a guided visit.
    minors : bool
        Whether the group includes children under 12.
    num_experts : int
        How many group members are expert-level in art.
    past_museum_visits : int
        How many museums the group has visited before.
    model : str, optional
        The LLM model to use (default: "gpt-3.5-turbo").

    Returns
    -------
    str
        A first-person narrative paragraph describing the group, their hobbies, and interests.
    """
    # Load the OpenAI API key from the .env file
    load_dotenv()
    client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


    # Construct a prompt that encourages a first-person, collective narrative.
    # The prompt should reflect all the given characteristics and add some "invented" details,
    # like hobbies or what they enjoy, while remaining coherent.
    prompt = f"""
You are a creative writer. Write a very short, first-person English description from the perspective of a group visiting a museum.
Create an invent description of the group not repeating the characteristics given but using them to create a natural-sounding introduction.
Do not mention the exact artist or year just use the vibes to create the hobbies.

**Group Characteristics:**
- Number of people: {num_people}
- Children under 12 present: {"Yes" if minors else "No"}
- Guided visit preferred: {"Yes" if guided_visit else "No"}
- Number of art experts in the group: {num_experts}
- Past museum visits: {past_museum_visits}
- Favorite artistic period (represented by year): {favorite_period}
- Favorite author/artist: {favorite_author}
- Favorite theme: {favorite_theme}

Write a very short invented description of what this group could look like, invent hobbies or interests that could be related to the characteristics given not related to the museums.
Do not mention all the information just the vibes of the group as it must be very very short.

Examples of group descriptions:
1. "We are a group of young professionals who enjoy art and music."
2. "A family of four with two young children who are curious and playful."
3. "A group of old enthusiastic book club members who love discussing literature."
4. "A small group of elderly scholars who are meticulous and reflective."
5. "We are a lively band of teenagers who love music festivals and concerts."
6. "Small group of business executives in their forties visiting for a quick corporate retreat."
7. "We are a duo of adventure-seeking college roommates who love hiking and exploring."
8. "We are a tightly-knit community of recent graduates exploring career opportunities."

Finally the description must be as short as the ones provided as examples, not longer. VERY SHORT!
    """

    # Call to GPT model
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=1.5
    )

    # Extract the content of the response
    description = response.choices[0].message.content.strip()
    return description

# Example usage:
"""if __name__ == "__main__":
    desc = generate_group_description(
        num_people=4,
        favorite_author="Van Gogh",
        favorite_period=1850,
        favorite_theme="horror",
        guided_visit=True,
        minors=False,
        num_experts=1,
        past_museum_visits=2
    )

    print("Generated Description:\n", desc)"""