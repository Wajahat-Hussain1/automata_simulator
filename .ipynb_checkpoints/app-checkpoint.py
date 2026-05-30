import streamlit as st
from graphviz import Digraph
import time
import json
from google import genai
from google.genai import types
from pydantic import BaseModel, Field
from typing import List, Dict

st.set_page_config(layout="wide")

# --- 1. CLEAN AI STRUCTURED DATA SCHEMA (NO EPSILON) ---
class TransitionEntry(BaseModel):
    from_state: str = Field(description="The source state, e.g., 'q0'")
    symbol: str = Field(description="The input alphabet character, e.g., '0' or '1'")
    to_states: List[str] = Field(description="List of target states reached on this input character")

class SmartAutomataSchema(BaseModel):
    detected_input_format: str = Field(description="Must be explicitly classified as either 'Diagram' or 'Table'")
    machine_type: str = Field(description="Must be explicitly classified as either 'DFA' or 'NFA'")
    states: List[str] = Field(description="List of all unique states parsed from the image")
    alphabet: List[str] = Field(description="List of input language symbols found (e.g., ['0', '1'])")
    initial_state: str = Field(description="The designated starting state")
    final_states: List[str] = Field(description="List of all final/accepting states")
    transitions: List[TransitionEntry] = Field(description="Complete tracking list of all standard structural transitions")

# --- 2. AUTOMATA LOGIC CORE (CLEAN NFA/DFA) ---
def render_automaton(config, active_states=None):
    if active_states is None:
        active_states = set()
    dot = Digraph(comment='Automata Map')
    dot.attr(rankdir='LR')
    
    dot.node('start', shape='point', width='0')
    if config["initial_state"]:
        dot.edge('start', config["initial_state"])
    
    for state in config["states"]:
        if not state.strip():
            continue
        shape = "doublecircle" if state in config["final_states"] else "circle"
        if state in active_states:
            dot.node(state, shape=shape, style="filled", fillcolor="#90CAF9", color="#1E88E5", penwidth="3")
        else:
            dot.node(state, shape=shape, style="solid")
            
    for from_state, trans in config["transitions"].items():
        for symbol, to_states_list in trans.items():
            for to_state in to_states_list:
                if to_state:
                    dot.edge(from_state, to_state, label=symbol)
    return dot

# --- 3. STATE SYNCHRONIZATION ---
if "smart_ai_payload" not in st.session_state:
    st.session_state.smart_ai_payload = None

st.title("🤖 Intelligent Vision-Driven NFA/DFA Automata Simulator")
st.markdown("### Classifies, Parses, and Simulates Handwritten Diagrams or Tables Automatically")
st.divider()

col1, col2 = st.columns([1, 1.2], gap="large")

is_config_valid = True

with col1:
    st.header("⚙️ Machine Configuration & Vision Layer")

    # --- INTERACTIVE AI VISION DECK ---
    with st.expander("📸 Smart AI Engine: Scan Handwritten Work", expanded=True):
        uploaded_image = st.file_uploader("Upload image (Handwritten Diagram, Table, NFA or DFA):", type=["png", "jpg", "jpeg"])
        
        if st.button("Analyze & Classify Image ✨", disabled=not uploaded_image):
            with st.spinner("AI analyzing layout structures and extracting data states..."):
                try:
                    # PERMANENT SOLUTION: Fetching the key securely from Streamlit Secrets
                    if "GEMINI_API_KEY" in st.secrets:
                        api_key = st.secrets["GEMINI_API_KEY"]
                    else:
                        st.error("❌ API Key missing! Please configure GEMINI_API_KEY in your Streamlit secrets management panel.")
                        st.stop()
                        
                    client = genai.Client(api_key=api_key)
                    img_bytes = uploaded_image.read()
                    image_part = types.Part.from_bytes(data=img_bytes, mime_type=uploaded_image.type)
    
    # # --- INTERACTIVE AI VISION DECK ---
    # with st.expander("📸 Smart AI Engine: Scan Handwritten Work", expanded=True):
    #     api_key = st.text_input("Provide Gemini API Key:", type="password")
    #     uploaded_image = st.file_uploader("Upload image (Handwritten Diagram, Table, NFA or DFA):", type=["png", "jpg", "jpeg"])
        
    #     if st.button("Analyze & Classify Image ✨", disabled=not (api_key and uploaded_image)):
    #         with st.spinner("AI analyzing layout structures and extracting data states..."):
    #             try:
    #                 client = genai.Client(api_key=api_key)
    #                 img_bytes = uploaded_image.read()
                     # image_part = types.Part.from_bytes(data=img_bytes, mime_type=uploaded_image.type)
                    
                    system_prompt = (
    "Analyze this image meticulously. First, determine if it is a visual 'Diagram' or a structural 'Table'. "
    "Second, evaluate the transitions to determine the machine type: "
    "Classify as a 'DFA' ONLY if every single state has exactly ONE transition for every symbol in the alphabet. "
    "If any state has multiple target states on the same symbol, OR if any state is missing an explicit transition "
    "for an alphabet symbol, you MUST classify it as an 'NFA'.\n\n"
    
    "CRITICAL VISUAL PARSING RULES:\n"
    "1. FINAL STATES: Only classify a state as a final state if it features two distinctly separated, intentional concentric circles. "
    "Do NOT classify a state as final if it is simply a single circle drawn with a thick line, heavy pen pressure, or retraced ink.\n"
    "2. IF NO FINAL STATE IS FOUND: If there are no clear double circles in the image, return the `final_states` array completely empty: []. "
    "Do NOT assume or guess which state might be final.\n"
    "3. ARROW DIRECTIONS: Look carefully at the arrowheads. Only map a transition if the arrowhead clearly points to a destination. "
    "Pay close attention to self-loops vs. transitions between different states.\n"
    "4. NO EPSILON: Ignore any markings resembling epsilon (ε). Epsilon is completely unsupported.\n\n"
    
    "Extract all states, standard alphabet characters, start states, final states, and transition details. "
    "Populate the schema carefully based strictly on what is visible."

                    )
                    
                    response = client.models.generate_content(
                        model='gemini-2.5-flash',
                        contents=[image_part, system_prompt],
                        config=types.GenerateContentConfig(
                            response_mime_type="application/json",
                            response_schema=SmartAutomataSchema,
                            temperature=0.1
                        ),
                    )
                    
                    st.session_state.smart_ai_payload = json.loads(response.text)
                except Exception as e:
                    st.error(f"Vision analysis obstacle encountered: {e}")

    # Process Active Form States
    ai_data = st.session_state.smart_ai_payload
    
    if ai_data:
        st.success(f"🎯 **AI Classification Complete:** Detected a **{ai_data['machine_type']}** from a handwritten **{ai_data['detected_input_format']}**!")
        init_machine_type = "NFA (Non-Deterministic)" if ai_data["machine_type"] == "NFA" else "DFA (Deterministic)"
        init_states = ", ".join(ai_data["states"])
        # Filter out epsilon if the AI somehow hallucinated it
        init_alphabet = ", ".join([a for a in ai_data["alphabet"] if a not in ["ε", "epsilon", "E", "eps"]])
    else:
        init_machine_type = "DFA (Deterministic)"
        init_states = "q0, q1, q2"
        init_alphabet = "0, 1"

    # --- RENDER CONTROL INTERFACES ---
    machine_choice = st.radio("Select Machine Type:", ("DFA (Deterministic)", "NFA (Non-Deterministic)"), 
                              index=0 if init_machine_type == "DFA (Deterministic)" else 1, horizontal=True)
    is_nfa = (machine_choice == "NFA (Non-Deterministic)")
    
    states_text = st.text_input("1. Handled State Nodes:", init_states)
    alphabet_text = st.text_input("2. Active Symbols:", init_alphabet)
    
    states = [s.strip() for s in states_text.split(",") if s.strip()]
    
    # Strictly filter out any epsilon-related text inputs from the user or AI
    raw_alphabet = [a.strip() for a in alphabet_text.split(",") if a.strip()]
    alphabet = [a for a in raw_alphabet if a not in ["ε", "epsilon", "E", "eps"]]
    
    # Build clean working alphabet without any duplicates
    working_alphabet = []
    for sym in alphabet:
        if sym not in working_alphabet:
            working_alphabet.append(sym)
    
    if not states or not alphabet:
        is_config_valid = False
        
    def_start_idx = 0
    if ai_data and ai_data.get("initial_state") in states:
        def_start_idx = states.index(ai_data["initial_state"])
        
    initial_state = st.selectbox("3. Machine Entry State:", options=states if states else [""], index=def_start_idx)
    
    def_finals_list = []
    if ai_data:
        def_finals_list = [f for f in ai_data.get("final_states", []) if f in states]
    final_states = st.multiselect("4. Target Final States:", options=states if states else [], default=def_finals_list)
    
    if not final_states and states:
        is_config_valid = False

    st.subheader("5. Formulated Transition Matrix Mapping")
    
    # Restructure AI paths for lookups
    ai_mapping = {}
    if ai_data and "transitions" in ai_data:
        for trans in ai_data["transitions"]:
            f_s, sym, t_ss = trans["from_state"], trans["symbol"], trans["to_states"]
            if f_s not in ai_mapping: ai_mapping[f_s] = {}
            ai_mapping[f_s][sym] = t_ss

    transitions = {}
    if states and working_alphabet:
        for state in states:
            transitions[state] = {}
            st.markdown(f"**Transitions originating from state `{state}`:**")
            cols = st.columns(len(working_alphabet))
            for idx, symbol in enumerate(working_alphabet):
                with cols[idx]:
                    ai_defaults = ai_mapping.get(state, {}).get(symbol, [])
                    ai_defaults = [d for d in ai_defaults if d in states]
                    
                    unique_widget_key = f"widget_t_{str(state).strip()}_{str(symbol).strip()}"
                    
                    if is_nfa:
                        next_dest = st.multiselect(f"On '{symbol}' ➔", options=states, key=unique_widget_key, default=ai_defaults)
                        transitions[state][symbol] = next_dest
                    else:
                        def_val = ai_defaults[0] if ai_defaults else ""
                        opt_list = [""] + states
                        def_idx = opt_list.index(def_val) if def_val in opt_list else 0
                        
                        next_dest = st.selectbox(f"On '{symbol}' ➔", options=opt_list, key=unique_widget_key, index=def_idx)
                        if next_dest:
                            transitions[state][symbol] = [next_dest]
                        else:
                            transitions[state][symbol] = []
                            is_config_valid = False

    user_config = {
        "states": set(states), "alphabet": set(alphabet), "transitions": transitions,
        "initial_state": initial_state, "final_states": set(final_states), "type": "NFA" if is_nfa else "DFA"
    }

with col2:
    st.header("🔍 Simulation & Graph Visualizer")
    
    if not states or not alphabet or not initial_state:
        st.warning("Awaiting configuration properties from manual setups or AI vision inputs.")
    else:
        st.subheader("📊 Transition Table Map")
        table_data = []
        for state in states:
            row = {"State": state}
            for symbol in working_alphabet:
                destinations = transitions[state].get(symbol, [])
                row[symbol] = ", ".join(destinations) if destinations else "-"
            table_data.append(row)
        st.table(table_data)

        st.subheader("🗺️ Rendered Automata Blueprint Diagram")
        st.graphviz_chart(render_automaton(user_config))
        
        st.divider()
        st.subheader("🏃‍♂️ Run Interactive Test String")
        test_string = st.text_input("Provide test string execution candidate:", "1001")
        
        if not is_config_valid:
            st.error("⚠️ **Execution Engine Halted:** Complete required transitions and fields to proceed.")
        elif not test_string:
            st.warning("Provide a test string sequence candidate to execute tracking simulation.")
            
        execution_gate = (not is_config_valid) or (not test_string)
        
        if st.button("Execute Step-by-Step Transition Animation", type="primary", disabled=execution_gate):
            current_states = {user_config["initial_state"]}
                
            st.write("#### Live Computing Execution Path Trace:")
            status_text = st.empty()
            graph_placeholder = st.empty()
            
            status_text.info(f"🏁 **Start Node:** Processing set initiated with states: `{list(current_states)}`")
            graph_placeholder.graphviz_chart(render_automaton(user_config, active_states=current_states))
            time.sleep(1.5)
            
            invalid_string = False
            for i, symbol in enumerate(test_string):
                if symbol not in user_config["alphabet"]:
                    st.error(f"❌ Error: Symbol '{symbol}' falls outside language alphabet boundaries.")
                    invalid_string = True
                    break
                
                next_states_set = set()
                for state in current_states:
                    transitions_from_state = user_config["transitions"].get(state, {}).get(symbol, [])
                    for next_s in transitions_from_state:
                        next_states_set.add(next_s)
                
                if not next_states_set:
                    status_text.error(f"💥 **Dead End:** Computation path halted tracking index on symbol `{symbol}`.")
                    current_states = set()
                    invalid_string = True
                    break
                    
                st.write(f"🔹 **Step {i+1}:** Read character symbol `{symbol}` ➔ Engine shifted active sets to: `{list(next_states_set)}`")
                current_states = next_states_set
                graph_placeholder.graphviz_chart(render_automaton(user_config, active_states=current_states))
                time.sleep(1.5)
                
            if not invalid_string:
                has_accepted = any(s in user_config["final_states"] for s in current_states)
                if has_accepted:
                    st.success(f"🎉 **String Status: ACCEPTED.** Computing path hit matching final acceptance parameters.")
                else:
                    st.error(f"❌ **String Status: REJECTED.** Computation ended in standard non-accepting states.")