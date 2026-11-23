
import random
import requests

import database as db
from villagers import VILLAGERS

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL = "llama3.2:3b"


def get_profile(name):
    return next(v for v in VILLAGERS if v["name"] == name)


def ask_ai(name, message, extra_context=""):
    """Talk to a villager using the local Ollama model."""

    profile = get_profile(name)
    memories = db.get_memories(name)

    memory_text = "\n".join(
        [f"Day {day}: {memory}" for memory, day in memories]
    )

    system_prompt = f"""
You are {profile['name']}, a resident of Tiny Town.

JOB: {profile['job']}
PERSONALITY: {profile['personality']}
BACKSTORY: {profile['backstory']}
PRIVATE SECRET: {profile['secret']}
PERSONAL GOAL: {profile['goal']}

YOUR MEMORIES:
{memory_text if memory_text else "You have just started your adventure."}

OTHER CONTEXT:
{extra_context}

Rules:
- Stay in character.
- Speak naturally, like a real person.
- Remember previous events and conversations.
- Never claim to have done something that did not happen.
- Do not reveal your private secret immediately.
- Keep responses between 2 and 5 sentences.
- You live inside a fictional village simulation.
"""

    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": MODEL,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": message}
                ],
                "stream": False,
                "options": {"temperature": 0.85}
            },
            timeout=100
        )

        response.raise_for_status()

        answer = response.json().get("message", {}).get("content", "")

        if not answer.strip():
            return "I'm not sure what to say right now. Can you ask me again?"

        return answer.strip()

    except requests.exceptions.ConnectionError:
        return (
            "I can't think clearly right now. My connection to the village's "
            "AI brain seems unavailable. Is Ollama running?"
        )

    except requests.exceptions.Timeout:
        return "Hmm... give me a moment. I'm thinking very hard!"

    except requests.exceptions.RequestException:
        return "I'm having trouble connecting to my AI brain right now."

    except Exception as error:
        return f"Something went wrong: {error}"


def generate_newspaper():
    events = db.get_events(12)

    if not events:
        return "The village is peaceful today. Nothing unusual has happened yet."

    event_text = "\n".join(
        [f"Day {day}: {description}" for day, category, description in events]
    )

    prompt = f"""
You are the editor of THE TINY TOWN TIMES.

Write a fun fictional village newspaper based ONLY on these actual events:

{event_text}

Include:
- A dramatic headline
- Three short news stories
- A gossip column
- A closing line

Do not invent major events that are not in the event list.
Keep it entertaining and easy to read.
"""

    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": MODEL,
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "stream": False,
                "options": {"temperature": 0.7}
            },
            timeout=100
        )

        response.raise_for_status()

        newspaper = response.json().get("message", {}).get("content", "")

        if newspaper.strip():
            return newspaper.strip()

    except Exception:
        pass

    return (
        "THE TINY TOWN TIMES\n\n"
        "The village continues to surprise its residents!\n\n"
        + "\n".join(
            [f"• {event[2]}" for event in events[:5]]
        )
    )


def advance_day():
    day = db.get_day() + 1
    db.set_day(day)

    people = VILLAGERS
    first, second = random.sample(people, 2)

    scenarios = [
        (
            "GOSSIP",
            f"{first['name']} was seen whispering with "
            f"{second['name']} near the market.",
            5
        ),
        (
            "FRIENDSHIP",
            f"{first['name']} and {second['name']} spent time together "
            "and became closer.",
            12
        ),
        (
            "ARGUMENT",
            f"{first['name']} and {second['name']} had a disagreement "
            "in the village square.",
            -10
        ),
        (
            "MYSTERY",
            f"{first['name']} discovered something strange near the forest.",
            0
        ),
        (
            "ROMANCE",
            f"{first['name']} left a mysterious gift for "
            f"{second['name']}.",
            8
        ),
        (
            "FESTIVAL",
            f"{first['name']} suggested organizing a village celebration "
            f"with {second['name']}.",
            5
        ),
        (
            "DISCOVERY",
            f"{first['name']} made an unexpected discovery during work.",
            0
        )
    ]

    category, description, score = random.choice(scenarios)

    # Save event
    db.add_event(day, category, description)

    # Update relationship
    if score != 0:
        db.change_relationship(
            first["name"],
            second["name"],
            score
        )

    # Save memories for both villagers
    db.add_memory(first["name"], description, day)
    db.add_memory(second["name"], description, day)

    # Update villagers' moods and energy
    villagers_status = db.get_villagers()

    for person in people:
        mood = random.choice([
            "Happy",
            "Excited",
            "Calm",
            "Curious",
            "Tired"
        ])

        current_energy = villagers_status[person["name"]]["energy"]

        energy = max(
            10,
            min(100, current_energy + random.randint(-15, 10))
        )

        db.update_villager(
            person["name"],
            mood,
            energy
        )

    return description


def get_ollama_status():
    try:
        response = requests.get(
            "http://localhost:11434/api/tags",
            timeout=3
        )

        response.raise_for_status()

        models = response.json().get("models", [])

        model_names = [
            model["name"] for model in models
        ]

        return True, model_names

    except Exception:
        return False, []
