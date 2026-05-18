# recommender.py
from groq import Groq
from config import GROQ_API_KEY

client = Groq(api_key=GROQ_API_KEY)

SYSTEM_PROMPT = """You are CineMind — an expert film curator with deep knowledge of world cinema, psychology, and storytelling.

Your job is to recommend exactly 3 movies tailored precisely to the user's mood, situation, or visual context.

For each recommendation follow this format strictly:
🎬 **[Movie Title]** ([Year]) — [Genre]
> [2-sentence reason why THIS person, in THIS mood, needs THIS film]
⭐ Mood match: [e.g. "Perfect for a rainy introspective evening"]
🍿 Watch if you liked: [one similar well-known film]

Rules:
- Never repeat obvious blockbusters unless they genuinely fit.
- Mix at least one underrated/lesser-known gem.
- Match tone: if the user is sad, don't force comedy. If they want fun, skip depressing arthouse.
- If an image is described, extract the visual mood, color palette, and setting — use that to inform genre and tone.
- End with one short line: a bold, specific reason why these 3 together form a perfect watch list for them tonight.
"""

def get_recommendation(user_input, image_description=None):
    if image_description:
        user_message = (
            f"Visual context from uploaded image:\n{image_description}\n\n"
            f"User's message: {user_input}\n\n"
            "Instructions: carefully read ALL the visual context above.\n"
            "- If any brand, franchise, or character is detected (e.g. Marvel, DC, Disney, Star Wars), "
            "prioritise recommending films from that universe or closely related franchises.\n"
            "- Use the dominant colors and tags to infer tone (dark/gritty vs bright/fun).\n"
            "- Use objects and scene description to pick the right genre and era.\n"
            "Give recommendations that feel like a natural extension of what is shown in the image."
        )
    else:
        user_message = user_input

    stream = client.chat.completions.create(
        model="llama-3.3-70b-versatile",  # most capable free model on Groq
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": user_message}
        ],
        temperature=0.85,
        max_tokens=1024,
        stream=True
    )
    for chunk in stream:
        delta = chunk.choices[0].delta.content
        if delta:
            yield delta
