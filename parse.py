H1 = "heading_1"
H2 = "heading_2"
IMG = "image"
BLT = "bulleted_list_item"
PAR = "paragraph"
CODE = "code"


def get_slide(slide_id: str, client):
    data = client.blocks.children.list(slide_id)

    current_slide = None
    current_list = None
    current_column = None
    slides = []

    for block in data["results"]:
        block_type = block["type"]

        if block_type != BLT and current_list is not None:
            current_list = None

        if block_type == H1:

            h1 = block[H1]["rich_text"][0]["plain_text"]
            current_slide = {"type": "slide", "content": [], "name": h1}
            slides.append(current_slide)

        if block_type == H2:
            current_column = {
                "type": "column",
                "content": [],
            }
            current_slide["content"].append(current_column)

        if block_type == IMG:
            url = block["image"]["external"]["url"]
            obj = {"type": "image", "url": url}

            if current_column is not None:
                current_column["content"].append(obj)
            elif current_slide is not None:
                current_slide["content"].append(obj)

        if block_type == BLT:
            text = block["bulleted_list_item"]["rich_text"][0]["plain_text"]
            if current_list is None:
                current_list = {
                    "type": "list",
                    "content": [text],
                }
                if current_column is not None:
                    current_column["content"].append(current_list)
                elif current_slide is not None:
                    current_slide["content"].append(current_list)

            elif current_list is not None:
                current_list["content"].append(text)

        if block_type == CODE:
            obj = {
                "type": CODE,
                "content": block[CODE]["rich_text"][0]["plain_text"],
                "language": block[CODE]["language"],
            }
            if current_column is not None:
                current_column["content"].append(obj)
            elif current_slide is not None:
                current_slide["content"].append(obj)

    with open("templates/style.css", "r") as fh:
        style = fh.read()

    with open("templates/revealjs.html", "r") as fh:
        html = fh.read()
        slides_html = "\n".join(render_slide(s) for s in slides)
        html = html.replace("<!--slides_here>-->", slides_html)
        html = html.replace("/*style_here*/", style)
        print(html)

    return html


# %%


# %%
def render_list(obj):
    html = "<ul>\n"
    for elem in obj["content"]:
        html += f'<li class="fragment fade-in-then-semi-out">{elem}</li>\n'
    html += "</ul>\n"
    return html


def render_image(obj):
    url = obj["url"]
    html = f'<img class="my-image" src="{url}">'
    return html


def render_column(obj):

    html = '<div class="col">\n'
    for elem in obj["content"]:
        body = render[elem["type"]](elem)
        html += body
    html += "</div>"
    return html


def render_slide(obj):

    html = """
    <section> 
    <div class="title">
    {title}
    </div>
    <div class="content">
    {content}
    </div>
    </section>
    """

    # html = "<section>"
    # html += f"<div class=\"title\"><a class=\"title-h1\">{obj['name']}</a></div>\n"
    content = ""
    if obj["content"][0]["type"] == "column":
        content += '<div class="container">'
    for elem in obj["content"]:
        body = render[elem["type"]](elem)
        content += body
    if obj["content"][0]["type"] == "column":
        content += "</div>"

    html = html.format(title=obj["name"], content=content)
    return html


def render_code(obj):

    lang = obj["language"]
    html = '<pre><code class="{lang}">'
    html += obj["content"]
    html += "</code></pre>"
    return html


render = {
    "image": render_image,
    "list": render_list,
    "column": render_column,
    "code": render_code,
}
