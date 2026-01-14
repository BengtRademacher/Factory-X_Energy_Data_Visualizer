import streamlit as st
from app.config import COLOR_PALETTE


def _color_option_label(name: str, hex_color: str) -> str:
    """Erzeugt ein HTML-Label mit farbigem Text für die Farbauswahl."""
    return f'<span style="color:{hex_color}; font-weight:600;">{name}</span>'


def render_color_selector(label: str, key: str, default_color: str) -> str:
    """
    Rendert eine kombinierte Farbauswahl (Dropdown + optionaler Color Picker).
    
    Args:
        label: Anzeigename für das Widget
        key: Eindeutiger Streamlit-Key
        default_color: Standard-Hex-Farbe
        
    Returns:
        Ausgewählter Hex-Code
    """
    
    # Umkehrmapping Hex -> Name finden
    hex_to_name = {v.lower(): k for k, v in COLOR_PALETTE.items()}
    current_color = st.session_state.get(key, default_color).lower()
    
    # Bestimme initialen Namen
    initial_name = hex_to_name.get(current_color, "Benutzerdefiniert")
    
    # Optionen für die Selectbox vorbereiten (nur Namen)
    color_names = list(COLOR_PALETTE.keys())
    options = color_names + ["Benutzerdefiniert..."]
    
    # Index der aktuellen Auswahl finden
    try:
        if initial_name == "Benutzerdefiniert":
            start_index = len(options) - 1
        else:
            start_index = color_names.index(initial_name)
    except ValueError:
        start_index = len(options) - 1

    # Farbigen Label-Text anzeigen
    if initial_name == "Benutzerdefiniert":
        preview_color = current_color
        preview_name = "Benutzerdefiniert"
    else:
        preview_color = COLOR_PALETTE.get(initial_name, default_color)
        preview_name = initial_name
    
    st.markdown(
        f'<p style="margin-bottom:2px; font-size:0.85em;">{label}: '
        f'<span style="color:{preview_color}; font-weight:700;">■ {preview_name}</span></p>',
        unsafe_allow_html=True
    )

    # Selectbox anzeigen
    selected_option = st.selectbox(
        label,
        options=options,
        index=start_index,
        key=f"sel_{key}",
        label_visibility="collapsed"
    )
    
    # Reinen Namen extrahieren
    selected_name = selected_option.replace("...", "")
    
    if selected_name == "Benutzerdefiniert":
        # Falls benutzerdefiniert, zeige den Color Picker
        color = st.color_picker(
            f"Eigene Farbe", 
            value=current_color if initial_name == "Benutzerdefiniert" else default_color,
            key=key
        )
    else:
        # Falls Standardfarbe, nimm den Wert aus der Palette
        color = COLOR_PALETTE[selected_name]
        st.session_state[key] = color
        
    return color

