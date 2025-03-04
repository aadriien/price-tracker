# 🛒 price-tracker

## Description

Ever wonder if that “deal” was actually a deal? `price-tracker` is a tool that automates the tracking of  purchases over time by pulling purchase history from emails and analyzing price trends. This project is a **work in progress**, with plenty of room to grow—because tracking prices is one thing, but making sense of them is another. 


## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [Features](#features)
- [Design Choices](#design-choices)
- [Ethical Considerations](#ethical-considerations)
- [Future Plans](#future-plans)


## Installation

### Prerequisites

- Python 3.x
- Poetry (for dependency management)
- Gmail API access (if using email parsing)

### Setup

```sh
# Clone the repository
git clone https://github.com/aadriien/price-tracker.git

# Navigate to the project directory
cd price-tracker

# Install dependencies and run setup
make all
```


## Usage

### Running the Tracker

```sh
make all
```

What happens when you run this?

1. It filters and fetches past purchases from email inbox (no manual ingestion!).
2. It checks live product prices on the web (ethically, of course).
3. It crunches the numbers to spot trends, storing the results.
4. It generates insights to understand when prices drop, spike, or just do weird things.


## Features

- **📬 Smart email parsing**: Automatically extracts and parses product receipts from inbox.
- **🌐 Live price checks**: Scrapes current prices for comparison (see ethics below!).
- **📊 Historical trend tracking**: Logs past prices to analyze shifts over time.
- **📈 Rolling averages**: Smooths out random price spikes for a comprehensive picture.
- **💾 Data export options**: Saves insights for deeper analysis and cross-references.


## Design Choices

- **Modular separation**: Email parsing, web scraping, and analysis are separate pieces, making future tweaks easier (e.g. activation flags).
- **Scalable and functional**: Structured data storage for efficient long-term tracking.
- **Built for iteration**: Features are built step by step, focusing on foundational elements first, and with an emphasis on reusability.
- **Privacy-conscious**: Only processes purchase-related emails—no snooping beyond that.
- **Intentional obfuscation**: Certain files (like `.env`) are `.gitignore`'d to prevent potential misuse of features, because security matters.


## Ethical Considerations 

This project’s web scraping component is **for learning purposes**—think of it as a sandbox for mindfully experimenting with web security, networking, parsing techniques, and dynamic content. The real goal is to **build skills, not just track prices**.

To keep things ethical and responsible: 🚦

- **Sensitive details are redacted**: Some required files and fields are intentionally omitted.
- **Not plug-and-play**: If you're cloning this repo, don’t expect the scraper to magically work. It’s meant for experimentation, so the stuff that goes live is hidden. Any modifications are **your responsibility**.
- **Respect website policies**: If you choose to implement scraping, it's at your own discretion. Be mindful of robots.txt and ethical guidelines.


## Future Plans 

Plenty more to come, including:

- **Smarter trend analysis**: More sophisticated models to detect and describe the trends that really matter.
- **Key data visualizations**: Because numbers are easier to digest when they're easier to access.
- **Improved automation**: Reducing manual steps to make tracking seamless, even with flexible data.
- **Stronger security**: Activation flags, usage alerts, and separate environments for a controlled system.

This project will evolve as I explore new ideas, fine-tune the approach, and, most importantly, continue learning. Stay tuned! 🚀

