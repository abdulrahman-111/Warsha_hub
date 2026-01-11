def get_stylesheet(light=True):
    # --- PALETTE DEFINITION ---
    if light:
        # LIGHT MODE (Exact colors from old_settings.py)
        bg_main = "#F8F9FD"
        text_main = "#2D3436"
        text_sub = "#666666"

        # Cards (Profile, etc.)
        card_bg = "white"
        card_border = "#E5E5F0"

        # --- SETTINGS SPECIFIC (From old_settings.py) ---
        settings_card_bg = "#f8f9fa"  # Light Gray Box
        settings_input_bg = "white"  # White Input
        settings_input_border = "#ddd"  # Light Grey Border
        settings_input_text = "#333"  # Dark Text

        # Buttons
        accent = "#6C5CE7"
        btn_text = "white"
        btn_hover = "#7E6FF2"
        action_btn_hover = "#F0F0F0"

        # Danger Zone
        danger_bg = "#FFF5F5"
        danger_border = "#FFEBEE"

        # Messaging
        msg_user_bg = "white"
        msg_input_bg = "white"
        msg_border = "#E0E0E0"
        msg_hover = "#F5F6FA"

        # Chat Bubbles
        sent_bg = "qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #6C5CE7, stop:1 #5B4BC4)"
        recv_bg = "#F1F2F6"
        recv_text = "#2D3436"

        list_hover = "#F0F0F0"

    else:
        # DARK MODE (The Dark equivalent of old_settings)
        bg_main = "#2C2C2C"
        text_main = "#ECF0F1"
        text_sub = "#BDC3C7"

        # Cards
        card_bg = "#383838"
        card_border = "#555555"

        # --- SETTINGS SPECIFIC ---
        settings_card_bg = "#383838"  # Dark Box
        settings_input_bg = "#444444"  # Darker Input
        settings_input_border = "#666666"  # Grey Border
        settings_input_text = "#ECF0F1"  # White Text

        # Buttons
        accent = "#6C5CE7"
        btn_text = "white"
        btn_hover = "#7E6FF2"
        action_btn_hover = "#666666"

        # Danger Zone
        danger_bg = "#4A2C2C"
        danger_border = "#6E3B3B"

        # Messaging
        msg_user_bg = "#383838"
        msg_input_bg = "#383838"
        msg_border = "#555555"
        msg_hover = "#444444"

        # Chat Bubbles
        sent_bg = "qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #6C5CE7, stop:1 #5B4BC4)"
        recv_bg = "#444444"
        recv_text = "#ECF0F1"

        list_hover = "#555555"

    return f"""
    /* GLOBAL RESET */
    QWidget {{
        background-color: {bg_main};
        color: {text_main};
        font-family: 'Segoe UI', Arial;
    }}

    /* COMMON BUTTONS */
    QPushButton {{
        background-color: {accent};
        color: {btn_text};
        padding: 8px 12px;
        border-radius: 8px;
        font-size: 14px;
        border: none;
    }}
    QPushButton:hover {{ background-color: {btn_hover}; }}

    /* COMMON INPUTS */
    QLineEdit, QTextEdit {{
        background-color: {settings_input_bg};
        border: 2px solid {settings_input_border};
        border-radius: 6px;
        padding: 6px;
        color: {text_main};
    }}

    /* SCROLL & LISTS */
    QScrollArea {{ border: none; background: transparent; }}
    QListWidget {{
        background-color: {card_bg};
        border: 1px solid {card_border};
        border-radius: 6px;
        color: {text_main};
    }}
    QListWidget::item:hover {{
        background-color: {list_hover};
    }}

    /* --- SETTINGS SPECIFIC (The "Old Settings" Look) --- */

    /* 1. The Spacious Input Boxes */
    #SettingsInput {{
        background-color: {settings_input_bg};
        border: 1px solid {settings_input_border};
        border-radius: 8px;
        padding: 12px; 
        font-size: 14px;
        color: {settings_input_text};
    }}
    #SettingsInput:focus {{
        border: 2px solid {accent};
    }}

    /* 2. The Settings Card Container */
    #SettingsCard {{
        background-color: {settings_card_bg};
        border: 1px solid {card_border}; /* Optional border for definition */
        border-radius: 12px;
        padding: 20px;
    }}

    /* 3. The Outline 'Change' Buttons */
    #OutlineButton {{
        background-color: transparent;
        border: 2px solid {accent};
        color: {accent};
        font-weight: bold;
        border-radius: 8px;
    }}
    #OutlineButton:hover {{
        background-color: {accent};
        color: white;
    }}

    /* 4. The Danger 'Delete' Button */
    #DangerButton {{
        background-color: #E74C3C;
        color: white;
        font-weight: bold;
        border: none;
        border-radius: 8px;
    }}
    #DangerButton:hover {{ background-color: #C0392B; }}

    /* 5. Danger Zone Card */
    #DangerCard {{
        background-color: {danger_bg};
        border: 2px solid {danger_border};
        border-radius: 12px;
        padding: 20px;
    }}

    /* --- HOME / PROFILE CARDS --- */
    #PostCard, #ProfileHeader {{
        background-color: {card_bg};
        border: 1px solid {card_border};
        border-radius: 15px;
    }}

    /* --- MESSAGING --- */
    #ConversationItem {{
        background-color: {msg_user_bg};
        border: 1px solid {msg_border};
        border-radius: 12px;
        margin-bottom: 4px;
    }}
    #ConversationItem:hover {{
        border: 1px solid {accent};
        background-color: {msg_hover};
    }}
    #ConversationPanel, #ChatPanel {{
        background-color: {msg_user_bg};
        border: 1px solid {msg_border};
        border-radius: 15px;
    }}
    #ChatHeader, #MessageInputContainer, #ChatHeaderContainer {{
        background-color: {msg_input_bg};
        border-bottom: 1px solid {msg_border};
    }}
    #MessageInputContainer {{ border-top: 1px solid {msg_border}; border-bottom: none; }}

    /* Chat Bubbles */
    #ChatBubbleSent {{
        background: {sent_bg};
        border-radius: 15px;
        border-bottom-right-radius: 2px;
        color: white;
    }}
    #ChatBubbleReceived {{
        background-color: {recv_bg};
        border-radius: 15px;
        border-bottom-left-radius: 2px;
        color: {recv_text};
        border: 1px solid {card_border};
    }}

    /* TEXT UTILS */
    #SubText {{ color: {text_sub}; background: transparent; }}
    #TitleText {{ font-size: 32px; font-weight: bold; color: {text_main}; background: transparent; }}
    #MainText {{ color: {text_main}; background: transparent; }}
    #HeaderText {{ color: {text_main}; font-weight: bold; font-size: 16px; background: transparent; }}

    #ActionButton {{
        background-color: transparent;
        color: {text_sub};
        border: 1px solid {card_border};
    }}
    #ActionButton:hover {{
        background-color: {action_btn_hover};
        color: {accent};
        border-color: {accent};
    }}
    """