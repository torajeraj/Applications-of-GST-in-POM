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
  git clone https://github.com/torajeraj/Applications-of-GST-in-POM.git
  

    Crucial File Placement Rule:

    All Python scripts (Login.py, main_app.py, and the individual module files) must be kept together in the same directory. The data folder (/data) containing the Excel and JSON files must also remain in its relative position so the modules can reference them directly.

### Step 2: Install Required Python Libraries

The software requires several standard scientific Python libraries. 

---

## 4. Running the Application

Once the required libraries are installed, start the software by running the login script:

    Open your terminal or Command Prompt.
    Navigate to the project folder where the files are extracted (for example: cd C:\Users\YourName\Grey-Systems-POM).
    Execute the following command:

         python Login.py                                                            bash
  
   
    The GST Login window will appear. Click the entry confirmation button.
    The Main Application Window will open, displaying the navigation tree on the left.
    Expand any branch (e.g., Grey Forecasting, Grey Line Balancing, Grey MRP), select the desired method, and the module interface will load in the main panel.

---

## 5. Using the Example Datasets (Excel & JSON)

To reproduce the numerical examples presented in the book:

    When a module is loaded, click the file selection button (e.g., Browse / Load File).
    Navigate to the data/excel_examples/ or data/json_examples/ folder.
    Select the file corresponding to the chapter or method you are studying (e.g., Chapter03_MRP_Simple.xlsx).
    Click Run / Solve to view the step-by-step computational results and figures without entering numerical matrices manually.

---

## 6. Citation

If you use this software or the accompanying datasets in your academic research or teaching, please cite both the book and the software archive:

      Karimi, T., and Lin, Y. (2027). Application of Grey Systems Theory in Production and Operations Management. Springer.                                                             
      Karimi, T., and Lin, Y. (2027). Application of Grey Systems Theory in Production and Operations Management (Version 1.0.0) [Computer software]. Zenodo. https://doi.org/10.5281/zenodo.23132816

---

## 7. License
  This project is distributed for academic, educational, and research purposes. Please refer to the repository license for permissions and usage rights.
---
