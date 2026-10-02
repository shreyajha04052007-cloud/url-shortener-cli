CLI URL Shortener

A lightweight, terminal-based URL shortener built with standard Python. It handles unique code generation, custom aliases, redirection simulation, click tracking, and link expiration cleanup.

What It Does

1)SHA-256 Code Generation: Hashes URLs to create short 6-character codes.

2)Custom Aliases: Set your own custom short codes instead of generated hashes.

3)Click Counter: Tracks total redirect attempts for every link.

4)Analytics & Search: Easily check link stats or search through saved URLs.

5)Performance Profiling: Includes a simple decorator (@measure_execution_time) to print execution times in milliseconds.

6)Link Expiration & Cleanup: Automatically flag and purge expired links.

7)Local Persistence: Data stays saved in urls.json, with system logs tracked in app.log.



File Structure
├── main.py          # Main CLI application
├── urls.json        # Saved link mappings
├── app.log          # Runtime activity logs
└── README.md        # Project documentation


How to Run
No external dependencies are required—it uses Python's built-in modules (hashlib, json, os, time, datetime).
Clone the repo: https://github.com/shreyajha04052007-cloud/url-shortener-cli



Execute the program:
python main.py



