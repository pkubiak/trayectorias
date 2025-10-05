import streamlit as st
import json, os

import datetime, random
import enum
import typing as T
from models import Impact, EventsList, PlayerReaction, DEFAULT_PLAYER, PlayerAction, DEFAULT_HISTORY, DEFAULT_DATE, EVENT_TYPES
from utils import apply_impact
from genai_story import generate_event, generate_reaction, generate_action, summarize_action, summarize_history
from tombstone import generate_tombstone
from PIL import Image
from user_creator import user_creator

st.html("styles.css")

# st.set_page_config(page_title="Trayectorias", page_icon="🧬", layout="centered", initial_sidebar_state="collapsed")

if "current_date" not in st.session_state:
    user_creator()


user_parameters = st.session_state["user_parameters"]
current_date = st.session_state["current_date"]
user_history = st.session_state["user_history"]


user_parameters["age"] = (datetime.datetime.strptime(current_date, "%Y-%m-%d") - datetime.datetime.strptime(user_parameters["birth_date"], "%Y-%m-%d")).days // 365 

def change_event_type():
    if "response" in st.session_state:
        del st.session_state["response"]

with st.sidebar:
    with st.expander("Debug"):
        cols = st.columns(2, vertical_alignment="bottom")
        event_type = cols[0].selectbox("Wybierz typ wydarzeń:", EVENT_TYPES)
        event_sentiment = cols[1].selectbox("Wybierz sentyment wydarzeń:", ["positive", "neutral", "negative", "fatal"])
        custom = st.text_input("Niestandardowy opis wydarzenia:", placeholder="np. 'a job interview'")
        st.text(f"{event_type}, {event_sentiment}")
        with st.container(horizontal=True):
            if st.button("Event"):
                st.session_state["response_type"] = "event"
                st.session_state["custom"] = custom
                change_event_type()
            if st.button("Reaction"):
                st.session_state["response_type"] = "reaction"
                st.session_state["custom"] = custom
                change_event_type()
            if st.button("Action"):
                st.session_state["response_type"] = "action"
                st.session_state["custom"] = custom
                change_event_type()
                
    with st.expander("Parameters"):
        st.table(user_parameters)
    with st.expander("History"):
        st.write(user_history)


if user_parameters["health_level"]["value"] <= 0:
    generate_tombstone(user_parameters, user_history)
    st.stop()

def health_fn(age):
    x = age
    a4 = 2.43056e-7
    a3 = -4.40972e-5
    a2 = 2.47222e-3
    a1 = -8.375e-2
    a0 = 2.0
    
    return a4 * x**4 + a3 * x**3 + a2 * x**2 + a1 * x + a0

def time_progression(current_date, target_date, user_parameters):

    current_date = datetime.datetime.strptime(current_date, "%Y-%m-%d")
    target_date = datetime.datetime.strptime(target_date, "%Y-%m-%d")
    st.write(current_date, target_date)
    while current_date < target_date:
        # last day of month
        if (current_date + datetime.timedelta(days=1)).day == 1:
            # Przychody
            for k, v in user_parameters["monthly_income"].items():
                user_parameters["savings"]["bank_account"] += v

            # Wydatki
            for k, v in user_parameters["monthly_outcome"].items():
                if v > user_parameters["savings"]["bank_account"]:
                    v -= user_parameters["savings"]["bank_account"]
                    user_parameters["savings"]["bank_account"] = 0
                    user_parameters["savings"]["cash"] -= v
                else:
                    user_parameters["savings"]["bank_account"] -= v

            # Inwestycje
            for k, v in user_parameters["investments"].items():
                if k == "shares":
                    user_parameters["investments"][k] += int(v * random.uniform(-0.01, 0.02))
                elif k == "bonds":
                    user_parameters["investments"][k] += int(v * 0.005)  # 0.5% zwrotu
                elif k == "crypto":
                    user_parameters["investments"][k] = v * random.gauss(1.0, 0.01)
                elif k == "real_estate":
                    user_parameters["investments"][k] += int(v * 0.002)  # 0.2% zwrotu

            # Emerytura
            if "employment_contract" in user_parameters["monthly_income"]:
                user_parameters["savings"]["retirement_account"] += int(user_parameters["monthly_income"]["employment_contract"] * 0.18)
        current_date += datetime.timedelta(days=1)

def forward_history(date: str, title: str, impacts: list[Impact], current_date, user_parameters):
    if not isinstance(date, str):
        date = date.strftime("%Y-%m-%d")
    if not isinstance(current_date, str):
        current_date = current_date.strftime("%Y-%m-%d")

    st.session_state["user_history"].append({"date": date, "title": title})

    time_progression(current_date, date, user_parameters)

    age = 21
    if age < 30:
        multiplier = 1
    elif age < 40:
        multiplier = 1.5
    elif age < 50:
        multiplier = 2
    elif age < 70: 
        multiplier = 3
    else:
        multiplier = 5
    days = random.randint(7, 30) * multiplier

    next_date = datetime.datetime.strptime(date, "%Y-%m-%d") + datetime.timedelta(days=days) # FIXME: zmienić progresję czasu na bardziej realistyczną
    next_date = next_date.strftime("%Y-%m-%d")
    st.session_state["current_date"] = next_date

    show_impacts(impacts) 
    for impact in impacts:
        # st.write(impact)
        assert impact.parameter in st.session_state["user_parameters"]
        current_value = st.session_state["user_parameters"][impact.parameter]
        new_value = apply_impact(current_value, impact)
        st.session_state["user_parameters"][impact.parameter] = new_value
    
    time_progression(current_date, next_date, user_parameters)

    del st.session_state["response"]
    del st.session_state["response_type"]
    st.rerun()


def material_icon(name: str) -> str:
    icon_mapping = {
        "health":"health_metrics",
        "friends": "diversity_3",
        "education": "school",
        "love": "bookmark_heart",
        "family": "family_restroom",
    }
    if name in icon_mapping:
        name = icon_mapping[name]
    return f":material/{name}:"

TRANSLATIONS = {
    "rent": "czynsz",
    "food": "jedzenie",
    "utilities": "media",
    "transportation": "transport",
    "entertainment": "rozrywka",
    "shares": "akcje",
    "bonds": "obligacje",
    "crypto": "kryptowaluty",
    "real_estate": "nieruchomości",
    "medical_consultations": "konsultacje medyczne",
    "medications": "leki",
    "health_insurance": "ubezpieczenie zdrowotne",
    "employment_contract": "umowa o pracę",
    "freelance": "działalność gospodarcza",
    "cash": "gotówka",
    "bank_account": "konto bankowe",
    "retirement_account": "konto emerytalne",
}

def show_avatar(avatar_file: str, age: int, mood: str):
    cols = [20, 40, 60, 80, 1000]
    for i in range(len(cols) - 1):
        if cols[i+1] > age:
            col_id = i
            break
    
    row_id = [":)", ":|", ":("].index(mood)
    image = Image.open(avatar_file)
    cropped = image.crop((col_id*296 + 8, row_id*288+4, (col_id+1)*296 - 16, (row_id+1)*288-8))
    st.image(cropped)

    
def show_hud(user_parameters):
    age = user_parameters["age"]
    st.slider("Age", min_value=0, max_value=120, value=age, disabled=True, label_visibility="collapsed", key='life-slider')
    with st.container(key="hud", border=True):
        cols = st.columns([1,2,2], vertical_alignment="center")
        health = user_parameters["health_level"]["value"]
        energy = user_parameters["energy_level"]["value"]
        if health >= 70 and energy >= 70:
            mood = ":)"
        elif health <= 20 or energy <= 20:
            mood = ":("
        else:
            mood = ":|"

        mood_mapping = {
            ":)": "😊",
            ":|": "😐",
            ":(": "☹️",
        }
        with cols[0]:
            avatar_file = "static/avatars/20251005074740.png" if user_parameters["gender"] == "male" else "static/avatars/20251005073909.png"
            show_avatar(avatar_file, age=age, mood=mood)

        age = user_parameters["age"]
        cols[1].markdown(f"📅 **{current_date}** ⏳ **{age} lat** {mood_mapping[mood]}")
        cols[1].progress(user_parameters["health_level"]["value"]/100, text="Poziom zdrowia")
        cols[1].progress(max(0.0, user_parameters["energy_level"]["value"]/100), text="Poziom energii")
        
        with cols[2].container( key="vertical-buttons"):
            tabs =st.segmented_control(
                "Tool",
                options=["Bio", "Przychody", "Wydatki", "Oszczędności", "Inwestycje", "Umiejętności"],
                selection_mode="single",
                label_visibility="collapsed",
            )
    if tabs is None:
        return
    
    with st.container(border=True):
        if tabs == "Bio":
            with st.spinner("Podsumowywanie historii...", ):
                history = summarize_history(user_parameters, user_history, death_age=None, style="Zwróć jeden akapit tekstu")
            st.html(history.summary)
        elif tabs == "Umiejętności":    
            skills = list(user_parameters.get("skills", []))
            text = [f":blue-badge[{skill}]" for skill in skills]
            st.markdown(" ".join(text))
        else:
            keys_map = {
                "Przychody": "monthly_income",
                "Wydatki": "monthly_outcome",
                "Oszczędności": "savings",
                "Inwestycje": "investments",
            }[tabs]
            
            columns = []
            COLS = 3
            for i in range(0, len(user_parameters[keys_map]), COLS):
                columns.extend(st.columns(COLS))

            for i, (key, value) in enumerate(user_parameters[keys_map].items()):
                columns[i].metric(TRANSLATIONS.get(key, key), f"{value:,} PLN")


    # st.write(tabs)

    # cols = st.columns([1,4], vertical_alignment="center")
    # cols[0].metric("📅 Current date", current_date)
    # 

def show_banner(key: str):
    if os.path.exists(f"static/{key}.png"):
        st.html(f'<div style="height:120px;width:100;overflow:hidden"><div style="height:100%;width:100%;background:url(\'/app/static/{key}.png\') center/cover no-repeat;transform:scale(1.1)"></div></div>')
    else:
        pass
        # st.info(f"Brak baneru dla klucza {key}")

def nice_text(text: str):
    st.html(f"<p style='font-size: 1.25rem; font-weight:300; text-align:justify; -moz-hyphens: auto;-webkit-hyphens: auto;-ms-hyphens: auto;hyphens: auto;'>{text}</p>")

def show_impacts(impacts: list[Impact]):
    output = []
    with st.container(horizontal=True,):
        for impact in impacts:
                icon = {"add": "+=", "sub": "-=", "set": "="}[impact.operation]
                var = impact.parameter
                if impact.key:
                    var = f"{var}[{impact.key}]"
                # st.badge(f"{var} **{icon}** {impact.value}")
                output.append(f":blue-badge[{var} **{icon}** {impact.value}]")

    msg = " ".join(output)
    if msg:
        st.toast(msg, icon="ℹ️", duration="long")

def handle_event():
    global current_date, event_type, event_sentiment, user_parameters, user_history

    if "response" not in st.session_state:
        contents = f"<event-type>{event_type}</event-type>\n\n<event-sentiment>{event_sentiment}</event-sentiment>\n\n<current-date>{current_date}</current-date>\n\n<user>{json.dumps(user_parameters, ensure_ascii=False)}</user>\n\n<history>{json.dumps(user_history, ensure_ascii=False)}</history>"
        if "custom" in st.session_state and st.session_state["custom"]:
            contents += f"\n\n<additional-requirements>{st.session_state['custom']}</additional-requirements>"
            del st.session_state["custom"]
        response_text = generate_event(contents)
        
        with st.expander("Input content:"):
            st.write(contents)
        with st.expander("Raw response:"):
            st.write(response_text  )
        response_model = EventsList.model_validate_json(response_text) 
        st.session_state["response"] = random.choice(response_model.events)
        st.session_state["response_key"] = f"{event_sentiment}_{event_type}"
        st.rerun()
    else:
        item = st.session_state["response"]
        
        st.subheader(f"{material_icon(item.material_icon)} {item.date} - {item.title}")
        show_banner(st.session_state["response_key"])
        nice_text(item.short_description)
        # show_impacts(item.player_impact)

        if st.button("Kontynuuj", use_container_width=True):
            forward_history(item.date, f"{item.title} - {item.short_description}", item.player_impact, current_date, user_parameters)

def handle_action():
    global current_date, event_type, event_sentiment, user_parameters, user_history

    if "response" not in st.session_state:
        payload = f"<action-topic>{event_type}</action-topic>\n\n<current-date>{current_date}</current-date>\n\n<user>{json.dumps(user_parameters, ensure_ascii=False)}</user>\n\n<history>{json.dumps(user_history, ensure_ascii=False)}</history>"
        if "custom" in st.session_state and st.session_state["custom"]:
            payload += f"\n\n<additional-requirements>{st.session_state['custom']}</additional-requirements>"
            del st.session_state["custom"]
        response_text = generate_action(payload)
        

        st.session_state["response"] = PlayerAction.model_validate_json(response_text) 
        st.session_state["response_key"] = f"neutral_{event_type}"
        st.rerun()
    else:
        response_model = st.session_state["response"]
        st.subheader(f"{material_icon(response_model.material_icon)} {response_model.date} Pora do działania!")
        show_banner(st.session_state["response_key"])
        # st.write(response_model)

        with st.container(key='buttons'):
            for action in response_model.actions:
                if st.button(action.short_description, use_container_width=True):
                    summary = summarize_action("", action.short_description, action.player_impact)
                    forward_history(response_model.date, summary, action.player_impact, current_date, user_parameters)
                    # forward_history(response_model.date, action.short_description, action.player_impact)


def handle_reaction():
    global current_date, event_type, event_sentiment, user_parameters, user_history

    if "response" not in st.session_state:
        contents = f"<reaction-kind>{event_type}</reaction-kind>\n\n<reaction-sentiment>{event_sentiment}</reaction-sentiment>\n\n<current-date>{current_date}</current-date>\n\n<user>{json.dumps(user_parameters, ensure_ascii=False)}</user>\n\n<history>{json.dumps(user_history, ensure_ascii=False)}</history>"
        if "custom" in st.session_state and st.session_state["custom"]:
            contents += f"\n\n<additional-requirements>{st.session_state['custom']}</additional-requirements>"
            del st.session_state["custom"]
        response_text = generate_reaction(contents)
        st.session_state["response"] = PlayerReaction.model_validate_json(response_text) 
        st.session_state["response_key"] = f"{event_sentiment}_{event_type}"
        st.rerun()
    else:
        response_model = st.session_state["response"]

        st.subheader(f"{material_icon(response_model.material_icon)} {response_model.date} - {response_model.title}")
        show_banner(st.session_state["response_key"])
        nice_text(response_model.short_description)

        with st.container(key='buttons'):
            for item in response_model.reactions:
                if st.button(item.description, width="stretch"):
                    summary = summarize_action(response_model.short_description, item.description, item.player_impact)
                    forward_history(response_model.date, summary, item.player_impact, current_date, user_parameters)
                    # forward_history(response_model.date, f"{response_model.title} - {item.description}", item.player_impact)

show_hud(user_parameters=user_parameters)

response_type = st.session_state.get("response_type")

if response_type is None:
    event_type = random.choice(EVENT_TYPES)
    event_sentiment = random.choice(["positive", "neutral", "negative", "fatal"])
    st.session_state["response_type"] = response_type = random.choice(["event", "action", "reaction"])

if response_type == "event":
    handle_event()
elif response_type == "action":
    handle_action()
elif response_type == "reaction":
    handle_reaction()
else:
    st.info("Wybierz typ wydarzeń lub reakcji")