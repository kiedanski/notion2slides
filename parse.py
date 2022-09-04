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

        if block_type == H1:

            h1 = block[H1]["rich_text"][0]["plain_text"]
            obj = {"type": "slide", "content": [], "name": h1}
            if current_slide is None:
                current_slide = obj
            elif current_slide is not None:
                slides.append(current_slide)
                current_slide = obj

            current_list = None  # reset list
            current_column = None

        if block_type == H2:
            obj = {
                "type": "column",
                "content": [],
            }
            if current_column is None:
                current_column = obj
            elif current_column is not None:
                current_slide["content"].append(current_column)
                current_column = obj

            current_list = None  # reset list

        if block_type == IMG:
            url = block["image"]["external"]["url"]
            obj = {"type": "image", "url": url}

            if current_column is not None:
                current_column["content"].append(obj)
            elif current_slide is not None:
                current_slide["content"].append(obj)

            current_list = None  # reset list

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

            current_list = None

    if current_column is not None:
        current_slide["content"].append(current_column)
    slides.append(current_slide)

    with open("templates/revealjs.html", "r") as fh:
        html = fh.read()
        slides_html = "\n".join(render_slide(s) for s in slides)
        print(slides_html)
        html = html.replace("<!--slides_here>-->", slides_html)

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

    html = "<section>"
    html += f"<h1>{obj['name']}</h1>\n"
    if obj["content"][0]["type"] == "column":
        html += '<div class="container">'
    for elem in obj["content"]:
        body = render[elem["type"]](elem)
        html += body

    if obj["content"][0]["type"] == "column":
        html += "</div>"
    html += "</section>"
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
