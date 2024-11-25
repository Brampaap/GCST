main = """
<style>
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

    /* Выровнять все кнопки по центру блока в котором они находятся */
    .stButton > button{
        display: block;
        margin-left: auto;
        margin-right: auto;
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
