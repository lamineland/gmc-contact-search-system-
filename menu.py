"""Text menu for the contact book.

Run with:  python menu.py
"""

from __future__ import annotations

from contacts import Contact, ContactBook


def _print_menu(output) -> None:
    output("")
    output("1. Add Contact")
    output("2. Search by Keyword")
    output("3. Search by Exact Name")
    output("4. View All (Forward)")
    output("5. View All (Backward)")
    output("6. Exit")
    output("")


def _read(prompt: str, input_fn) -> str:
    """Read one line. input() shows the prompt; EOF ends the menu."""
    return input_fn(prompt)


def _print_contacts(contacts: list[Contact], output) -> None:
    if not contacts:
        output("No contacts yet. Add one with option 1.")
        return
    for contact in contacts:
        output(str(contact))


def _add(book: ContactBook, input_fn, output) -> None:
    name = _read("Name: ", input_fn)
    phone = _read("Phone: ", input_fn)
    try:
        book.add(name, phone)
    except ValueError as exc:
        output(str(exc))
        return
    output("Contact added.")


def _search_keyword(book: ContactBook, input_fn, output) -> None:
    keyword = _read("Search keyword: ", input_fn)
    try:
        matches = book.search_keyword(keyword)
    except ValueError as exc:
        output(str(exc))
        return
    if not matches:
        output("No match found.")
        return
    for contact in matches:
        output(f"Match found: {contact}")


def _search_name(book: ContactBook, input_fn, output) -> None:
    name = _read("Name: ", input_fn)
    try:
        contact = book.search_name(name)
    except ValueError as exc:
        output(str(exc))
        return
    if contact is None:
        output(f"No contact named {name.strip()}.")
        return
    output(f"Match found: {contact}")


def run_menu(book: ContactBook | None = None, input_fn=input, output_fn=print) -> None:
    """Run the menu until the user chooses Exit or closes the input."""
    if book is None:
        book = ContactBook()

    while True:
        _print_menu(output_fn)
        try:
            choice = _read("Enter option: ", input_fn).strip()
        except EOFError:
            output_fn("")
            return

        try:
            if choice == "1":
                _add(book, input_fn, output_fn)
            elif choice == "2":
                _search_keyword(book, input_fn, output_fn)
            elif choice == "3":
                _search_name(book, input_fn, output_fn)
            elif choice == "4":
                _print_contacts(book.forward(), output_fn)
            elif choice == "5":
                _print_contacts(book.backward(), output_fn)
            elif choice == "6":
                return
            else:
                output_fn("Choose an option from 1 to 6.")
        except EOFError:
            output_fn("")
            return


if __name__ == "__main__":
    run_menu()
