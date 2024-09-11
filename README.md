# NFL Game Statistics Analysis

## Overview

This project provides an in-depth analysis and prediction system for NFL game statistics, using historical data from 1983 to 2023. The system is designed to clean, preprocess, and analyze game data to derive valuable insights and predictions. It integrates with Firebase for data storage and uses Flask to deliver a user-friendly interface.

## Features

- **Data Import and Preprocessing**: Import game data from various sources (Excel, MS Access) into Firebase. The data is cleaned and preprocessed for consistency and accuracy.
- **Feature Selection**: Systematically analyze features such as game site, day, type, line, SU outcome, points scored, points allowed, and more.
- **Predictive Analysis**: Utilize selected features to predict game outcomes and trends based on historical performance.
- **User Interface**: Provides an interactive UI for querying and retrieving predictions.
- **Deployment**: Hosted on PythonAnywhere for reliable access and scalability.

## Tech Stack

- **Frontend**: HTML, CSS, JavaScript
- **Backend**: Python, Flask
- **Database**: Firebase
- **Deployment**: PythonAnywhere
- **Version Control**: Git, GitHub
- **Project Management**: Jira
- **Data Processing**: Pandas, NumPy
- **APIs**: Flask REST APIs for data retrieval and processing

## Installation

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/shashankkannan/Sports_Statistics.git
   cd Sports_Statistics
   ```

2. **Set Up a Virtual Environment:**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Set Up Firebase:**
   - Configure Firebase and download your `firebase_config.json`.
   - Place `firebase_config.json` in the root directory.

4. **Run the Application:**

   ```bash
   python app.py
   ```

   Access the application at `http://localhost:5000`.

## Usage

1. **Import Data**: Use the provided scripts to import historical NFL game data into Firebase.
2. **Query Predictions**: Use the UI to input queries and retrieve predictions based on historical data.
3. **Analyze Results**: Review predictions and analyze performance trends through the interface.

## Deployment

This project is deployed on [PythonAnywhere](https://www.pythonanywhere.com/). For updates or changes, you can push updates to this repository and redeploy as needed.

## Contact

For any questions or support, please contact:

- **Email**: shashank.kannan.cs@gmail.com
- **GitHub**: [shashankkannan](https://github.com/shashankkannan)
