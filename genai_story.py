
import json
from google.genai import Client, types
import os
from models import EventsList, HistorySummary, PlayerReaction, PlayerAction, Impact


EVENT_PROMPT = """
Wciel się mistrza gry w sesji RPG, na podstawie opisu postaci i skróconej historii jej poczynań zaproponuj kilka możliwych wydarzeń które mogą mieć miejsce w najbliższym czasie.
Bądź precyzyjny w opisie wydarzeń, każde wydarzenie powinno być konkretne. 
Dla każdej propozycji zwróć date i krótki opis wydarzenia oraz to jak wydarzenie wpłynie na parametry postaci.
Weż pod uwagę takie kluczowe informacje o postaci jak: wiek, miejsce zamieszkania, stan zdrowia, poziom energii, zainteresowania, miesięczny dochód, oszczędności.
Teksty generuj w trybie drugiej osoby w czasie teraźniejszym.
"""

REACTION_PROMPT = """
Wciel się mistrza gry w sesji RPG, na podstawie opisu postaci i skróconej historii jej poczynań zaproponuj konieczność decyzji przed którą stanie gracz.
Bądź precyzyjny w opisie, każdy opis powinien być konkretny. 
Zwróc opis sytuacji w której gracz musi podjąć decyzję i zaproponuj 2-3 możliwe reakcje na tę sytuację.
Zwróć krótkie opisy każdej reakcji, bądź precyzyjny i konkretny, nie wspominaj o uczuciach i emocjach.
Weż pod uwagę takie kluczowe informacje o postaci jak: wiek, miejsce zamieszkania, stan zdrowia, poziom energii, zainteresowania, miesięczny dochód, oszczędności,
ale nie wspominaj o nich w opisie sytuacji i reakcji.
Teksty generuj w trybie drugiej osoby liczby pojedynczej w czasie teraźniejszym.
"""

ACTION_PROMPT = """
Wciel się mistrza gry w sesji RPG, na podstawie opisu postaci i skróconej historii jej poczynań zaproponuj kilka (3-4) działań, różniących się skalą i konsekwencjami, które gracz może podjąć w obecnej sytuacji.
Zaproponuj działania które mogą prowadzić do pozytywnych, neutralnych oraz negatywnych rezultatów.
Nie sugeruj w opisie działań jakie będą ich konsekwencje, nie podawaj żadnych wartości liczbowych.
Zwróć krótki opis każdej akcji, bądź precyzyjny i konkretny, nie wspominaj o uczuciach i emocjach.
Weż pod uwagę takie kluczowe informacje o postaci jak: wiek, miejsce zamieszkania, stan zdrowia, poziom energii, zainteresowania, miesięczny dochód, oszczędności,
ale nie wspominaj o nich w opisie akcji.
Teksty generuj w trybie drugiej osoby liczby pojedynczej w czasie teraźniejszym.
"""

SUMMARIZE_HISTORY_PROMPT = """
Podsumuj w kilku zdaniach historię życia postaci na podstawie poniższych punktów. 
Podsumowanie powinno być napisane w języku polskim. Unikaj podawania dat i szczegółów, skup się na kluczowych momentach i ogólnym zarysie życia postaci.
Uwypuklij ważne wydarzenie i zmiany w życiu postaci. Wskaż ważne decyzje i ich konsekwencje. Tekst wygeneruj w trybie drugiej osoby w czasie przeszłym.
Ważne fragment oznacz jako <b> </b>, kluczowe cześci wydziel jako paragrafy <p> </p>.
Uwzględnij wiek postaci w podsumowaniu.
Zakończ podsumowanie cytatem pasującym do życia postaci.
"""

SUMMARIZE_ACTION_PROMPT = """
Podsumuj krótko działenie podjęte przez gracza. 
Zwróć tekst w języku polskim w postaci równoważnika zdania.
Uwzględnij wpływ akcji na postać. Nie używaj średników.
"""

client = Client(api_key=os.environ["API_KEY"])

def ask_gemini(prompt: str, content: str, response_schema) -> str:
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        config=types.GenerateContentConfig(
            system_instruction=prompt.strip(),
            thinking_config=types.ThinkingConfig(thinking_budget=0),
            temperature=0.9,
            response_mime_type='application/json',
            response_schema=response_schema,
        ),
        contents=content,
    )
    text = response.text
    text = text.removeprefix("```json").removesuffix("```").strip()
    
    return text

def generate_event(contents: str):
    return ask_gemini(EVENT_PROMPT, contents, EventsList)


def generate_reaction(contents: str):
    return ask_gemini(REACTION_PROMPT, contents, PlayerReaction)

def generate_action(contents: str):
    return ask_gemini(ACTION_PROMPT, contents, PlayerAction)

def summarize_history(user_parameters, user_history, death_age, style=None) -> str:
    history = []
    for entry in user_history:
        history.append(f"- {entry['date']}: {entry['title']}")
    history = "\n".join(history)
    parameters = "\n".join([f"- {key}: {value}" for key, value in user_parameters.items()])

    death_label = "- death at age: {death_age}\n" if death_age else ""
    content = f"""
## Parameters
{parameters}
{death_label}

## History
{history}
""".strip()
    # import streamlit as st
    # st.write(content)
    
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        config=types.GenerateContentConfig(
            system_instruction=SUMMARIZE_HISTORY_PROMPT + (f"\n{style}" if style else ""),
            thinking_config=types.ThinkingConfig(thinking_budget=0),
            temperature=0.9,
            response_mime_type='application/json',
            response_schema=HistorySummary,
        ),
        contents=content,
    )

    return HistorySummary.model_validate_json(response.text)


def summarize_action(text: str, action: str, impacts: list[Impact]) -> str:
    parts = []
    if text:
        parts.append(f"Sytuacja: {text}")
    parts.append(f"Podjęta akcja: {action}")
    if impacts:
        parts.append(f"Wływ na postać: {json.dumps([impact.model_dump() for impact in impacts], ensure_ascii=False)}")
    
    return ask_gemini(SUMMARIZE_ACTION_PROMPT, "\n\n".join(parts), str)
    # import streamlit as st
    # st.write("\n\n".join(parts))
