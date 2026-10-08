# Contact Search System

A contact book with two ways to use it: a text menu, and a small Flask page.
Contacts live in memory (no database). Each contact is stored once and
referenced by both a doubly linked list and a hash table.

## Features

- Add a contact with a name and a phone number
- Search names with naive substring matching
- Look up an exact name through a Python dictionary
- Read every contact forward or backward through a doubly linked list

## Project structure

```
contact-search-system/
├── contacts.py         # Contact, doubly linked list, hash table, naive search
├── menu.py             # Text menu
├── app.py              # Flask pages over the same contact book
├── templates/
├── static/style.css
├── test_contacts.py
├── requirements.txt
└── README.md
```

## Setup

```bash
cd contact-search-system
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

## Text menu

```bash
.venv/bin/python menu.py
```

```
1. Add Contact
2. Search by Keyword
3. Search by Exact Name
4. View All (Forward)
5. View All (Backward)
6. Exit
```

## Web page

```bash
.venv/bin/python app.py
```

Then open http://127.0.0.1:5050/ in your browser.

The app uses port 5050 because macOS AirPlay Receiver occupies port 5000.
Restarting the server clears the contacts.

## Tests

```bash
.venv/bin/python -m unittest test_contacts.py
```
