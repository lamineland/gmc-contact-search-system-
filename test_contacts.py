"""Tests for the contact book, substring search, and text menu."""

import io
import subprocess
import sys
import unittest
from pathlib import Path

import app as app_module
from contacts import ContactBook, DoublyLinkedList, naive_substring_search
from menu import run_menu

ROOT = Path(__file__).resolve().parent


class NaiveSearchTests(unittest.TestCase):
    def test_match_at_start_middle_and_end(self):
        self.assertTrue(naive_substring_search("Alice", "Al"))
        self.assertTrue(naive_substring_search("Alice", "lic"))
        self.assertTrue(naive_substring_search("Alice", "ice"))
        self.assertTrue(naive_substring_search("Alice", "Alice"))

    def test_case_insensitive(self):
        self.assertTrue(naive_substring_search("Alice", "al"))
        self.assertTrue(naive_substring_search("alice", "ALI"))

    def test_miss_and_longer_pattern(self):
        self.assertFalse(naive_substring_search("Alice", "Bob"))
        self.assertFalse(naive_substring_search("Al", "Alice"))

    def test_empty_pattern_matches(self):
        self.assertTrue(naive_substring_search("Alice", ""))
        self.assertTrue(naive_substring_search("", ""))

    def test_overlapping_pattern(self):
        self.assertTrue(naive_substring_search("aaa", "aa"))


class ListTests(unittest.TestCase):
    def test_forward_and_backward_follow_the_links(self):
        contacts = DoublyLinkedList()
        first = contacts.append(type("C", (), {"name": "A"})())
        second = contacts.append(type("C", (), {"name": "B"})())
        third = contacts.append(type("C", (), {"name": "C"})())

        self.assertIs(contacts.head, first)
        self.assertIs(contacts.tail, third)
        self.assertIsNone(first.prev)
        self.assertIs(first.next, second)
        self.assertIs(second.prev, first)
        self.assertIs(second.next, third)
        self.assertIs(third.prev, second)
        self.assertIsNone(third.next)

        self.assertEqual([c.name for c in contacts.forward()], ["A", "B", "C"])
        self.assertEqual([c.name for c in contacts.backward()], ["C", "B", "A"])

    def test_empty_list(self):
        contacts = DoublyLinkedList()
        self.assertEqual(contacts.forward(), [])
        self.assertEqual(contacts.backward(), [])


class ContactBookTests(unittest.TestCase):
    def setUp(self):
        self.book = ContactBook()

    def test_add_stores_the_same_object_in_the_list_and_the_table(self):
        added = self.book.add("Alice", "1234567890")
        self.assertIs(added, self.book.search_name("Alice"))
        self.assertIs(added, self.book.forward()[0])
        self.assertIs(added, self.book.contacts.head.contact)
        self.assertIs(self.book.by_name["alice"], self.book.contacts.head.contact)

    def test_exact_lookup_ignores_case_and_extra_space(self):
        added = self.book.add("Alice", "123")
        self.assertIs(self.book.search_name("  ALICE  "), added)
        self.assertIsNone(self.book.search_name("Alicia"))

    def test_keyword_search_walks_insertion_order(self):
        self.book.add("Alice", "1")
        self.book.add("Bob", "2")
        self.book.add("Alicia", "3")
        matches = self.book.search_keyword("li")
        self.assertEqual([c.name for c in matches], ["Alice", "Alicia"])

    def test_keyword_miss(self):
        self.book.add("Alice", "1")
        self.assertEqual(self.book.search_keyword("zzz"), [])

    def test_duplicate_name_is_rejected(self):
        self.book.add("Alice", "1")
        with self.assertRaises(ValueError):
            self.book.add("alice", "2")
        self.assertEqual(len(self.book.forward()), 1)

    def test_blank_fields_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "name"):
            self.book.add("   ", "123")
        with self.assertRaisesRegex(ValueError, "phone"):
            self.book.add("Alice", "  ")
        with self.assertRaisesRegex(ValueError, "keyword"):
            self.book.search_keyword("  ")
        with self.assertRaisesRegex(ValueError, "name"):
            self.book.search_name(" ")
        self.assertEqual(self.book.forward(), [])

    def test_display_order(self):
        self.book.add("Alice", "1")
        self.book.add("Bob", "2")
        self.assertEqual([str(c) for c in self.book.forward()], ["Alice - 1", "Bob - 2"])
        self.assertEqual([str(c) for c in self.book.backward()], ["Bob - 2", "Alice - 1"])


class MenuTests(unittest.TestCase):
    def test_sample_session(self):
        lines = iter(
            [
                "1",
                "Alice",
                "1234567890",
                "1",
                "Bob",
                "222",
                "2",
                "Al",
                "3",
                "Alice",
                "3",
                "Nobody",
                "4",
                "5",
                "9",
                "6",
            ]
        )

        def input_fn(prompt=""):
            del prompt
            return next(lines)

        output = io.StringIO()

        def write(message: str = "") -> None:
            output.write(f"{message}\n")

        run_menu(input_fn=input_fn, output_fn=write)
        text = output.getvalue()
        self.assertIn("1. Add Contact", text)
        self.assertIn("6. Exit", text)
        self.assertIn("Contact added.", text)
        self.assertIn("Match found: Alice - 1234567890", text)
        self.assertIn("No contact named Nobody.", text)
        self.assertIn("Alice - 1234567890\nBob - 222", text)
        self.assertIn("Bob - 222\nAlice - 1234567890", text)
        self.assertIn("Choose an option from 1 to 6.", text)

    def test_cli_process_matches_the_sample(self):
        completed = subprocess.run(
            [sys.executable, str(ROOT / "menu.py")],
            input="1\nAlice\n1234567890\n2\nAl\n6\n",
            text=True,
            capture_output=True,
            check=True,
        )
        self.assertIn("Enter option:", completed.stdout)
        self.assertIn("Name:", completed.stdout)
        self.assertIn("Phone:", completed.stdout)
        self.assertIn("Contact added.", completed.stdout)
        self.assertIn("Search keyword:", completed.stdout)
        self.assertIn("Match found: Alice - 1234567890", completed.stdout)
        self.assertEqual(completed.returncode, 0)


class WebTests(unittest.TestCase):
    def setUp(self):
        app_module.book = ContactBook()
        self.client = app_module.app.test_client()

    def test_empty_home_and_about(self):
        home = self.client.get("/")
        self.assertEqual(home.status_code, 200)
        self.assertIn(b"No contacts yet", home.data)
        about = self.client.get("/about")
        self.assertEqual(about.status_code, 200)
        self.assertIn(b"doubly linked list", about.data)

    def test_add_keyword_exact_and_backward(self):
        added = self.client.post(
            "/contacts",
            data={"name": "Alice", "phone": "1234567890", "order": "forward"},
            follow_redirects=True,
        )
        self.assertIn(b"Contact added.", added.data)
        self.assertIn(b"Alice", added.data)
        self.assertIn(b"1234567890", added.data)

        self.client.post(
            "/contacts",
            data={"name": "Bob", "phone": "222", "order": "forward"},
            follow_redirects=True,
        )

        keyword = self.client.get("/?keyword=Al")
        self.assertIn(b"Match found: Alice -", keyword.data)
        self.assertNotIn(b"Match found: Bob -", keyword.data)

        exact = self.client.get("/?exact=alice")
        self.assertIn(b"Match found: Alice -", exact.data)

        missing = self.client.get("/?exact=Nobody")
        self.assertIn(b"No contact named Nobody.", missing.data)

        backward = self.client.get("/?order=backward")
        body = backward.data.decode()
        self.assertLess(body.index(">Bob<"), body.index(">Alice<"))

        duplicate = self.client.post(
            "/contacts",
            data={"name": "alice", "phone": "999", "order": "forward"},
            follow_redirects=True,
        )
        self.assertIn(b"already in your contacts", duplicate.data)

    def test_blank_keyword_reports_an_error(self):
        response = self.client.get("/?keyword=%20")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Enter a keyword.", response.data)


if __name__ == "__main__":
    unittest.main()
