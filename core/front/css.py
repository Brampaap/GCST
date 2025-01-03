main = """
<style>
    [data-testid='stHeaderActionElements'] {
		display: none;
	}
    .stAppHeader {
        display: none;
    }
    .stProgress {
        position: fixed;
        bottom: 0;
        padding-bottom: 8px;
        width: 44rem;
        z-index: 101;z
    }

    .stProgress:has(> .st-emotion-cache-16bwex0) {
        background-color: rgb(14, 17, 23);
    }
    .stProgress:has(> .st-emotion-cache-169zpbd) {
        background-color: white;
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
    @media (max-width: 50.5rem) {
        .stMainBlockContainer {
            max-width: None;
        }
        .stProgress {
            width: 92%;
        }
		ol li {
		  margin-left: -10px !important;
		}
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