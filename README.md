
CLI URL Shortener

A lightweight, clean, and cross-platform CLI tool built in Python for shortening URLs, managing custom aliases, tracking click analytics, and setting link expiration dates.


Key Features

1)Smart URL Normalization: Automatically handles missing schemas (converts google.com or www.google.com to https://google.com before saving).

2)Collision Handling: Safely resolves hash and alias collisions using dynamic counter-based seeding without overwriting existing data.


3)Multiple Short Code Modes:

*Standard Hash: Generates fast, unique 6-character SHA-256 short codes.

*Smart Keyword Alias: Parses domain names and paths to create readable, auto-generated aliases.

*Custom Alias: Allows users to define custom short codes.
4)Link Expiration (TTL): Supports setting optional validity periods (in days) to expire links automatically.

5)Direct Browser Redirection & Analytics: Instantly launches destination links in your default web browser while tracking total clicks.

6)Search & View Saved Links: Built-in searching and filtering to query stored links by code or destination URL.

7)Zero External Dependencies: Built strictly using Python standard library for a clean, bloat-free codebase.


Tech Stack

1)Language: Python 3.8+

2)Standard Libraries: hashlib, json, os, re, urllib.parse, webbrowser, datetime


Installation & Setup

1)Clone the Repository:
git clone https://github.com/your-username/cli-url-shortener.git
cd cli-url-shortener

2)Run the Application:
python main.py


CLI Menu Options

=== CLI URL SHORTENER ===
1)Shorten URL (Standard Hash)

2)Shorten URL (Smart Keyword Alias)

3)Shorten URL (Custom Alias)

4)Access Link (Redirect & Open Browser)

5)View & Search Saved Links / Analytics

6)Exit


Project Structure

cli-url-shortener/
├── main.py          # Core CLI application logic
├── urls.json        # Data store for shortened URLs and click metrics
└── README.md        # Project documentation
