"""Contacts stored in a doubly linked list and a hash table.

Each contact is one object. The list keeps insertion order so the book can
be read forward or backward. The dict keys the same object by name for an
O(1) exact lookup. Keyword search walks the list and runs a naive substring
scan on each name.
"""

from __future__ import annotations


class Contact:
    """A person stored by name and phone number."""

    def __init__(self, name: str, phone: str) -> None:
        self.name = name
        self.phone = phone

    def __str__(self) -> str:
        return f"{self.name} - {self.phone}"

    def __repr__(self) -> str:
        return f"Contact({self.name!r}, {self.phone!r})"


class Node:
    """One link in the doubly linked list. Holds a contact, not a copy."""

    def __init__(self, contact: Contact) -> None:
        self.contact = contact
        self.prev: Node | None = None
        self.next: Node | None = None


class DoublyLinkedList:
    """Insertion-ordered list with forward and backward traversal."""

    def __init__(self) -> None:
        self.head: Node | None = None
        self.tail: Node | None = None

    def append(self, contact: Contact) -> Node:
        """Add contact at the tail. Returns the new node."""
        node = Node(contact)
        if self.tail is None:
            self.head = node
            self.tail = node
        else:
            node.prev = self.tail
            self.tail.next = node
            self.tail = node
        return node

    def forward(self) -> list[Contact]:
        """Contacts from the first added to the most recent."""
        contacts: list[Contact] = []
        current = self.head
        while current is not None:
            contacts.append(current.contact)
            current = current.next
        return contacts

    def backward(self) -> list[Contact]:
        """Contacts from the most recent back to the first added."""
        contacts: list[Contact] = []
        current = self.tail
        while current is not None:
            contacts.append(current.contact)
            current = current.prev
        return contacts


def naive_substring_search(text: str, pattern: str) -> bool:
    """Return True when pattern occurs inside text.

    Tries every alignment of pattern against text and compares characters
    one by one. Matching is case-insensitive. An empty pattern matches any
    text, including an empty one.
    """
    haystack = text.casefold()
    needle = pattern.casefold()
    if needle == "":
        return True

    text_length = len(haystack)
    pattern_length = len(needle)
    if pattern_length > text_length:
        return False

    last_start = text_length - pattern_length
    for start in range(last_start + 1):
        matched = True
        for offset in range(pattern_length):
            if haystack[start + offset] != needle[offset]:
                matched = False
                break
        if matched:
            return True
    return False


class ContactBook:
    """Contacts shared by a doubly linked list and a name hash table."""

    def __init__(self) -> None:
        self.contacts = DoublyLinkedList()
        # casefold(name) -> the same Contact instance stored in the list
        self.by_name: dict[str, Contact] = {}

    def add(self, name: str, phone: str) -> Contact:
        """Store a new contact in both structures.

        Names are unique ignoring case. Raises ValueError when the name or
        phone is blank, or when that name is already stored.
        """
        clean_name = name.strip()
        clean_phone = phone.strip()
        if not clean_name:
            raise ValueError("Enter a name.")
        if not clean_phone:
            raise ValueError("Enter a phone number.")

        key = clean_name.casefold()
        existing = self.by_name.get(key)
        if existing is not None:
            raise ValueError(
                f"{existing.name} is already in your contacts. "
                "Search by that name, or add a different name."
            )

        contact = Contact(clean_name, clean_phone)
        self.contacts.append(contact)
        self.by_name[key] = contact
        return contact

    def search_keyword(self, keyword: str) -> list[Contact]:
        """Names that contain keyword, in list order.

        Walks the linked list from head to tail and tests each name with
        naive substring search. Raises ValueError when keyword is blank.
        """
        pattern = keyword.strip()
        if not pattern:
            raise ValueError("Enter a keyword.")

        matches: list[Contact] = []
        current = self.contacts.head
        while current is not None:
            if naive_substring_search(current.contact.name, pattern):
                matches.append(current.contact)
            current = current.next
        return matches

    def search_name(self, name: str) -> Contact | None:
        """Exact name lookup through the hash table.

        Returns the stored contact, or None when the name is unknown.
        Raises ValueError when name is blank.
        """
        clean_name = name.strip()
        if not clean_name:
            raise ValueError("Enter a name.")
        return self.by_name.get(clean_name.casefold())

    def forward(self) -> list[Contact]:
        return self.contacts.forward()

    def backward(self) -> list[Contact]:
        return self.contacts.backward()
