import pandas as pd
import streamlit as st

APP_VERSION = "1.0.0"
    
st.set_page_config(layout="wide", page_title="Construction Cost Calculator")
st.title("Complete Construction Cost Calculator")

# ==========================================
# 2. COST BREAKDOWN TABS
# ==========================================
st.header("2. Cost Breakdown")
tab_area_breakdown, tab_hard_cost, tab_soft_cost = st.tabs(["Area Breakdown", "Hard Cost", "Soft Cost"])

with tab_area_breakdown:

    # ==========================================
    # BUILDING CONFIGURATION
    # ==========================================
    st.divider()
    st.header("Building Configuration")
    st.markdown("Set your floor counts below to generate the Area tables.")

    # Changed to 4 columns to fit the new top floor options
    c1, c2, c3, c4 = st.columns(4, vertical_alignment="top")
    with c1:
        num_basements = st.number_input("Number of Basements", min_value=0, value=1, step=1)
    with c2:
        num_floors = st.number_input("Number of Floors (Levels)", min_value=1, value=5, step=1)
    with c3:
        num_refuges = st.number_input("Number of Refuge Floors", min_value=0, value=0, step=1)
    with c4:
        # Adding optional toggles for the standard top floors
        st.write("**Top Floors**")
        c1, c2 = st.columns(2)
        has_roof = c1.checkbox("Include Roof", value=True)
        has_roof_machine = c2.checkbox("Include Roof Machine", value=True)

    # Generate the dynamic list of floor names
    floor_names = []

    # 1. Basements (e.g., if 3 basements: B2, B1, LG)
    for i in range(num_basements, 0, -1):
        if i == 1:
            floor_names.append("LG")
        else:
            floor_names.append(f"B{i-1}")

    # 2. Above Ground Levels
    for i in range(1, num_floors + 1):
        floor_names.append(f"Level {i}")

    # 3. Refuge Floors
    for i in range(1, num_refuges + 1):
        floor_names.append(f"Refuge {i}")

    # 4. Top Floors (Appended at the very top of the building)
    if has_roof:
        floor_names.append("Roof")
    if has_roof_machine:
        floor_names.append("Roof Machine")


    # ==========================================
    # MASTER AREA DATAFRAME
    # ==========================================
    st.header("Area Breakdown")
    st.caption("💡 **Tip:** Highlight your input data in Excel, click the top-left cell of the Input Table, and paste (`Ctrl+V`). The Results Table will calculate instantly.")
    
    # 1. Define ONLY the inputs for the editable dataframe
    df_inputs_base = pd.DataFrame({
        "FLOOR": floor_names,
        "FL TO FL HEIGHT": [3.5] * len(floor_names),
        "PARKIR": [0.0] * len(floor_names),
        "Roof/Deck": [0.0] * len(floor_names),
        "MEP Outdoor": [0.0] * len(floor_names),
        "Koridor/Lobby": [0.0] * len(floor_names),
        "Stair, MEP, Etc": [0.0] * len(floor_names),
        "Unit": [0.0] * len(floor_names),
        "Office": [0.0] * len(floor_names),
    })

    # Store inputs in session state
    if "area_inputs_df" not in st.session_state or len(st.session_state.area_inputs_df) != len(floor_names):
        st.session_state.area_inputs_df = df_inputs_base

    # Create a side-by-side layout (Left is wider for inputs, Right is narrower for results)
    col_inputs, col_results = st.columns([1.8, 1])

    with col_inputs:
        st.write("**📥 Input Table**")
        edited_inputs = st.data_editor(
            st.session_state.area_inputs_df,
            use_container_width=True,
            num_rows="dynamic",
            hide_index=True,
            key="area_input_editor"
        )
        # Save state
        st.session_state.area_inputs_df = edited_inputs

    # 2. Apply the calculation logic based on the inputs
    calc_nfa = edited_inputs["Office"] + edited_inputs["Unit"]
    calc_sgfa = calc_nfa + edited_inputs["Koridor/Lobby"]
    calc_gfa = calc_sgfa + edited_inputs["Stair, MEP, Etc"]
    calc_gba = calc_gfa + edited_inputs["PARKIR"] + edited_inputs["Roof/Deck"] + edited_inputs["MEP Outdoor"]
    calc_total = calc_gba

    # 3. Build the Results DataFrame exactly as requested
    df_results = pd.DataFrame({
        "FLOOR": edited_inputs["FLOOR"], 
        "TOTAL": calc_total,
        "GBA": calc_gba,
        "GFA": calc_gfa, 
        "SGFA": calc_sgfa,
        "NFA": calc_nfa,
    })

    with col_results:
        st.write("**🧮 Calculated Results**")
        st.dataframe(
            df_results, 
            use_container_width=True, 
            hide_index=True
        )

    # 4. Extract the grand totals to feed into your Area Parameters
    calculated_nfa = df_results["NFA"].sum()
    calculated_sgfa = df_results["SGFA"].sum()
    calculated_gfa = df_results["GFA"].sum()
    calculated_gba = df_results["GBA"].sum()

    st.divider()

    # Display clean metric cards below the tables
    st.subheader("Grand Totals & Dependencies")
    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Total NFA", f"{calculated_nfa:,.2f} m2")
    m2.metric("Total SGFA", f"{calculated_sgfa:,.2f} m2")
    m3.metric("Total GFA", f"{calculated_gfa:,.2f} m2")
    m4.metric("Total GBA", f"{calculated_gba:,.2f} m2")
    
    with m5:
        # Added Total Rooms here so it can feed the dependency calculator
        rooms = st.number_input("Total Rooms", value=256, step=1)

    # ==========================================
    # 1. AREA PARAMETERS (Manual Override)
    # ==========================================
    with st.expander("Manual Override (Optional)"):    
        st.markdown("Only Change if GBA/GFA/SGFA/NFA are different from the calculated values above.")

        g1, g2, g3, g4 = st.columns(4)
        with g1:
            gba = st.number_input("Gross Building Area (GBA)", value=float(calculated_gba))
        with g2:
            gfa = st.number_input("Gross Floor Area (GFA)", value=float(calculated_gfa))
        with g3:
            sgfa = st.number_input("Semi-Gross Floor Area (SGFA)", value=float(calculated_sgfa))
        with g4:
            nfa = st.number_input("Net Floor Area (NFA)", value=float(calculated_nfa))

# ==========================================
# HARD COST TAB
# ==========================================
with tab_hard_cost:

    cost_estimate_framework = {
        "HARDCOST": {
            "PRELIMINARIES": {
                "id": "TOTAL_HARD_PRELIM",
                "unit": "%",
                "volume_label": "5%",
                "price_label": "5% OF SUBTOTAL HARDCOST EXCLUDE PRELIMINARIES AND CONTINGENCIES",
                "items": {} 
            },
            "EARTHWORKS": {
                "id": "TOTAL_SUB_HARD_EARTH",
                "items": {
                    "Cut fill": {"id": "SUB_HARD_EARTH_CUTFILL", "unit": "m2", "volume_label": "VOLUME_M2_SUB_HARD_EARTH_CUTFILL", "price_label": "PRICE_SUB_HARD_EARTH_CUTFILL", "dependent_label": "GBA"},
                    "Dewatering": {"id": "SUB_HARD_EARTH_DEWATERING", "unit": "ls", "volume_label": 1, "price_label": "PRICE_SUB_HARD_EARTH_DEWATERING"},
                    "Soil Improvement": {"id": "SUB_HARD_EARTH_IMPROVEMENT", "unit": "ls", "volume_label": 1, "price_label": "PRICE_SUB_HARD_EARTH_IMPROVEMENT"},
                    "Shoring System": {"id": "SUB_HARD_EARTH_SHORING", "unit": "ls", "volume_label": 1, "price_label": "PRICE_SUB_HARD_EARTH_SHORING"},
                    "Others": {"id": "SUB_HARD_EARTH_OTHERS", "unit": "ls", "volume_label": 1, "price_label": "PRICE_SUB_HARD_EARTH_OTHERS", "dependent_label": "OTHERS_EARTH"}
                }
            },
            "FOUNDATION WORKS": {
                "id": "TOTAL_SUB_HARD_FOUND",
                "items": {
                    "Supply Tiang Pancang": {"id": "SUB_HARD_FOUND_SUPPLY", "unit": "M'", "volume_label": "VOLUME_M1_SUB_HARD_FOUND_SUPPLY", "price_label": "PRICE_SUB_HARD_FOUND_SUPPLY", "dependent_label": "GBA"},
                    "Install Tiang Pancang": {"id": "SUB_HARD_FOUND_INSTALL", "unit": "M'", "volume_label": "VOLUME_M1_SUB_HARD_FOUND_INSTALL", "price_label": "PRICE_SUB_HARD_FOUND_INSTALL", "dependent_label": "GBA"},
                    "Others": {"id": "SUB_HARD_FOUND_OTHERS", "unit": "ls", "volume_label": 1, "price_label": "PRICE_SUB_HARD_FOUND_OTHERS"}
                }
            },
            "STRUCTURAL WORKS": {
                "id": "TOTAL_SUB_HARD_STR",
                "items": {
                    "Sub/Superstructure": {"id": "SUB_HARD_STR_SUBSUPER", "unit": "m3", "volume_label": "VOLUME_M3_SUB_HARD_STR_SUBSUPER", "price_label": "PRICE_SUB_HARD_STR_SUBSUPER", "other_label": "RATIO_M3_M2_SUB_HARD_STR_SUBSUPER(def=0.4)", "dependent_label": "GBA"},
                    "Bekisting": {"id": "SUB_HARD_STR_BEKISTING", "unit": "m2", "volume_label": "VOLUME_M2_SUB_HARD_STR_BEKISTING", "price_label": "PRICE_SUB_HARD_STR_BEKISTING", "other_label": "RATIO_M2_M3_SUB_HARD_STR_BEKISTING(def=5.0)"},
                    "Besi (180kg/m3)": {"id": "SUB_HARD_STR_BESI", "unit": "kg", "volume_label": "VOLUME_KG_SUB_HARD_STR_BESI", "price_label": "PRICE_SUB_HARD_STR_BESI", "other_label": "RATIO_KG_M3_SUB_HARD_STR_BESI(def=180)"},
                    "Readymix Concrete": {"id": "SUB_HARD_STR_CONCRETE", "unit": "m3", "volume_label": "VOLUME_M3_SUB_HARD_STR_CONCRETE", "price_label": "PRICE_SUB_HARD_STR_CONCRETE", "other_label": "RATIO_SUB_HARD_STR_CONCRETE(def=1.08)", "dependent_label": "VOLUME_M3_SUB_HARD_STR_SUBSUPER"},
                    "Rebar": {"id": "SUB_HARD_STR_REBARSBO", "unit": "kg", "volume_label": "VOLUME_KG_SUB_HARD_STR_REBARSBO", "price_label": "PRICE_SUB_HARD_STR_REBARSBO", "other_label": "RATIO_KG_M3_SUB_HARD_STR_BESI(def=180)"},
                    "Prestress Works": {"id": "SUB_HARD_STR_PRESTRESS", "unit": "m2", "volume_label": "VOLUME_M2_SUB_HARD_STR_PRESTRESS", "price_label": "PRICE_SUB_HARD_STR_PRESTRESS"},
                    "Steelworks": {"id": "SUB_HARD_STR_STEELWORKS", "unit": "m3", "volume_label": "VOLUME_M3_SUB_HARD_STR_STEELWORKS", "price_label": "PRICE_SUB_HARD_STR_STEELWORKS"},
                    "Others (WP integral, FH, etc)": {"id": "SUB_HARD_STR_OTHERS", "unit": "m2", "volume_label": 1, "price_label": "PRICE_SUB_HARD_STR_OTHERS", "dependent_label": "GBA"}
                }
            },
            "ARCHITECTURAL WORKS": {
                "id": "TOTAL_SUB_HARD_ARCH",
                "items": {
                    "Basic Finishes Work": {"id": "SUB_HARD_ARCH_BASICARCH", "unit": "m2", "volume_label": "VOLUME_M2_SUB_HARD_ARCH_BASICARCH", "price_label": "PRICE_SUB_HARD_ARCH_BASICARCH", "dependent_label": "GFA"},
                    "Gondola": {"id": "SUB_HARD_ARCH_GONDOLA", "unit": "unit", "volume_label": "VOLUME_UNIT_SUB_HARD_ARCH_GONDOLA", "price_label": "PRICE_SUB_HARD_ARCH_GONDOLA"},
                    "Skylight": {"id": "SUB_HARD_ARCH_SKYLIGHT", "unit": "m2", "volume_label": "VOLUME_M2_SUB_HARD_ARCH_SKYLIGHT", "price_label": "PRICE_SUB_HARD_ARCH_SKYLIGHT"},
                    "Interior Main Lobby": {"id": "SUB_HARD_ARCH_LOBBY", "unit": "m2", "volume_label": "VOLUME_M2_SUB_HARD_ARCH_LOBBY", "price_label": "PRICE_SUB_HARD_ARCH_LOBBY"},
                    "Railing Balkon": {"id": "SUB_HARD_ARCH_RAILING", "unit": "m'", "volume_label": "VOLUME_M1_SUB_HARD_ARCH_RAILING", "price_label": "PRICE_SUB_HARD_ARCH_RAILING", "dependent_label": "ROOM"},
                    "Kitchen Equipment": {"id": "SUB_HARD_ARCH_KITCHEN", "unit": "unit", "volume_label": "VOLUME_UNIT_SUB_HARD_ARCH_KITCHEN", "price_label": "PRICE_SUB_HARD_ARCH_KITCHEN"},
                    "Carpet": {"id": "SUB_HARD_ARCH_CARPET", "unit": "m2", "volume_label": "VOLUME_M2_SUB_HARD_ARCH_CARPET", "price_label": "PRICE_SUB_HARD_ARCH_CARPET"},
                    "Kaca": {"id": "SUB_HARD_ARCH_KACA", "unit": "m2", "volume_label": "VOLUME_M2_SUB_HARD_ARCH_KACA", "price_label": "PRICE_SUB_HARD_ARCH_KACA"},
                    "Custom Item Architecture": {"id": "SUB_HARD_ARCH_OTHERS", "unit": "ls", "volume_label": 1, "price_label": "PRICE_SUB_HARD_ARCH_OTHERS", "dependent_label": "OTHERS_ARCHITECTURE"},
                    
                    "Window Wall": {"id": "SUB_HARD_ARCH_FACADE_WINDOW", "unit": "m2", "volume_label": 1, "price_label": "PRICE_SUB_HARD_ARCH_FACADE_WINDOW", "other_label": "PERCENT_SUB_HARD_ARCH_FACADE_WINDOW", "dependent_label": "SUB_HARD_ARCH_FACADE"},
                    "Double Skin": {"id": "SUB_HARD_ARCH_FACADE_DOUBLE", "unit": "m2", "volume_label": 1, "price_label": "PRICE_SUB_HARD_ARCH_FACADE_DOUBLE", "other_label": "PERCENT_SUB_HARD_ARCH_FACADE_DOUBLE", "dependent_label": "SUB_HARD_ARCH_FACADE"},
                    "Precast Facade": {"id": "SUB_HARD_ARCH_FACADE_PRECAST", "unit": "m2", "volume_label": 1, "price_label": "PRICE_SUB_HARD_ARCH_FACADE_PRECAST", "other_label": "PERCENT_SUB_HARD_ARCH_FACADE_PRECAST", "dependent_label": "SUB_HARD_ARCH_FACADE"},
                    
                    "Pintu Gelas": {"id": "SUB_HARD_ARCH_PINTU_GELAS", "unit": "unit", "volume_label": 1, "price_label": "PRICE_SUB_HARD_ARCH_PINTU_GELAS", "dependent_label": "VOLUME_UNIT_SUB_HARD_ARCH_PINTU_GELAS"},
                    "Pintu Besi": {"id": "SUB_HARD_ARCH_PINTU_BESI", "unit": "unit", "volume_label": 1, "price_label": "PRICE_SUB_HARD_ARCH_PINTU_BESI", "dependent_label": "VOLUME_UNIT_SUB_HARD_ARCH_PINTU_BESI"},
                    "Pintu Kayu": {"id": "SUB_HARD_ARCH_PINTU_KAYU", "unit": "unit", "volume_label": 1, "price_label": "PRICE_SUB_HARD_ARCH_PINTU_KAYU", "dependent_label": "VOLUME_UNIT_SUB_HARD_ARCH_PINTU_KAYU"},
                    
                    "Ironmongeries Besi": {"id": "SUB_HARD_ARCH_PINTU_HARDWARE_BESI", "unit": "unit", "volume_label": 1, "price_label": "PRICE_SUB_HARD_ARCH_PINTU_HARDWARE_BESI", "dependent_label": "VOLUME_UNIT_SUB_HARD_ARCH_PINTU_BESI"},
                    "Ironmongeries Kayu": {"id": "SUB_HARD_ARCH_PINTU_HARDWARE_KAYU", "unit": "unit", "volume_label": 1, "price_label": "PRICE_SUB_HARD_ARCH_PINTU_HARDWARE_KAYU", "dependent_label": "VOLUME_UNIT_SUB_HARD_ARCH_PINTU_KAYU"},
                    
                    "Toilet Wanita": {"id": "SUB_HARD_ARCH_SANITARY_WANITA", "unit": "unit", "volume_label": "VOLUME_UNIT_SUB_HARD_ARCH_SANITARY_WANITA", "price_label": "PRICE_SUB_HARD_ARCH_SANITARY_WANITA"},
                    "Toilet Pria": {"id": "SUB_HARD_ARCH_SANITARY_PRIA", "unit": "unit", "volume_label": "VOLUME_UNIT_SUB_HARD_ARCH_SANITARY_PRIA", "price_label": "PRICE_SUB_HARD_ARCH_SANITARY_PRIA"},
                    "Toilet Disable": {"id": "SUB_HARD_ARCH_SANITARY_DISABLE", "unit": "unit", "volume_label": "VOLUME_UNIT_SUB_HARD_ARCH_SANITARY_DISABLE", "price_label": "PRICE_SUB_HARD_ARCH_SANITARY_DISABLE"},
                    "Musholla": {"id": "SUB_HARD_ARCH_SANITARY_MUSHOLLA", "unit": "unit", "volume_label": "VOLUME_UNIT_SUB_HARD_ARCH_SANITARY_MUSHOLLA", "price_label": "PRICE_SUB_HARD_ARCH_SANITARY_MUSHOLLA"},
                    "Toilet Ruang": {"id": "SUB_HARD_ARCH_SANITARY_TOILETROOM", "unit": "unit", "volume_label": "VOLUME_UNIT_SUB_HARD_ARCH_SANITARY_TOILETROOM", "price_label": "PRICE_SUB_HARD_ARCH_SANITARY_TOILETROOM", "dependent_label": "ROOM"},
                    
                    "Keramik & HT": {"id": "SUB_HARD_ARCH_LANTAI_KERAMIKHT", "unit": "m2", "volume_label": 1, "price_label": "PRICE_SUB_HARD_ARCH_LANTAI_KERAMIKHT", "other_label": "PERCENT_SUB_HARD_ARCH_LANTAI_KERAMIKHT", "dependent_label": "SUB_HARD_ARCH_LANTAI"},
                    "Vinyl": {"id": "SUB_HARD_ARCH_LANTAI_VINYL", "unit": "m2", "volume_label": 1, "price_label": "PRICE_SUB_HARD_ARCH_LANTAI_VINYL", "other_label": "PERCENT_SUB_HARD_ARCH_LANTAI_VINYL", "dependent_label": "SUB_HARD_ARCH_LANTAI"},
                    "Marmer": {"id": "SUB_HARD_ARCH_LANTAI_MARMER", "unit": "m2", "volume_label": 1, "price_label": "PRICE_SUB_HARD_ARCH_LANTAI_MARMER", "other_label": "PERCENT_SUB_HARD_ARCH_LANTAI_MARMER", "dependent_label": "SUB_HARD_ARCH_LANTAI"}
                }
            },
            "F. F. & E.": {
                "id": "TOTAL_SUB_HARD_FFE",
                "items": {
                    "Seater & Chair": {"id": "SUB_HARD_FFE_SEATER", "unit": "unit", "volume_label": "VOLUME_UNIT_SUB_HARD_FFE_SEATER", "price_label": "PRICE_SUB_HARD_FFE_SEATER"},
                    "Beds & Linen": {"id": "SUB_HARD_FFE_BEDS", "unit": "unit", "volume_label": "VOLUME_UNIT_SUB_HARD_FFE_BEDS", "price_label": "PRICE_SUB_HARD_FFE_BEDS"},
                    "Kitchen Cabinet, Drawer": {"id": "SUB_HARD_FFE_CABINET", "unit": "unit", "volume_label": "VOLUME_UNIT_SUB_HARD_FFE_CABINET", "price_label": "PRICE_SUB_HARD_FFE_CABINET"},
                    "Electronic": {"id": "SUB_HARD_FFE_ELECTRONIC", "unit": "unit", "volume_label": "VOLUME_UNIT_SUB_HARD_FFE_ELECTRONIC", "price_label": "PRICE_SUB_HARD_FFE_ELECTRONIC"},
                    "Housewares": {"id": "SUB_HARD_FFE_HOUSEWARE", "unit": "unit", "volume_label": "VOLUME_UNIT_SUB_HARD_FFE_HOUSEWARE", "price_label": "PRICE_SUB_HARD_FFE_HOUSEWARE"},
                    "Stove w/ 2 burner + Hoods": {"id": "SUB_HARD_FFE_STOVE", "unit": "unit", "volume_label": "VOLUME_UNIT_SUB_HARD_FFE_STOVE", "price_label": "PRICE_SUB_HARD_FFE_STOVE"},
                    "Appliance (Microwave, Fridge, Washer)": {"id": "SUB_HARD_FFE_APPLIANCE", "unit": "unit", "volume_label": "VOLUME_UNIT_SUB_HARD_FFE_APPLIANCE", "price_label": "PRICE_SUB_HARD_FFE_APPLIANCE"},
                    "Artwork": {"id": "SUB_HARD_FFE_ARTWORK", "unit": "unit", "volume_label": "VOLUME_UNIT_SUB_HARD_FFE_ARTWORK", "price_label": "PRICE_SUB_HARD_FFE_ARTWORK"},
                    "Others (Trash chute, Gym, Winch)": {"id": "SUB_HARD_FFE_OTHERS", "unit": "unit", "volume_label": "VOLUME_UNIT_SUB_HARD_FFE_OTHERS", "price_label": "PRICE_SUB_HARD_FFE_OTHERS"}
                }
            },
            "MEP INSTALLATION WORKS": {
                "id": "TOTAL_SUB_HARD_MEP",
                "items": {
                    "STP & WTP system": {"id": "SUB_HARD_MEP_STPWTP", "unit": "m2", "volume_label": "VOLUME_M2_SUB_HARD_MEP_STPWTP", "price_label": "PRICE_SUB_HARD_MEP_STPWTP"},
                    "Plumbing Installation": {"id": "SUB_HARD_MEP_PLUMBING", "unit": "m2", "volume_label": "VOLUME_M2_SUB_HARD_MEP_PLUMBING", "price_label": "PRICE_SUB_HARD_MEP_PLUMBING"},
                    "Fire Protection": {"id": "SUB_HARD_MEP_FIRE", "unit": "m2", "volume_label": "VOLUME_M2_SUB_HARD_MEP_FIRE_FIGHTING", "price_label": "PRICE_SUB_HARD_MEP_FIRE_FIGHTING"},
                    "Electrical Installation": {"id": "SUB_HARD_MEP_ELECTRICAL", "unit": "m2", "volume_label": "VOLUME_M2_SUB_HARD_MEP_ELECTRICAL", "price_label": "PRICE_SUB_HARD_MEP_ELECTRICAL"},
                    "Genset Installation": {"id": "SUB_HARD_MEP_GENSETINSTALL", "unit": "m2", "volume_label": "VOLUME_M2_SUB_HARD_MEP_GENSETINSTALL", "price_label": "PRICE_SUB_HARD_MEP_GENSETINSTALL"},
                    "MVAC Installation": {"id": "SUB_HARD_MEP_MVACINSTALL", "unit": "m2", "volume_label": "VOLUME_M2_SUB_HARD_MEP_MVACINSTALL", "price_label": "PRICE_SUB_HARD_MEP_MVACINSTALL"},
                    "Vertical Transport": {"id": "SUB_HARD_MEP_VTRANSPORT", "unit": "m2", "volume_label": "VOLUME_M2_SUB_HARD_MEP_VTRANSPORT", "price_label": "PRICE_SUB_HARD_MEP_VTRANSPORT"},
                    "Electronic Installation": {"id": "SUB_HARD_MEP_ELECTRONIC", "unit": "m2", "volume_label": "VOLUME_M2_SUB_HARD_MEP_ELECTRONIC", "price_label": "PRICE_SUB_HARD_MEP_ELECTRONIC"},
                    "System Data": {"id": "SUB_HARD_MEP_DATA", "unit": "m2", "volume_label": "VOLUME_M2_SUB_HARD_MEP_DATA", "price_label": "PRICE_SUB_HARD_MEP_DATA"},
                    "Gas Installation": {"id": "SUB_HARD_MEP_GASINSTALL", "unit": "m2", "volume_label": "VOLUME_M2_SUB_HARD_MEP_GASINSTALL", "price_label": "PRICE_SUB_HARD_MEP_GASINSTALL"},
                    "Special Lighting": {"id": "SUB_HARD_MEP_LIGHTINGSPECIAL", "unit": "m2", "volume_label": "VOLUME_M2_SUB_HARD_MEP_LIGHTINGSPECIAL", "price_label": "PRICE_SUB_HARD_MEP_LIGHTINGSPECIAL"},
                    "Pompa Pemadam": {"id": "SUB_HARD_MEP_PUMP", "unit": "unit", "volume_label": "VOLUME_UNIT_SUB_HARD_MEP_PUMP", "price_label": "PRICE_SUB_HARD_MEP_PUMP"},
                    "Chillers, AHU, FCU": {"id": "SUB_HARD_MEP_HVAC", "unit": "unit", "volume_label": "VOLUME_UNIT_SUB_HARD_MEP_HVAC", "price_label": "PRICE_SUB_HARD_MEP_HVAC"},
                    "Lighting Fixtures": {"id": "SUB_HARD_MEP_LIGHTFIXTURE", "unit": "ttk", "volume_label": "VOLUME_TTK_SUB_HARD_MEP_LIGHTFIXTURE", "price_label": "PRICE_SUB_HARD_MEP_LIGHTFIXTURE"},
                    "Genset": {"id": "SUB_HARD_MEP_GENSET", "unit": "unit", "volume_label": "VOLUME_UNIT_SUB_HARD_MEP_GENSET", "price_label": "PRICE_SUB_HARD_MEP_GENSET"},
                    "Heat Pump": {"id": "SUB_HARD_MEP_HEATPUMP", "unit": "unit", "volume_label": "VOLUME_UNIT_SUB_HARD_MEP_HEATPUMP", "price_label": "PRICE_SUB_HARD_MEP_HEATPUMP"},
                    "Cooling Towers": {"id": "SUB_HARD_MEP_COOLTOWER", "unit": "unit", "volume_label": "VOLUME_UNIT_SUB_HARD_MEP_COOLTOWER", "price_label": "PRICE_SUB_HARD_MEP_COOLTOWER"},
                    "Water Heater": {"id": "SUB_HARD_MEP_WATERHEATER", "unit": "unit", "volume_label": "VOLUME_UNIT_SUB_HARD_MEP_WATERHEATER", "price_label": "PRICE_SUB_HARD_MEP_WATERHEATER"},
                    "Swimming Pool Equipment": {"id": "SUB_HARD_MEP_SWIMMINGPOOL", "unit": "unit", "volume_label": "VOLUME_UNIT_SUB_HARD_MEP_SWIMMINGPOOL", "price_label": "PRICE_SUB_HARD_MEP_SWIMMINGPOOL"},
                    "Deep Well": {"id": "SUB_HARD_MEP_DEEPWELL", "unit": "unit", "volume_label": "VOLUME_UNIT_SUB_HARD_MEP_DEEPWELL", "price_label": "PRICE_SUB_HARD_MEP_DEEPWELL"},
                    "Check Point": {"id": "SUB_HARD_MEP_CHECKPOINT", "unit": "unit", "volume_label": "VOLUME_UNIT_SUB_HARD_MEP_CHECKPOINT", "price_label": "PRICE_SUB_HARD_MEP_CHECKPOINT"},
                    "AC Unit": {"id": "SUB_HARD_MEP_ACUNIT", "unit": "unit", "volume_label": "VOLUME_UNIT_SUB_HARD_MEP_ACUNIT", "price_label": "PRICE_SUB_HARD_MEP_ACUNIT"},
                    "AC VRV/Split": {"id": "SUB_HARD_MEP_ACVRV", "unit": "unit", "volume_label": "VOLUME_UNIT_SUB_HARD_MEP_ACVRV", "price_label": "PRICE_SUB_HARD_MEP_ACVRV"},
                    "Unit Fan": {"id": "SUB_HARD_MEP_FANUNIT", "unit": "unit", "volume_label": "VOLUME_UNIT_SUB_HARD_MEP_FANUNIT", "price_label": "PRICE_SUB_HARD_MEP_FANUNIT"},
                    "Other - Pek. MEP": {"id": "SUB_HARD_MEP_OTHERS", "unit": "ls", "volume_label": 1, "price_label": "PRICE_SUB_HARD_MEP_OTHERS"}
                }
            },
            "EXTERNAL WORKS": {
                "id": "TOTAL_SUB_HARD_EXT",
                "items": {
                    "Landscape Works": {"id": "SUB_HARD_EXT_LANDSCAPE", "unit": "m2", "volume_label": "VOLUME_M2_SUB_HARD_EXT_LANDSCAPE", "price_label": "PRICE_SUB_HARD_EXT_LANDSCAPE"},
                    "Hardscape": {"id": "SUB_HARD_EXT_HARDSCAPE", "unit": "m2", "volume_label": 1, "price_label": "PRICE_SUB_HARD_EXT_HARDSCAPE", "other_label": "PERCENT_SUB_HARD_EXT_HARDSCAPE", "dependent_label": "VOLUME_M2_SUB_HARD_EXT_LANDSCAPE"},
                    "Softscape": {"id": "SUB_HARD_EXT_SOFTSCAPE", "unit": "m2", "volume_label": 1, "price_label": "PRICE_SUB_HARD_EXT_SOFTSCAPE", "other_label": "PERCENT_SUB_HARD_EXT_SOFTSCAPE", "dependent_label": "VOLUME_M2_SUB_HARD_EXT_LANDSCAPE"},
                    "PJU": {"id": "SUB_HARD_EXT_SBO_PJU", "unit": "ttk", "volume_label": "VOLUME_TTK_SUB_HARD_EXT_SBO_PJU", "price_label": "PRICE_SUB_HARD_EXT_SBO_PJU"},
                    "Drainage System": {"id": "SUB_HARD_EXT_DRAINAGE", "unit": "m2", "volume_label": "VOLUME_M2_SUB_HARD_EXT_DRAINAGE", "price_label": "PRICE_SUB_HARD_EXT_DRAINAGE"},
                    "Boundary Wall & Gates": {"id": "SUB_HARD_EXT_BOUNDARY", "unit": "m1", "volume_label": "VOLUME_M1_SUB_HARD_EXT_BOUNDARY", "price_label": "PRICE_SUB_HARD_EXT_BOUNDARY"},
                    "Infrastructure - Access Road": {"id": "SUB_HARD_EXT_INFRA_ROAD", "unit": "m2", "volume_label": "VOLUME_M2_SUB_HARD_EXT_INFRA_ROAD", "price_label": "PRICE_SUB_HARD_EXT_INFRA_ROAD"},
                    "Others": {"id": "SUB_HARD_EXT_OTHERS", "unit": "ls", "volume_label": "VOLUME_LS_SUB_HARD_EXT_OTHERS", "price_label": "PRICE_SUB_HARD_EXT_OTHERS"}
                }
            },
            "UTILITIES WORKS": {
                "id": "TOTAL_SUB_HARD_UTIL",
                "items": {
                    "Connection Fee PLN": {"id": "SUB_HARD_UTIL_LISTRIK", "unit": "ls", "volume_label": 1, "price_label": "PRICE_SUB_HARD_UTIL_LISTRIK"},
                    "Connection Fee PAM": {"id": "SUB_HARD_UTIL_BERSIH", "unit": "ls", "volume_label": 1, "price_label": "PRICE_SUB_HARD_UTIL_BERSIH"},
                    "Connection Fee Internet": {"id": "SUB_HARD_UTIL_TELKOM", "unit": "ls", "volume_label": 1, "price_label": "PRICE_SUB_HARD_UTIL_TELKOM"},
                    "Connection Fee Gas": {"id": "SUB_HARD_UTIL_GAS", "unit": "ls", "volume_label": 1, "price_label": "PRICE_SUB_HARD_UTIL_GAS"},
                    "Connection Fee Sewerage": {"id": "SUB_HARD_UTIL_LIMBAH", "unit": "ls", "volume_label": 1, "price_label": "PRICE_SUB_HARD_UTIL_LIMBAH"},
                    "Connection Fee Other": {"id": "SUB_HARD_UTIL_OTHERS", "unit": "ls", "volume_label": 1, "price_label": "PRICE_SUB_HARD_UTIL_OTHERS"}
                }
            },
            "MISCELLANEOUS WORKS": {
                "id": "TOTAL_SUB_HARD_MISC",
                "items": {
                    "Public Facilities": {"id": "SUB_HARD_FAC_PUBLIC", "unit": "m2", "volume_label": "VOLUME_M2_SUB_HARD_FAC_PUBLIC", "price_label": "PRICE_SUB_HARD_FAC_PUBLIC"},
                    "Swimming Pool": {"id": "SUB_HARD_FAC_TENANT_SWIMPOOL", "unit": "m2", "volume_label": "VOLUME_M2_SUB_HARD_FAC_TENANT_SWIMPOOL", "price_label": "PRICE_SUB_HARD_FAC_TENANT_SWIMPOOL"},
                    "Club House": {"id": "SUB_HARD_FAC_TENANT_CLUBHOUSE", "unit": "unit", "volume_label": "VOLUME_UNIT_SUB_HARD_FAC_TENANT_CLUBHOUSE", "price_label": "PRICE_SUB_HARD_FAC_TENANT_CLUBHOUSE"},
                    "Fitness Center": {"id": "SUB_HARD_FAC_TENANT_FITNESS", "unit": "unit", "volume_label": "VOLUME_UNIT_SUB_HARD_FAC_TENANT_FITNESS", "price_label": "PRICE_SUB_HARD_FAC_TENANT_FITNESS"},
                    "Pool Deck": {"id": "SUB_HARD_FAC_TENANT_POOLDECK", "unit": "m2", "volume_label": "VOLUME_M2_SUB_HARD_FAC_TENANT_POOLDECK", "price_label": "PRICE_SUB_HARD_FAC_TENANT_POOLDECK"},
                    "Project Facilities": {"id": "SUB_HARD_FAC_PROJECT", "unit": "ls", "volume_label": 1, "price_label": "PRICE_SUB_HARD_FAC_PROJECT"},
                    "Other Facilities": {"id": "SUB_HARD_FAC_OTHERS", "unit": "ls", "volume_label": 1, "price_label": "PRICE_SUB_HARD_FAC_OTHERS"}
                }
            },
            "CONTINGENCIES": {
                "id": "TOTAL_HARD_CONTING",
                "unit": "%",
                "volume_label": "3%",
                "price_label": "3% OF SUBTOTAL HARDCOST EXCLUDE CONTINGENCIES",
                "items": {}
            }
        },
        "SOFTCOST": {
            "CONSULTANCY SERVICES": {
                "id": "TOTAL_SUB_SOFT_CONSULT",
                "items": {
                    "Quantity Surveyor": {"id": "SUB_SOFT_QS", "unit": "bln", "volume_label": "VOLUME_BLN_SUB_SOFT_QS", "price_label": "PRICE_SUB_SOFT_QS"},
                    "Project Management": {"id": "SUB_SOFT_PM", "unit": "bln", "volume_label": "VOLUME_BLN_SUB_SOFT_PM", "price_label": "PRICE_SUB_SOFT_PM"},
                    "Architectural Consultant": {"id": "SUB_SOFT_CONSULT_ARCH", "unit": "m2", "volume_label": "VOLUME_M2_SUB_SOFT_CONSULT_ARCH", "price_label": "PRICE_SUB_SOFT_CONSULT_ARCH"},
                    "Structural Consultant": {"id": "SUB_SOFT_CONSULT_STR", "unit": "m2", "volume_label": "VOLUME_M2_SUB_SOFT_CONSULT_STR", "price_label": "PRICE_SUB_SOFT_CONSULT_STR"},
                    "MEP Consultant": {"id": "SUB_SOFT_CONSULT_MEP", "unit": "m2", "volume_label": "VOLUME_M2_SUB_SOFT_CONSULT_MEP", "price_label": "PRICE_SUB_SOFT_CONSULT_MEP"},
                    "Interior Designer": {"id": "SUB_SOFT_CONSULT_INT", "unit": "m2", "volume_label": "VOLUME_M2_SUB_SOFT_CONSULT_INT", "price_label": "PRICE_SUB_SOFT_CONSULT_INT"},
                    "Landscaping Consultant": {"id": "SUB_SOFT_CONSULT_LAND", "unit": "m2", "volume_label": "VOLUME_M2_SUB_SOFT_CONSULT_LAND", "price_label": "PRICE_SUB_SOFT_CONSULT_LAND"},
                    "Soil Investigation": {"id": "SUB_SOFT_CONSULT_SOIL", "unit": "m2", "volume_label": "VOLUME_M2_SUB_SOFT_CONSULT_SOIL", "price_label": "PRICE_SUB_SOFT_CONSULT_SOIL"},
                    "Signage Consultant": {"id": "SUB_SOFT_CONSULT_SIGN", "unit": "m2", "volume_label": "VOLUME_M2_SUB_SOFT_CONSULT_SIGN", "price_label": "PRICE_SUB_SOFT_CONSULT_SIGN"},
                    "Special Lighting": {"id": "SUB_SOFT_CONSULT_LIGHT", "unit": "m2", "volume_label": "VOLUME_M2_SUB_SOFT_CONSULT_LIGHT", "price_label": "PRICE_SUB_SOFT_CONSULT_LIGHT"},
                    "Infrastructure Consultant": {"id": "SUB_SOFT_CONSULT_INFRA", "unit": "m2", "volume_label": "VOLUME_M2_SUB_SOFT_CONSULT_INFRA", "price_label": "PRICE_SUB_SOFT_CONSULT_INFRA"},
                    "Amdal (Env. Impact)": {"id": "SUB_SOFT_CONSULT_AMDAL", "unit": "m2", "volume_label": "VOLUME_M2_SUB_SOFT_CONSULT_AMDAL", "price_label": "PRICE_SUB_SOFT_CONSULT_AMDAL"},
                    "Traffic Analysis": {"id": "SUB_SOFT_CONSULT_TRAF", "unit": "m2", "volume_label": "VOLUME_M2_SUB_SOFT_CONSULT_TRAF", "price_label": "PRICE_SUB_SOFT_CONSULT_TRAF"},
                    "Technical Assistant": {"id": "SUB_SOFT_CONSULT_TECH", "unit": "m2", "volume_label": "VOLUME_M2_SUB_SOFT_CONSULT_TECH", "price_label": "PRICE_SUB_SOFT_CONSULT_TECH"},
                    "Topografi (Survey)": {"id": "SUB_SOFT_CONSULT_TOPO", "unit": "m2", "volume_label": "VOLUME_M2_SUB_SOFT_CONSULT_TOPO", "price_label": "PRICE_SUB_SOFT_CONSULT_TOPO"}
                }
            },
            "INSURANCE": {
                "id": "TOTAL_SUB_SOFT_INSURANCE",
                "items": {
                    "CAR Insurance": {"id": "SUB_SOFT_INSURANCE", "unit": "%", "volume_label": "0.12% OF SUBTOTAL_HARD + SUBTOTAL_SOFT EXCL. INSURANCE", "price_label": "PRICE_SUB_SOFT_INSURANCE"}
                }
            }
        }
    }

    # Dependency resolver uses the live variables calculated in Tab 1
    def resolve_dependency(rule_string):
        rule = str(rule_string).strip().upper()
        if rule == "GBA": return gba
        if rule == "GFA": return gfa
        if rule == "SGFA": return sgfa
        if rule == "ROOMS": return rooms
        return 1.0

    st.subheader("Hard Cost Estimator")
    input_mode = st.radio(
        "Select Input Method:", 
        ["Manual (Tabs)", "Blank Paste (Excel)", "Pre-filled Grid"], 
        horizontal=True
    )
    st.divider()

    # ==========================================
    # MODE A: MANUAL NUMBER INPUTS (Tabs)
    # ==========================================
    if input_mode == "Manual (Tabs)":
        categories = list(cost_estimate_framework["HARDCOST"].keys())
        tabs = st.tabs(categories)
        
        for i, category in enumerate(categories):
            with tabs[i]:
                st.subheader(category.title())
                items = cost_estimate_framework["HARDCOST"][category].get("items", {})
                
                for item_name, config in items.items():
                    c1, c2, c3, c4, c5, c6 = st.columns(6, vertical_alignment="bottom")
                    item_id = config["id"]
                    unit = config["unit"]
                    
                    with c1: st.write(f"**{item_name} ({unit})**")
                    with c2: v = st.number_input("Volume", value=config.get("vol_def", 0.0), key=f"v_{item_id}")
                    with c3: p = st.number_input("Unit Price", value=config.get("price_def", 0.0), key=f"p_{item_id}")
                    
                    with c4: 
                        o_val = config.get("other_def", 1.0)
                        label = "Ratio/Pct" if "other_def" in config else "Other"
                        o = st.number_input(label, value=float(o_val), key=f"o_{item_id}")
                    
                    with c5: 
                        dep_str = config.get("dep", "None")
                        dep_val = resolve_dependency(dep_str)
                        
                        if dep_str in ["GBA", "GFA", "SGFA", "ROOMS"]:
                            st.text_input("Dependent", value=f"{dep_str}: {dep_val}", disabled=True, key=f"dep_{item_id}")
                        else:
                            st.caption(f"Dep: {dep_str}")
                    
                    with c6: 
                        total = v * p * o * dep_val
                        st.write(f"Rp {total:,.2f}")

    # ==========================================
    # MODE B: BLANK PASTE (From Excel)
    # ==========================================
    elif input_mode == "Blank Paste (Excel)":
        st.info("Copy 5 columns from Excel: **Item Name | Qty | Price | Percent | Dependencies**")
        
        blank_template = pd.DataFrame(columns=[
            "Item Name", "Qty", "Price", "Percent", "Dependencies"
        ])
        
        pasted_df = st.data_editor(
            blank_template, 
            num_rows="dynamic", 
            use_container_width=True,
            hide_index=True
        )
        
        if not pasted_df.empty:
            st.success("Data successfully pasted! Auto-calculating totals...")
            
            # Clean up the commas so math works!
            for col in ["Qty", "Price", "Percent"]:
                clean_str = pasted_df[col].astype(str).str.replace(',', '', regex=False).str.strip()
                pasted_df[col] = pd.to_numeric(clean_str, errors='coerce').fillna(0)
            
            # Make sure blank percents default to 1 (100%)
            pasted_df["Percent"] = pasted_df["Percent"].replace(0, 1.0)
            
            # Map the dependencies
            pasted_df["Dep_Multiplier"] = pasted_df["Dependencies"].apply(resolve_dependency)
            
            # Calculate Total
            pasted_df["Total Cost (Rp)"] = pasted_df["Qty"] * pasted_df["Price"] * pasted_df["Percent"] * pasted_df["Dep_Multiplier"]
            
            st.dataframe(pasted_df[["Item Name", "Qty", "Dependencies", "Total Cost (Rp)"]], use_container_width=True)
            st.metric("Grand Total", f"Rp {pasted_df['Total Cost (Rp)'].sum():,.2f}")

    # ==========================================
    # MODE C: PRE-FILLED DATAFRAME
    # ==========================================
    elif input_mode == "Pre-filled Grid":
        st.info("Edit the Volume, Price, and Ratio columns. Dependencies are auto-calculated.")
        
        flat_data = []
        for cat, cat_data in cost_estimate_framework["HARDCOST"].items():
            for item_name, config in cat_data.get("items", {}).items():
                dep_str = config.get("dependent_label", "None") # Fixed key lookup
                dep_val = resolve_dependency(dep_str)
                
                flat_data.append({
                    "Category": cat,
                    "Item": item_name,
                    "Unit": config["unit"],
                    "Volume": config.get("vol_def", 0.0),
                    "Price": config.get("price_def", 0.0),
                    "Ratio/Other": config.get("other_def", 1.0),
                    "Dep Rule": dep_str,
                    "Dep Value": dep_val
                })
                
        df = pd.DataFrame(flat_data)
        
        edited_df = st.data_editor(
            df,
            disabled=["Category", "Item", "Unit", "Dep Rule", "Dep Value"],
            hide_index=True,
            use_container_width=True,
            column_config={
                "Volume": st.column_config.NumberColumn("Volume", format="%.2f"),
                "Price": st.column_config.NumberColumn("Unit Price (Rp)", format="%d"),
            }
        )
        
        edited_df["Total (Rp)"] = edited_df["Volume"] * edited_df["Price"] * edited_df["Ratio/Other"] * edited_df["Dep Value"]
        
        st.subheader("Calculated Totals")
        st.dataframe(
            edited_df[["Category", "Item", "Total (Rp)"]], 
            use_container_width=True,
            hide_index=True,
            column_config={"Total (Rp)": st.column_config.NumberColumn(format="Rp %.2f")}
        )
        
        grand_total = edited_df["Total (Rp)"].sum()
        st.metric("Grand Total Hardcost (Displayed Items)", f"Rp {grand_total:,.2f}")

# ==========================================
# SOFT COST
# ==========================================
with tab_soft_cost:
    sub_tabs_soft = st.tabs([
        "12. Consultancy Services", "15. Insurance"
    ])

    # --- 12. CONSULTANCY ---
    with sub_tabs_soft[0]:
        st.subheader("Consultancy Services")

        c1, c2, c3, c4, c5, c6 = st.columns(6, vertical_alignment="bottom")
        with c1: st.write("**Quantity Surveyor (bln)**")
        with c2: v_c_qs = st.number_input("Volume", value=0.0, key="v_c_qs")
        with c3: p_c_qs = st.number_input("Unit Price", value=0.0, key="p_c_qs")
        with c4: o_c_qs = st.number_input("Other", value=1.0, key="o_c_qs")
        with c5: dep_c_qs = 1.0; st.caption("Dep: None")
        with c6: st.write(f"Rp {v_c_qs*p_c_qs*o_c_qs*dep_c_qs:,.2f}")

        c1, c2, c3, c4, c5, c6 = st.columns(6, vertical_alignment="bottom")
        with c1: st.write("**Project Management (bln)**")
        with c2: v_c_pm = st.number_input("Volume", value=0.0, key="v_c_pm")
        with c3: p_c_pm = st.number_input("Unit Price", value=0.0, key="p_c_pm")
        with c4: o_c_pm = st.number_input("Other", value=1.0, key="o_c_pm")
        with c5: dep_c_pm = 1.0; st.caption("Dep: None")
        with c6: st.write(f"Rp {v_c_pm*p_c_pm*o_c_pm*dep_c_pm:,.2f}")

        c1, c2, c3, c4, c5, c6 = st.columns(6, vertical_alignment="bottom")
        with c1: st.write("**Architectural Consultant (m2)**")
        with c2: v_c_arch = st.number_input("Volume", value=0.0, key="v_c_arch")
        with c3: p_c_arch = st.number_input("Unit Price", value=0.0, key="p_c_arch")
        with c4: o_c_arch = st.number_input("Other", value=1.0, key="o_c_arch")
        with c5: dep_c_arch = 1.0; st.caption("Dep: None")
        with c6: st.write(f"Rp {v_c_arch*p_c_arch*o_c_arch*dep_c_arch:,.2f}")

        c1, c2, c3, c4, c5, c6 = st.columns(6, vertical_alignment="bottom")
        with c1: st.write("**Structural Consultant (m2)**")
        with c2: v_c_str = st.number_input("Volume", value=0.0, key="v_c_str")
        with c3: p_c_str = st.number_input("Unit Price", value=0.0, key="p_c_str")
        with c4: o_c_str = st.number_input("Other", value=1.0, key="o_c_str")
        with c5: dep_c_str = 1.0; st.caption("Dep: None")
        with c6: st.write(f"Rp {v_c_str*p_c_str*o_c_str*dep_c_str:,.2f}")

        c1, c2, c3, c4, c5, c6 = st.columns(6, vertical_alignment="bottom")
        with c1: st.write("**MEP Consultant (m2)**")
        with c2: v_c_mep = st.number_input("Volume", value=0.0, key="v_c_mep")
        with c3: p_c_mep = st.number_input("Unit Price", value=0.0, key="p_c_mep")
        with c4: o_c_mep = st.number_input("Other", value=1.0, key="o_c_mep")
        with c5: dep_c_mep = 1.0; st.caption("Dep: None")
        with c6: st.write(f"Rp {v_c_mep*p_c_mep*o_c_mep*dep_c_mep:,.2f}")
        
        c1, c2, c3, c4, c5, c6 = st.columns(6, vertical_alignment="bottom")
        with c1: st.write("**Interior Designer (m2)**")
        with c2: v_c_int = st.number_input("Volume", value=0.0, key="v_c_int")
        with c3: p_c_int = st.number_input("Unit Price", value=0.0, key="p_c_int")
        with c4: o_c_int = st.number_input("Other", value=1.0, key="o_c_int")
        with c5: dep_c_int = 1.0; st.caption("Dep: None")
        with c6: st.write(f"Rp {v_c_int*p_c_int*o_c_int*dep_c_int:,.2f}")

        c1, c2, c3, c4, c5, c6 = st.columns(6, vertical_alignment="bottom")
        with c1: st.write("**Landscaping Consultant (m2)**")
        with c2: v_c_lnd = st.number_input("Volume", value=0.0, key="v_c_lnd")
        with c3: p_c_lnd = st.number_input("Unit Price", value=0.0, key="p_c_lnd")
        with c4: o_c_lnd = st.number_input("Other", value=1.0, key="o_c_lnd")
        with c5: dep_c_lnd = 1.0; st.caption("Dep: None")
        with c6: st.write(f"Rp {v_c_lnd*p_c_lnd*o_c_lnd*dep_c_lnd:,.2f}")

        c1, c2, c3, c4, c5, c6 = st.columns(6, vertical_alignment="bottom")
        with c1: st.write("**Soil Investigation (m2)**")
        with c2: v_c_soil = st.number_input("Volume", value=0.0, key="v_c_soil")
        with c3: p_c_soil = st.number_input("Unit Price", value=0.0, key="p_c_soil")
        with c4: o_c_soil = st.number_input("Other", value=1.0, key="o_c_soil")
        with c5: dep_c_soil = 1.0; st.caption("Dep: None")
        with c6: st.write(f"Rp {v_c_soil*p_c_soil*o_c_soil*dep_c_soil:,.2f}")

        c1, c2, c3, c4, c5, c6 = st.columns(6, vertical_alignment="bottom")
        with c1: st.write("**Signage Consultant (m2)**")
        with c2: v_c_sig = st.number_input("Volume", value=0.0, key="v_c_sig")
        with c3: p_c_sig = st.number_input("Unit Price", value=0.0, key="p_c_sig")
        with c4: o_c_sig = st.number_input("Other", value=1.0, key="o_c_sig")
        with c5: dep_c_sig = 1.0; st.caption("Dep: None")
        with c6: st.write(f"Rp {v_c_sig*p_c_sig*o_c_sig*dep_c_sig:,.2f}")

        c1, c2, c3, c4, c5, c6 = st.columns(6, vertical_alignment="bottom")
        with c1: st.write("**Special Lighting (m2)**")
        with c2: v_c_lit = st.number_input("Volume", value=0.0, key="v_c_lit")
        with c3: p_c_lit = st.number_input("Unit Price", value=0.0, key="p_c_lit")
        with c4: o_c_lit = st.number_input("Other", value=1.0, key="o_c_lit")
        with c5: dep_c_lit = 1.0; st.caption("Dep: None")
        with c6: st.write(f"Rp {v_c_lit*p_c_lit*o_c_lit*dep_c_lit:,.2f}")

        c1, c2, c3, c4, c5, c6 = st.columns(6, vertical_alignment="bottom")
        with c1: st.write("**Infrastructure Consultant (m2)**")
        with c2: v_c_inf = st.number_input("Volume", value=0.0, key="v_c_inf")
        with c3: p_c_inf = st.number_input("Unit Price", value=0.0, key="p_c_inf")
        with c4: o_c_inf = st.number_input("Other", value=1.0, key="o_c_inf")
        with c5: dep_c_inf = 1.0; st.caption("Dep: None")
        with c6: st.write(f"Rp {v_c_inf*p_c_inf*o_c_inf*dep_c_inf:,.2f}")

        c1, c2, c3, c4, c5, c6 = st.columns(6, vertical_alignment="bottom")
        with c1: st.write("**Amdal (Env. Impact) (m2)**")
        with c2: v_c_amd = st.number_input("Volume", value=0.0, key="v_c_amd")
        with c3: p_c_amd = st.number_input("Unit Price", value=0.0, key="p_c_amd")
        with c4: o_c_amd = st.number_input("Other", value=1.0, key="o_c_amd")
        with c5: dep_c_amd = 1.0; st.caption("Dep: None")
        with c6: st.write(f"Rp {v_c_amd*p_c_amd*o_c_amd*dep_c_amd:,.2f}")

        c1, c2, c3, c4, c5, c6 = st.columns(6, vertical_alignment="bottom")
        with c1: st.write("**Traffic Analysis (m2)**")
        with c2: v_c_tra = st.number_input("Volume", value=0.0, key="v_c_tra")
        with c3: p_c_tra = st.number_input("Unit Price", value=0.0, key="p_c_tra")
        with c4: o_c_tra = st.number_input("Other", value=1.0, key="o_c_tra")
        with c5: dep_c_tra = 1.0; st.caption("Dep: None")
        with c6: st.write(f"Rp {v_c_tra*p_c_tra*o_c_tra*dep_c_tra:,.2f}")

        c1, c2, c3, c4, c5, c6 = st.columns(6, vertical_alignment="bottom")
        with c1: st.write("**Technical Assistant (m2)**")
        with c2: v_c_tch = st.number_input("Volume", value=0.0, key="v_c_tch")
        with c3: p_c_tch = st.number_input("Unit Price", value=0.0, key="p_c_tch")
        with c4: o_c_tch = st.number_input("Other", value=1.0, key="o_c_tch")
        with c5: dep_c_tch = 1.0; st.caption("Dep: None")
        with c6: st.write(f"Rp {v_c_tch*p_c_tch*o_c_tch*dep_c_tch:,.2f}")

        c1, c2, c3, c4, c5, c6 = st.columns(6, vertical_alignment="bottom")
        with c1: st.write("**Topografi (Survey) (m2)**")
        with c2: v_c_top = st.number_input("Volume", value=0.0, key="v_c_top")
        with c3: p_c_top = st.number_input("Unit Price", value=0.0, key="p_c_top")
        with c4: o_c_top = st.number_input("Other", value=1.0, key="o_c_top")
        with c5: dep_c_top = 1.0; st.caption("Dep: None")
        with c6: st.write(f"Rp {v_c_top*p_c_top*o_c_top*dep_c_top:,.2f}")

    # --- 15. INSURANCE ---
    with sub_tabs_soft[1]:
        st.subheader("Insurance")
        c1, c2, c3, c4, c5, c6 = st.columns(6, vertical_alignment="bottom")
        with c1: st.write("**Insurance (%)**")
        with c2: v_ins = st.number_input("Volume (%)", value=0.12, key="v_ins")
        with c3: p_ins = st.number_input("Est. Subtotal Hard+Soft", value=0.0, key="p_ins")
        with c4: o_ins = st.number_input("Other", value=1.0, key="o_ins")
        with c5: dep_ins = 1.0; st.caption("Dep: None")
        with c6: st.write(f"Rp {(v_ins/100)*p_ins*o_ins*dep_ins:,.2f}")
