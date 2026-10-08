"""Contact Search System web interface.

Uses the same ContactBook as menu.py: a doubly linked list for display
order and a hash table for exact name lookup.

Run with:  python app.py
Then open http://127.0.0.1:5050/
"""

from flask import Flask, flash, redirect, render_template, request, url_for

from contacts import ContactBook

app = Flask(__name__)
# Used only for flash messages during local development.
app.secret_key = "dev-contact-search"

book = ContactBook()


def _order() -> str:
    order = request.values.get("order", "forward")
    if order not in ("forward", "backward"):
        return "forward"
    return order


def _page_url(order: str, keyword: str | None, exact: str | None) -> str:
    params: dict[str, str] = {"order": order}
    if keyword is not None:
        params["keyword"] = keyword
    if exact is not None:
        params["exact"] = exact
    return url_for("index", **params)


@app.route("/")
def index():
    """Show the directory, plus keyword and exact-name searches when asked."""
    order = _order()
    keyword = request.args.get("keyword")
    exact = request.args.get("exact")

    keyword_matches = None
    keyword_error = None
    if keyword is not None:
        try:
            keyword_matches = book.search_keyword(keyword)
        except ValueError as exc:
            keyword_error = str(exc)

    exact_contact = None
    exact_missing = False
    exact_error = None
    if exact is not None:
        try:
            exact_contact = book.search_name(exact)
            exact_missing = exact_contact is None
        except ValueError as exc:
            exact_error = str(exc)

    contacts = book.forward() if order == "forward" else book.backward()
    return render_template(
        "index.html",
        order=order,
        contacts=contacts,
        keyword="" if keyword is None else keyword,
        keyword_active=keyword is not None,
        keyword_matches=keyword_matches,
        keyword_error=keyword_error,
        exact="" if exact is None else exact,
        exact_active=exact is not None,
        exact_contact=exact_contact,
        exact_missing=exact_missing,
        exact_error=exact_error,
        forward_url=_page_url("forward", keyword, exact),
        backward_url=_page_url("backward", keyword, exact),
        clear_keyword_url=_page_url(order, None, exact),
        clear_exact_url=_page_url(order, keyword, None),
    )


@app.post("/contacts")
def add_contact():
    """Add a contact, then return to the directory."""
    order = _order()
    keyword = request.form.get("keyword") if "keyword" in request.form else None
    exact = request.form.get("exact") if "exact" in request.form else None
    try:
        book.add(request.form.get("name", ""), request.form.get("phone", ""))
    except ValueError as exc:
        flash(str(exc), "error")
    else:
        flash("Contact added.", "success")
    return redirect(_page_url(order, keyword, exact))


@app.route("/about")
def about():
    """Explain how contacts are stored and searched."""
    return render_template("about.html")


if __name__ == "__main__":
    # Port 5050: macOS AirPlay Receiver already occupies port 5000.
    app.run(debug=True, port=5050)
