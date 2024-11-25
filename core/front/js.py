scroll = """
<script>
    itemsScrollTo = parent.window.document.getElementsByClassName("stButton"); 
    itemsScrollTo[itemsScrollTo.length-1].scrollIntoView();
</script>
"""

post_message_template = """
<script>
    window.parent.parent.postMessage({response_json}, "*");
</script>
"""
