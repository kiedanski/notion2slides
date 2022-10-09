import json

H1 = "heading_1"
H2 = "heading_2"
IMG = "image"
BLT = "bulleted_list_item"
PAR = "paragraph"
CODE = "code"


def get_slide(slide_id: str, client):
    data = client.blocks.children.list(slide_id)
    results = data["results"]
    next_cursor = data.get("next_cursor", None)
    while next_cursor is not None:
        data = client.blocks.children.list(slide_id, start_cursor=next_cursor)
        results.extend(data["results"])
        next_cursor = data.get("next_cursor", None)

    current_slide = None
    current_list = None
    current_column = None
    slides = []

    with open("raw.json", "w") as fh:
        json.dump(results, fh, indent=2)

    for block in results:
        block_type = block["type"]

        if block_type != BLT and current_list is not None:
            current_list = None

        if block_type == H1:

            if current_column is not None:
                current_column = None

            h1 = block[H1]["rich_text"][0]["plain_text"]
            current_slide = {"type": "slide", "content": [], "name": h1}
            slides.append(current_slide)

        elif block_type == H2:

            h2 = block[H2]["rich_text"]
            if h2[0]["plain_text"].startswith("!!"):
                h2 = ""
            else:
                h2 = proc_rich_text(h2)

            current_column = {"type": "column", "content": [], "name": h2}
            current_slide["content"].append(current_column)

        elif block_type == IMG:
            url = block["image"]["external"]["url"]
            obj = {"type": "image", "url": url}

            if current_column is not None:
                current_column["content"].append(obj)
            elif current_slide is not None:
                current_slide["content"].append(obj)

        elif block_type == BLT:
            text = block["bulleted_list_item"]["rich_text"]
            text = proc_rich_text(text)

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

        elif block_type == CODE:
            obj = {
                "type": CODE,
                "content": block[CODE]["rich_text"][0]["plain_text"],
                "language": block[CODE]["language"],
            }
            if current_column is not None:
                current_column["content"].append(obj)
            elif current_slide is not None:
                current_slide["content"].append(obj)

        elif block_type == PAR:

            text = block["paragraph"]["rich_text"]
            text = proc_rich_text(text)

            obj = {
                "type": PAR,
                "content": text,
            }
            if current_column is not None:
                current_column["content"].append(obj)
            elif current_slide is not None:
                current_slide["content"].append(obj)

        else:
            pass

    with open("templates/style.css", "r") as fh:
        style = fh.read()

    with open("templates/revealjs.html", "r") as fh:
        html = fh.read()
        slides_html = "\n".join(render_slide(s) for s in slides)
        html = html.replace("<!--slides_here>-->", slides_html)
        html = html.replace("/*style_here*/", style)

    return html


# %%


def proc_rich_text(text_list):

    text = ""
    for el in text_list:
        cls = ""
        for k, v in el["annotations"].items():

            if k != "color":
                if v is True:
                    cls += f" c-{k}"
            else:
                if v != "default":
                    cls += f" c-{v}"

        if cls != "":
            t = f'<a class={cls}>{el["plain_text"]}</a>'
        else:
            t = f'<a>{el["plain_text"]}</a>'
        text += t
    return text


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


def render_par(obj):
    content = obj["content"]
    html = f"<p>{content}</p>"
    return html


def render_column(obj):

    html = '<div class="col">\n'
    html += f'<div class="col-name">\n{obj["name"]}\n</div>\n'
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

    content = ""
    if len(obj["content"]) > 0:
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
    "paragraph": render_par,
}
