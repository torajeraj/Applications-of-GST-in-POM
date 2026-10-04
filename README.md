# Application of Grey Systems Theory in Production and Operations Management

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.23132816.svg)](https://doi.org/10.5281/zenodo.23132816)

This repository hosts the official Python companion software and datasets for the book:
**"Application of Grey Systems Theory in Production and Operations Management"** (published by Springer).

The software provides an integrated graphical user interface (GUI) and 18 dedicated computational modules implementing grey forecasting, incidence analysis, grey number operations and comparisons, line balancing, sequencing, Grey Material Requirements Planning (Grey-MRP), and grey aggregate planning.

---

## 1. Overview and Architecture

The software is structured modularly:
* **`Login.py`**: The entry point presenting the book and software context.
* **`main_app.py`**: The primary control dashboard featuring a hierarchical tree structure to launch specific algorithms.
* **Algorithmic Modules**: 18 standalone Python scripts implementing specific computational methods.
* **Example Datasets (`/data`)**: Pre-formatted Excel (`.xlsx`) and JSON (`.json`) datasets matching the numerical examples discussed in each chapter of the book, eliminating the need for manual data entry.

---

## 2. System Requirements and Prerequisites

To run this application, you only need Python installed on your local computer (Windows, macOS, or Linux).

### Step 1: Install Python
If Python is not already installed on your system:
1. Download Python (version 3.9 or higher) from the official website: [https://www.python.org/downloads/](https://www.python.org/downloads/).
2. **Important for Windows users:** During installation, check the box that says **"Add Python to PATH"** before clicking *Install Now*.

### Step 2: Note on Google Colab vs. Local Execution
* **Local Machine (Recommended):** The software relies on a graphical desktop interface (`tkinter`). It is designed to be executed directly on your local computer.
* **Google Colab:** Because Google Colab runs in a cloud environment without a native desktop display, running interactive desktop GUI windows requires additional virtual display streaming setups. For a seamless experience, running the application locally on your PC or laptop is strongly advised.

---

## 3. Installation and Setup

### Step 1: Download the Files
You do not need prior experience with Git to use this software:
* **Option A (Direct Download via Zenodo / GitHub):** Click the green **Code** button at the top of this repository and select **Download ZIP** (or download the source archive from Zenodo). Extract the entire `.zip` archive to a folder of your choice on your computer.
* **Option B (Using Git):** Open your terminal or command prompt and clone the repository:
```bash

