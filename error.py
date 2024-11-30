from flask import render_template

from models.page_title import build_title

error_codes = {
    405: {
        "title": "Method Not Allowed",
        "description": "What are you trying to accomplish?",
    },
    404: {
        "title": "Page Not Found",
        "description": "Where are you actually heading to?",
    },
    500: {
        "title": "Internal Server Error",
        "description": "What the hell happpened here?",
    },
}


def get_error(code):
    data = error_codes.get(
        code,
        {"title": "Error", "description": "I don't even want to know how it happened."},
    )

    return data["title"], data["description"]


def handle_error(e):
    title, description = get_error(e.code)
    return (
        render_template(
            "error_view.html",
            pagetitle=build_title(title),
            error_code=str(e.code),
            error_description=description,
        ),
        e.code,
    )
