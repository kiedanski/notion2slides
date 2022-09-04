# %%
from typing import Union
from notion_client import Client
from fastapi import FastAPI, Form, Request, Response, Cookie
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from parse import get_slide
from mangum import Mangum
import os

from pathlib import Path


def get_client(token):
    notion = Client(auth=token)
    return notion


def list_pages(client, database_id):
    page_list = client.databases.query(database_id=database_id)["results"]

    pages = {}
    for page in page_list:
        title = page["properties"]["Name"]["title"][0]["plain_text"]
        pages[title] = page["id"]
    return pages


app = FastAPI()
handler = Mangum(app)
templates = Jinja2Templates(directory="templates")


@app.post("/slide", response_class=HTMLResponse)
async def login(
    slide_id: str = Form(), notion_token: Union[str, None] = Cookie(default=None)
):

    client = get_client(notion_token)
    return get_slide(slide_id, client)


@app.get("/", response_class=HTMLResponse)
async def read_item(request: Request):
    print(list(Path(".").glob("*")))
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/login", response_class=HTMLResponse)
async def read_item(
    response: Response,
    request: Request,
    notion_token: str = Form(),
    database_id: str = Form(),
):

    # response.set_cookie("hola", value="chau", httponly=True, secure=False)
    response.set_cookie(
        "notion_token",
        value=notion_token,
        httponly=True,
        secure=False,
    )
    c = get_client(notion_token)
    pages = list_pages(c, database_id)
    resp = templates.TemplateResponse(
        "form.html", {"request": request, "slides": pages}
    )
    resp.set_cookie(
        "notion_token",
        value=notion_token,
        httponly=True,
        secure=False,
    )
    return resp
