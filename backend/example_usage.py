#!/usr/bin/env python
"""
Example script demonstrating the Freestyle Callificator API.
This shows how to create a battle, get verses, and rate them.
"""

import requests
import json
from typing import Dict, Any

BASE_URL = "http://localhost:8000/api"


def create_battle_from_text(battle_data: Dict[str, Any]) -> Dict[str, Any]:
    """Create a battle from already-transcribed text."""
    url = f"{BASE_URL}/battles/text"
    response = requests.post(url, json=battle_data)
    response.raise_for_status()
    return response.json()


def get_battle(battle_id: int) -> Dict[str, Any]:
    """Get a battle with all its verses."""
    url = f"{BASE_URL}/battles/{battle_id}"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()


def get_battle_verses(battle_id: int) -> list:
    """Get all verses of a battle with rhyme metrics."""
    url = f"{BASE_URL}/verses/battle/{battle_id}"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()


def rate_verse(verse_id: int, rating_data: Dict[str, Any]) -> Dict[str, Any]:
    """Rate a verse."""
    url = f"{BASE_URL}/ratings/verse/{verse_id}"
    response = requests.post(url, json=rating_data)
    response.raise_for_status()
    return response.json()


def get_verse_rating_stats(verse_id: int) -> Dict[str, Any]:
    """Get average ratings for a verse."""
    url = f"{BASE_URL}/ratings/verse/{verse_id}/stats"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()


def main():
    """Run example demonstration."""
    print("=" * 60)
    print("Freestyle Callificator - API Example")
    print("=" * 60)

    # Step 1: Create a battle from text
    print("\n1️⃣  Creating a battle from transcribed text...")

    battle_input = {
        "title": "FMS Argentina 2024 - Fecha 1",
        "description": "Batalla de prueba entre MC1 y MC2",
        "verses": [
            {
                "verse_number": 1,
                "speaker": "MC1",
                "text": "Yo vengo de la calle donde todo es distinto, representando el barrio con mi estilo bien finto, "
                        "miro al frente sin miedo aunque el rival sea malo, en este micrófono es donde yo soy un caballo",
                "duration_seconds": 30
            },
            {
                "verse_number": 2,
                "speaker": "MC2",
                "text": "Vos hablas de la calle pero aquí no te conocen, en mi barrio paso cosas que en el tuyo nunca pasan, "
                        "tengo rimas multisilábicas que te desorientan, con mi flow tan elegante todos mis rimas presenten",
                "duration_seconds": 30
            },
            {
                "verse_number": 3,
                "speaker": "MC1",
                "text": "Dijiste que no me conocen pero mira quien habla, alguien que vive en el centro sin bajarse a la cancha, "
                        "tus rimas son aburridas, predecibles y fangosas, mientras yo traigo densidad, complejidad y hermosa",
                "duration_seconds": 30
            },
        ]
    }

    try:
        battle = create_battle_from_text(battle_input)
        battle_id = battle["id"]
        print(f"✅ Battle created successfully! ID: {battle_id}")
        print(f"   Title: {battle['title']}")
        print(f"   Status: {battle['status']}")
    except Exception as e:
        print(f"❌ Error creating battle: {e}")
        return

    # Step 2: Get the battle with all verses
    print("\n2️⃣  Fetching battle details and verses...")

    try:
        verses = get_battle_verses(battle_id)
        print(f"✅ Retrieved {len(verses)} verses")

        for verse in verses:
            print(f"\n   Verse {verse['verse_number']} by {verse['speaker']}:")
            print(f"   Text: {verse['text'][:60]}...")

            if verse.get("rhyme_metric"):
                metrics = verse["rhyme_metric"]
                print(f"   📊 Rhyme Metrics:")
                print(f"      - Density: {metrics['rhyme_density']:.2%}")
                print(f"      - Multisyllabic Ratio: {metrics['multisyllabic_ratio']:.2%}")
                print(f"      - Internal Rhymes: {metrics['internal_rhymes_count']}")
                print(f"      - Diversity: {metrics['rhyme_diversity']:.2f}/1.0")

    except Exception as e:
        print(f"❌ Error fetching verses: {e}")
        return

    # Step 3: Rate some verses
    print("\n3️⃣  Users rating verses...")

    # User 1 rates verse 1
    try:
        verse_1_id = verses[0]["id"]
        rating_1 = rate_verse(
            verse_1_id,
            {
                "user_id": "user_alice_123",
                "rating_rhyme": 4.5,
                "rating_ingenio": 4.0,
                "rating_punchline": 4.5,
                "rating_respuesta": 3.5,
                "comment": "Excelentes rimas multisilábicas, muy técnico"
            }
        )
        print(f"✅ User 'alice' rated verse 1")
    except Exception as e:
        print(f"❌ Error rating verse: {e}")
        return

    # User 2 rates verse 1
    try:
        rating_2 = rate_verse(
            verse_1_id,
            {
                "user_id": "user_bob_456",
                "rating_rhyme": 5.0,
                "rating_ingenio": 5.0,
                "rating_punchline": 4.0,
                "rating_respuesta": 4.0,
                "comment": "Increíble, muy bien ejecutado"
            }
        )
        print(f"✅ User 'bob' rated verse 1")
    except Exception as e:
        print(f"❌ Error rating verse: {e}")
        return

    # User 3 rates verse 1
    try:
        rating_3 = rate_verse(
            verse_1_id,
            {
                "user_id": "user_charlie_789",
                "rating_rhyme": 4.0,
                "rating_ingenio": 3.5,
                "rating_punchline": 4.0,
                "rating_respuesta": 3.0,
                "comment": "Bueno pero podría mejorar"
            }
        )
        print(f"✅ User 'charlie' rated verse 1")
    except Exception as e:
        print(f"❌ Error rating verse: {e}")
        return

    # Step 4: Get rating statistics
    print("\n4️⃣  Getting crowdsourced rating statistics...")

    try:
        stats = get_verse_rating_stats(verse_1_id)
        print(f"✅ Verse {verse_1_id} Rating Statistics (from {stats['total_ratings']} users):")
        print(f"   - Avg Rhyme Rating: {stats['avg_rating_rhyme']:.1f}/5.0")
        print(f"   - Avg Ingenio Rating: {stats['avg_rating_ingenio']:.1f}/5.0")
        print(f"   - Avg Punchline Rating: {stats['avg_rating_punchline']:.1f}/5.0")
        print(f"   - Avg Respuesta Rating: {stats['avg_rating_respuesta']:.1f}/5.0")
    except Exception as e:
        print(f"❌ Error fetching stats: {e}")
        return

    # Summary
    print("\n" + "=" * 60)
    print("✨ Example completed successfully!")
    print("=" * 60)
    print(f"""
Key Insights:
1. Machine-Generated Metrics (from analysis/rhyme/):
   - Rhyme Density: {verses[0]['rhyme_metric']['rhyme_density']:.2%}
   - Multisyllabic Ratio: {verses[0]['rhyme_metric']['multisyllabic_ratio']:.2%}

2. Human Crowdsourced Ratings:
   - {stats['total_ratings']} users rated verse 1
   - Average rhyme quality: {stats['avg_rating_rhyme']:.1f}/5.0

3. The system now has:
   ✅ Automatic technical analysis
   ✅ Human validation data
   ✅ Multiple perspectives for training future models
""")


if __name__ == "__main__":
    main()
