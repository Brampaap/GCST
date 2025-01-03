scroll = """
<script>
    itemsScrollTo = parent.window.document.querySelector('.stMain'); 
    itemsScrollTo.scrollTo(0, itemsScrollTo.scrollHeight);
</script>
"""

post_message_template = """
<script>
    window.parent.parent.postMessage({response_json}, "http://localhost:8006");
</script>
"""
