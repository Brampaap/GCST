import html
import streamlit as st

def reset_empty_input(context):
    context.continueMode = False
    context.recorded_audio = None
    placeholder = st.empty() # Уход от долгой перезагрузки
    with placeholder: st.write("")


def render_no_copy_text(text: str) -> str:
    rendered = f"""
        <style>
            .overlay {{
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background-color: transparent;
                z-index: 10;
            }}

            .no-select-text {{
                pointer-events: none;
            }}

            .no-select-text > p {{
                -webkit-user-select: none; /* Safari */
                -moz-user-select: none;
                -ms-user-select: none;
                user-select: none;
            }}
        </style>
        
        <div class="text-container">
            <div class="overlay"></div>
            <div class="no-select-text">
                <p>{html.escape(text)}</p>
            </div>  
        </div>
    """
    return rendered
