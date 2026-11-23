
import streamlit as st
import random
from datetime import datetime

import database as db
import simulation as sim
from villagers import VILLAGERS

# ==========================================
# CONFIGURATION
# ==========================================

st.set_page_config(
    page_title="Tiny Town AI | Living World",
    page_icon="🏡",
    layout="wide",
    initial_sidebar_state="expanded"
)

db.initialize()

if "chat_history" not in st.session_state:
    st.session_state.chat_history = {}

if "last_event" not in st.session_state:
    st.session_state.last_event = "The town is peaceful."

# ==========================================
# DESIGN SYSTEM
# ==========================================

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap');

.stApp {
    background: #0c111b;
    color: #e8edf5;
    font-family: 'DM Sans', sans-serif;
}

header[data-testid="stHeader"] {
    background: transparent;
}

[data-testid="stSidebar"] {
    background: #131c2a;
    border-right: 1px solid #283449;
}

.block-container {
    max-width: 1450px;
    padding-top: 2rem;
    padding-bottom: 3rem;
}

h1, h2, h3 {
    font-family: 'Space Grotesk', sans-serif;
}

h1 {
    color: #eaf5ff;
    font-size: 2.5rem !important;
}

h2, h3 {
    color: #dceaff;
}

p, label, span {
    color: #c4cfdf;
}

[data-testid="stMetric"] {
    background: #172334;
    border: 1px solid #2b3c53;
    padding: 18px;
    border-radius: 14px;
}

[data-testid="stMetricValue"] {
    color: #7de2b8;
}

[data-testid="stMetricLabel"] {
    color: #aabbd0;
}

.town-banner {
    background: linear-gradient(120deg,#193b35,#1d3048,#302746);
    border: 1px solid #405a69;
    border-radius: 20px;
    padding: 28px;
    text-align: center;
    margin: 12px 0 24px 0;
}

.town-banner h2 {
    color: #ffffff;
    font-size: 28px;
}

.town-banner p {
    color: #bcd8d4;
}

.village-map {
    background: linear-gradient(145deg,#244d3d,#315c45);
    border: 1px solid #527a60;
    border-radius: 20px;
    padding: 22px;
}

.location {
    background: rgba(13,29,25,0.65);
    border: 1px solid rgba(205,255,220,0.15);
    padding: 17px 8px;
    border-radius: 13px;
    text-align: center;
    margin: 5px 0;
    min-height: 82px;
}

.location h3 {
    margin: 0;
    color: #ffffff;
    font-size: 16px;
}

.location p {
    margin: 3px 0 0 0;
    color: #c4dfcc;
    font-size: 12px;
}

.event-card {
    background: #182638;
    border-left: 4px solid #72d8ae;
    border-radius: 9px;
    padding: 13px 16px;
    margin-bottom: 10px;
}

.villager-card {
    background: linear-gradient(145deg,#192a3d,#1b2435);
    border: 1px solid #344a60;
    border-radius: 15px;
    padding: 17px;
    min-height: 170px;
}

.villager-card h3 {
    margin: 0 0 7px 0;
    color: white;
}

.mood {
    color: #83e4b9;
    font-size: 13px;
}

.small-text {
    color: #9eafc5;
    font-size: 12px;
}

.newspaper {
    background: #f0e6ca;
    color: #29261e;
    padding: 25px;
    border-radius: 10px;
}

.newspaper h2, .newspaper p {
    color: #29261e;
}

button[kind="primary"] {
    background: #299c78;
    border-color: #299c78;
}

.stButton button {
    border-radius: 10px;
}

div[data-testid="stTabs"] button {
    color: #cbd8e9;
}

hr {
    border-color: #29374a;
}
</style>
""", unsafe_allow_html=True)

# ==========================================
# HELPER FUNCTIONS
# ==========================================

def get_person(name):
    return next(v for v in VILLAGERS if v["name"] == name)


def show_event(category, description, day):
    colors = {
        "GOSSIP": "💬",
        "FRIENDSHIP": "💚",
        "ARGUMENT": "⚡",
        "MYSTERY": "🔮",
        "ROMANCE": "❤️",
        "FESTIVAL": "🎉",
        "DISCOVERY": "✨"
    }

    icon = colors.get(category, "📌")

    st.markdown(
        f"""
        <div class="event-card">
            <b>{icon} {category} · DAY {day}</b><br>
            {description}
        </div>
        """,
        unsafe_allow_html=True
    )


# ==========================================
# SIDEBAR
# ==========================================

day = db.get_day()
villager_status = db.get_villagers()
events = db.get_events()

st.sidebar.markdown("# 🏡 TINY TOWN")
st.sidebar.caption("THE LIVING WORLD")
st.sidebar.markdown("---")

st.sidebar.markdown("### 🌍 World controls")

st.sidebar.metric("Simulation Day", day)

if st.sidebar.button(
    "⏩ ADVANCE ONE DAY",
    use_container_width=True,
    type="primary"
):
    event = sim.advance_day()
    st.session_state.last_event = event
    st.rerun()

if st.sidebar.button(
    "🎲 Generate another event",
    use_container_width=True
):
    person = random.choice(VILLAGERS)
    day = db.get_day()

    event = (
        f"{person['name']} had an unexpected encounter "
        "that everyone will be talking about."
    )

    db.add_event(day, "DISCOVERY", event)
    db.add_memory(person["name"], event, day)

    st.session_state.last_event = event
    st.rerun()

st.sidebar.markdown("---")

online, models = sim.get_ollama_status()

if online:
    st.sidebar.success("AI ENGINE CONNECTED")

    if sim.MODEL in models:
        st.sidebar.caption(f"Model: {sim.MODEL}")
    else:
        st.sidebar.warning("Model not downloaded yet")
else:
    st.sidebar.warning("AI ENGINE OFFLINE")
    st.sidebar.caption("Install Ollama to activate conversations.")

st.sidebar.markdown("---")
st.sidebar.caption("A tiny world. Infinite stories.")

# ==========================================
# MAIN HEADER
# ==========================================

st.markdown(
    """
    <div class="town-banner">
        <h2>🌲 Welcome to Tiny Town 🌲</h2>
        <p>Every villager has a life. Every decision creates a story.</p>
        <p>THE WORLD NEVER STOPS CHANGING.</p>
    </div>
    """,
    unsafe_allow_html=True
)

# ==========================================
# TOP STATISTICS
# ==========================================

day = db.get_day()
villager_status = db.get_villagers()
events = db.get_events()

c1, c2, c3, c4 = st.columns(4)

c1.metric("👥 Population", "12")
c2.metric("📅 Simulation Day", day)
c3.metric("📰 Total Events", len(events))
c4.metric(
    "💚 Friendships",
    sum(
        1 for a, b, score in db.get_relationships()
        if score >= 25
    )
)

st.markdown("---")

# ==========================================
# NAVIGATION
# ==========================================

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🗺️ Village",
    "👥 Villagers",
    "💬 AI Chat",
    "❤️ Relationships",
    "📰 Newspaper"
])

# ==========================================
# TAB 1: VILLAGE
# ==========================================

with tab1:

    st.header("The Living Village")
    st.caption("Explore the places where your villagers live and work.")

    st.markdown('<div class="village-map">', unsafe_allow_html=True)

    st.markdown(
        """
        <div style="text-align:center;color:white;">
        <h2>🌳 THE TINY TOWN MAP 🌳</h2>
        <p>A peaceful village surrounded by an ancient forest</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    places = [
        [("🌾", "Farm"), ("🏰", "Town Hall"), ("🏥", "Hospital")],
        [("🍲", "Restaurant"), ("⚒️", "Blacksmith"), ("🔮", "Wizard Tower")],
        [("🌻", "Garden"), ("🛒", "Market"), ("🌲", "Forest")],
        [("⚙️", "Workshop"), ("🎨", "Art Studio"), ("🎵", "Music Hall")]
    ]

    for row in places:
        cols = st.columns(3)

        for col, (emoji, name) in zip(cols, row):
            with col:
                st.markdown(
                    f"""
                    <div class="location">
                        <h3>{emoji} {name}</h3>
                        <p>Village location</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("")
    st.subheader("📰 Latest Village Activity")

    if events:
        for event in events[:7]:
            show_event(event[1], event[2], event[0])
    else:
        st.info("Your village is waiting for its first story.")

    st.subheader("✨ Latest Simulation Event")
    st.info(st.session_state.last_event)

# ==========================================
# TAB 2: VILLAGERS
# ==========================================

with tab2:

    st.header("Meet the Residents")
    st.caption("12 individuals. 12 personalities. Countless possibilities.")

    cols = st.columns(3)

    for i, person in enumerate(VILLAGERS):

        status = villager_status[person["name"]]

        with cols[i % 3]:

            st.markdown(
                f"""
                <div class="villager-card">
                    <h3>{person['emoji']} {person['name']}</h3>
                    <b>{person['job']}</b>
                    <p class="mood">😊 {status['mood']}</p>
                    <p class="small-text">{person['personality']}</p>
                    <p class="small-text">🏠 {person['home']}</p>
                    <p class="small-text">⚡ Energy: {status['energy']}%</p>
                </div>
                """,
                unsafe_allow_html=True
            )

            with st.expander(f"Discover {person['name']}"):
                st.write("**Backstory**")
                st.write(person["backstory"])

                st.write("**Dream**")
                st.write(person["goal"])

                st.write("**Private secret**")
                st.write(person["secret"])

                memories = db.get_memories(person["name"])

                st.write("**Memories**")

                if memories:
                    for memory, memory_day in memories:
                        st.write(f"Day {memory_day}: {memory}")
                else:
                    st.caption("No memories yet.")

# ==========================================
# TAB 3: AI CHAT
# ==========================================

with tab3:

    st.header("Talk to the Villagers")
    st.caption("Have a conversation. Ask questions. Discover their personalities.")

    selected = st.selectbox(
        "Choose a villager",
        [p["name"] for p in VILLAGERS]
    )

    person = get_person(selected)

    st.info(
        f"{person['emoji']} **{selected}** · {person['job']} · "
        f"{person['personality']}"
    )

    history = st.session_state.chat_history.setdefault(
        selected, []
    )

    for chat in history:
        with st.chat_message(chat["role"]):
            st.write(chat["content"])

    user_message = st.chat_input(
        f"Talk to {selected}..."
    )

    if user_message:

        history.append({
            "role": "user",
            "content": user_message
        })

        with st.chat_message("user"):
            st.write(user_message)

        with st.chat_message("assistant"):

            with st.spinner(f"{selected} is thinking..."):

                memories = db.get_memories(selected)

                context = "\n".join(
    [f"Day {day_num}: {memory}" for memory, day_num in memories]
)

                reply = sim.ask_ai(
                    selected,
                    user_message,
                    extra_context=context
                )

                st.write(reply)

        history.append({
            "role": "assistant",
            "content": reply
        })

        db.add_memory(
            selected,
            f"You said: {user_message[:200]}. "
            f"{selected} replied: {reply[:250]}",
            db.get_day()
        )

# ==========================================
# TAB 4: RELATIONSHIPS
# ==========================================

with tab4:

    st.header("Social Network")
    st.caption("Friendships and rivalries shape the future of Tiny Town.")

    relationships = db.get_relationships()

    top_relationships = sorted(
        relationships,
        key=lambda x: x[2],
        reverse=True
    )

    for first, second, score in top_relationships[:12]:

        if score >= 25:
            label = "💚 Close friends"
        elif score >= 1:
            label = "🙂 Friendly"
        elif score <= -25:
            label = "💢 Rivals"
        elif score < 0:
            label = "😠 Tension"
        else:
            label = "🤝 Acquaintances"

        st.write(f"**{first} ↔ {second}**")
        st.progress((score + 100) / 200)
        st.caption(f"{label} · Relationship score: {score}")

# ==========================================
# TAB 5: NEWSPAPER
# ==========================================

with tab5:

    st.header("📰 The Tiny Town Times")
    st.caption("The official newspaper of the village.")

    if st.button("🖋️ Generate Today's Newspaper", type="primary"):

        with st.spinner("The town reporter is writing..."):
            article = sim.generate_newspaper()

        st.session_state.newspaper = article

    if "newspaper" in st.session_state:

        st.markdown(
            '<div class="newspaper">',
            unsafe_allow_html=True
        )

        st.markdown(
            "# THE TINY TOWN TIMES"
        )

        st.markdown(
            f"### Edition: Day {db.get_day()}"
        )

        st.markdown("---")

        st.markdown(
            st.session_state.newspaper
        )

        st.markdown("---")

        st.markdown(
            "*Reporting the stories that make Tiny Town special.*"
        )

        st.markdown(
            "</div>",
            unsafe_allow_html=True
        )

    else:
        st.info(
            "Press the button to generate your village's newspaper."
        )

# ==========================================
# FOOTER
# ==========================================

st.markdown("---")

st.markdown(
    """
    <div style="text-align:center;padding:20px;">
        <h3>🏡 TINY TOWN AI</h3>
        <p>A living world powered by artificial intelligence.</p>
        <p style="color:#7890a8;font-size:12px;">
        BUILT WITH PYTHON · STREAMLIT · OLLAMA · SQLITE
        </p>
    </div>
    """,
    unsafe_allow_html=True
)
