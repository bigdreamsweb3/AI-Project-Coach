import re
import tkinter as tk
from tkinter import scrolledtext


BOLD_PATTERN = re.compile(r"\*\*(.+?)\*\*")


def configure_rich_text(text_widget: scrolledtext.ScrolledText) -> None:
    text_widget.tag_configure("heading", font=("Georgia", 15, "bold"), spacing1=8, spacing3=4)
    text_widget.tag_configure("subheading", font=("Georgia", 12, "bold"), spacing1=6, spacing3=3)
    text_widget.tag_configure("bold", font=("Georgia", 11, "bold"))
    text_widget.tag_configure("body", font=("Georgia", 11), spacing3=3)
    text_widget.tag_configure("label", font=("Georgia", 11, "bold"), foreground="#273043")
    text_widget.tag_configure("bullet", lmargin1=20, lmargin2=38, font=("Georgia", 11), spacing3=3)


def append_plain(text_widget: scrolledtext.ScrolledText, text: str, tag: str = "body") -> None:
    text_widget.insert(tk.END, text, tag)
    text_widget.see(tk.END)


def append_markdown(text_widget: scrolledtext.ScrolledText, markdown_text: str) -> None:
    for raw_line in markdown_text.splitlines():
        line = raw_line.strip()

        if not line:
            text_widget.insert(tk.END, "\n")
            continue

        if line.startswith("### "):
            _insert_inline(text_widget, line[4:] + "\n", "subheading")
            continue

        if line.startswith("## "):
            _insert_inline(text_widget, line[3:] + "\n", "heading")
            continue

        if line.startswith("# "):
            _insert_inline(text_widget, line[2:] + "\n", "heading")
            continue

        if line.startswith(("- ", "* ")):
            text_widget.insert(tk.END, "- ", "bullet")
            _insert_inline(text_widget, line[2:] + "\n", "bullet")
            continue

        _insert_inline(text_widget, line + "\n", "body")

    text_widget.see(tk.END)


def replace_with_markdown(text_widget: scrolledtext.ScrolledText, markdown_text: str) -> None:
    text_widget.delete("1.0", tk.END)
    append_markdown(text_widget, markdown_text)


def _insert_inline(text_widget: scrolledtext.ScrolledText, text: str, base_tag: str) -> None:
    cursor = 0
    for match in BOLD_PATTERN.finditer(text):
        if match.start() > cursor:
            text_widget.insert(tk.END, text[cursor:match.start()], base_tag)
        text_widget.insert(tk.END, match.group(1), "bold")
        cursor = match.end()

    if cursor < len(text):
        text_widget.insert(tk.END, text[cursor:], base_tag)
