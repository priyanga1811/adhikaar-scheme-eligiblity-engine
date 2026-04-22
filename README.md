# Adhikaar – Scheme Eligibility Engine

## Overview

**Adhikaar – Scheme Eligibility Engine** is an AI-assisted, rule-based application developed to help users identify government welfare schemes for which they may be eligible. The system accepts user details in simple natural language, preprocesses the input into structured data, and matches it against predefined eligibility criteria to recommend relevant schemes.

This project is designed to simplify access to welfare information by making scheme discovery more user-friendly, accessible, and efficient. It demonstrates the practical application of AI/ML concepts such as preprocessing, rule-based inference, recommendation logic, and explainable outputs in a social welfare domain.

---

## Key Features

- Accepts user input in plain natural language
- Preprocesses and structures unstructured user input
- Matches user details against predefined eligibility rules
- Displays eligible government schemes in a clear format
- Supports PDF generation for downloadable results
- Provides text-to-speech output for accessibility
- Uses a JSON-based scheme dataset for easy updates and maintenance

---

## Objectives

- To simplify the process of identifying eligible government schemes
- To reduce the difficulty users face in understanding complex eligibility rules
- To build an intelligent welfare assistance system using AI/ML concepts
- To improve accessibility through voice output and downloadable reports

---

## Tech Stack

- **Python** – Core programming language
- **Streamlit** – Interactive web application framework
- **JSON** – Dataset storage for government schemes
- **ReportLab** – PDF generation
- **gTTS** – Text-to-speech conversion

---

## Project Structure

```bash
adhikaar/
│
├── app.py            # Main application
├── preprocess.py     # Input preprocessing and structuring
├── logic.py          # Eligibility matching logic
├── schemes.json      # Government schemes dataset
└── README.md         # Project documentation
```

---

## Working Principle

The application works in the following steps:

1. **User Input Collection**  
   The user enters personal details in simple natural language.

2. **Input Preprocessing**  
   The entered text is cleaned, normalized, and converted into structured fields such as age, gender, income, marital status, occupation, and state.

3. **Eligibility Matching**  
   The structured profile is compared against predefined eligibility conditions stored in the scheme dataset.

4. **Scheme Recommendation**  
   Matching schemes are identified and ranked based on eligibility logic.

5. **Output Generation**  
   The final results are displayed clearly and can also be exported as PDF or converted to speech output.

---

## Installation and Setup

### Clone the Repository

```bash
git clone https://github.com/priyanga1811/adhikaar-scheme-eligiblity-engine.git
cd adhikaar-scheme-eligiblity-engine
```

### Install Dependencies

```bash
pip install reportlab
pip install gTTS
pip install -r requirements.txt
```

### Run the Application

```bash
streamlit run app.py
```

### Open in Browser

```bash
http://localhost:8501
```

---

## AI/ML Concepts Used

This project incorporates the following AI/ML-related concepts:

- **Natural Language Input Handling** – Accepting simple user-friendly textual input
- **Data Preprocessing** – Cleaning and structuring raw input data
- **Rule-Based Expert System** – Applying eligibility rules for decision-making
- **Recommendation Logic** – Suggesting schemes based on user profile matching
- **Explainable Output** – Providing understandable results to the user

Although the project does not rely on advanced machine learning models, it effectively demonstrates how AI-inspired logic can be applied to solve real-world problems.

---

## Applications

- Government welfare recommendation systems
- Citizen assistance platforms
- Social welfare and inclusion projects
- Rural and urban public service support systems
- Accessibility-focused digital assistance tools

---

## Future Enhancements

- Multilingual input support
- Addition of more central and state government schemes
- Location-based nearby service center recommendations
- ML-based personalized scheme ranking
- Integration with live government databases
- Chatbot-based interaction for better user experience

---

## Notes

- The eligibility engine is currently based on **rule-based logic**
- Scheme data is maintained in a **JSON file** for simplicity and flexibility
- The system can be further enhanced with machine learning models for better personalization and recommendation quality

---


## Conclusion

**Adhikaar – Scheme Eligibility Engine** is a practical and socially relevant AI/ML project that bridges the gap between citizens and government welfare schemes. By combining natural language input, structured preprocessing, rule-based eligibility matching, and accessibility features, the project presents an effective solution for simplifying public scheme discovery.
