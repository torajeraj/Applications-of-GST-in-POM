# Applications-of-GST-in-POM
Python Software Suite for the Book: 
This repository contains the Python source code and instance datasets for the Book:

    "Applications of Grey System Theory in Production and Operations Management (Springer)"
   
Overview

These codes implements a heuristic approach based on Grey Systems Theory to solve Assembly Line Balancing Problems (ALBP) where task processing times are uncertain and represented as grey numbers.
Repository Contents

    GreyCOMSOAL_48tasks.json: The 48-task test instance used for scalability and sensitivity analysis.
    Python implementation scripts for the Grey COMSOAL algorithm and regret-based ranking procedure.
    To run the code properly, ensure that all the following files are located in the same directory (side by side):
    main_app.py (The main execution script)
    grey_comparison.py (Required module for grey comparison and ranking procedures)
    grey_number_operation.py (Required module for grey arithmetic)
    line_balancing.py((Required module for entering line balancing data)
    comsol.py (the main algorithem)
    GreyCOMSOAL_48tasks.json (The 48-task test instance used for scalability and sensitivity analysis)

Usage

    Before running the algorithm, ensure you have Python installed along with the required libraries.
    Ensure you have Python installed.
    Ensure that all Python script files (including main.py, grey_compar.py, and any other helper files) as well as the JSON dataset are placed together in the same folder.
    Open your terminal or command prompt in that directory.
    Execute the main script:
    Load the dataset ( GreyCOMSOAL_48tasks.json).
    Run the model

Manuscript Status

This repository serves as supplemental material to support the manuscript titled: "Assembly Line Balancing with Grey Task Times: A Grey COMSOAL Heuristic"
Status: Currently under peer review at Grey Systems: Theory and Application.
