import streamlit as st
from models import DEFAULT_DATE, DEFAULT_HISTORY, DEFAULT_PLAYER, DEFAULT_HISTORY_AGNIESZKA, DEFAULT_PLAYER_AGNIESZKA
def user_creator():
    st.title("Wybierz swoją postać:")
    cols = st.columns(2)
    with cols[0]:
        st.image("static/avatars/b3e5db5a3bf1399f74500a6209462794.jpg")
        if st.button("Andrzej (21 lat)", width="stretch"):
            st.session_state["current_date"] = DEFAULT_DATE
            st.session_state["user_history"] = DEFAULT_HISTORY
            st.session_state["user_parameters"] = DEFAULT_PLAYER
            st.rerun()
    
    with cols[1]:
        st.image("static/avatars/8c6ddb5fe6600fcc4b183cb2ee228eb7.jpg")
        if st.button("Agnieszka (25 lat)", width="stretch"):
            st.session_state["current_date"] = DEFAULT_DATE
            st.session_state["user_history"] = DEFAULT_HISTORY_AGNIESZKA
            st.session_state["user_parameters"] = DEFAULT_PLAYER_AGNIESZKA
            st.rerun()

    st.stop()

    
