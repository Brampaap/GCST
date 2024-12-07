main = """
<style>
    @media (max-width: 50.5rem) {
        .stMainBlockContainer {
            max-width: None;
        }
    }
    /* Кнопки и верного ответа по горизонтали */
    .stColumn.st-emotion-cache-12w0qpk.e1f1d6gn3 {
        margin-top: 5px;
    }
    .stElementContainer:has(> .stAudio) {
        display:none;
    }

    .text-container {
        position: relative;
        display: inline-block;
        width: 100%;
    }

    span {
        word-break: break-all; 
    }

    iframe {
        position: fixed;
        bottom: 0;
        z-index: 100;
    }

    .st-emotion-cache-8ijwm3 {
        height: 48px;
    }

    .stApp [data-testid="stToolbar"]{
        display:none;
    }

    .st-emotion-cache-qcqlej{
        display:none;
    }

    .block-container {
        padding: 2rem 1rem 10rem 1rem;
    }
</style>
        """

show_audio_css = """
<style>
[data-testid="stChatMessageContent"] .stElementContainer:has(> .stAudio) {
    display:block;
}
</style>
"""