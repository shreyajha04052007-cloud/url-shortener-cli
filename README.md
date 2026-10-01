# url-shortener-cli
# URL Shortener CLI

This is a simple command-line URL shortener written in Python. It takes a long URL and generates a short code or lets you pass a custom alias. All data is saved locally in a JSON file.

## How to run

Shorten a link:
python main.py shorten https://google.com

Shorten with custom alias:
python main.py shorten https://google.com --alias mylink

Resolve a short code (and count clicks):
python main.py resolve mylink

Show all saved links:
python main.py list
