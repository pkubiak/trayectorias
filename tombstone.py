from genai_story import summarize_history
import streamlit as st
from jinja2 import Environment, FileSystemLoader

TOMBSTONE_TEMPLATE = "assets/tombstone.html.jinja2"

def generate_tombstone(user_parameters, user_history) -> str:
    name = user_parameters.get("name", "Nieznany")
    birth_year = user_parameters.get("birth_date", "???").split("-")[0]
    death_year = user_history[-1]["date"].split("-")[0]
    death_age = int(death_year) - int(birth_year) if birth_year.isdigit() and death_year.isdigit() else "???"
    zus_money = 123_000
    summary = summarize_history(user_parameters, user_history, death_age)

    # st.write(name, birth_year, death_year, zus_money)
    # st.write(summary)

    env = Environment(loader=FileSystemLoader("."))
    template = env.get_template(TOMBSTONE_TEMPLATE)

    html_content = template.render(
        name=name,
        birth_year=birth_year,
        death_year=death_year,
        zus_money=zus_money,
        summary=summary.summary,
        quote=summary.quote,
    )

    st.html(html_content)
    return html_content