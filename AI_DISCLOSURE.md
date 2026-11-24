# AI Disclosure

AI (Claude, by Anthropic) heavily assisted with this project. It wrote most of the code (the Python files in `src/`, the `budget.py` launcher and the tests) and the sample data files.

I made the design decisions. For each one, the AI explained the options and trade-offs, and I chose the approach. In a few cases I accepted its recommendation. These decisions include the allowed categories and currency, rejecting unknown categories and invalid amounts instead of silently fixing them, strict date format, how invalid rows in a file are reported, and how the command-line tool behaves.

I reviewed and tested all AI-written code before submitting it.
