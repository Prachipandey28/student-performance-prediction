#  EduSense — Student Performance Intelligence System

EduSense is an **AI-powered Student Performance Analysis Dashboard** built using **Python, Streamlit, SQLite, Plotly, and Google Gemini AI**.

The system helps educational institutions and students **analyze academic performance, detect risk factors, generate personalized suggestions, and provide AI-powered academic guidance**.

EduSense evaluates **academic performance, lifestyle habits, and behavioural patterns** to generate insights that help students improve their performance.

---

#  Features

## Dashboard Analytics
- Real-time class statistics
- CGPA distribution visualization
- Screen time vs CGPA analysis
- Pass rate monitoring
- At-risk student detection

## Student Registration
- Add complete student academic and lifestyle data
- Automatic CGPA calculation
- Automatic grade generation
- Email confirmation after registration

## Student Lookup
- Search student by ID
- View full academic profile
- Download performance report

##  Student Suggestions
Provides **personalized improvement suggestions** based on:

- CGPA
- Attendance
- Screen time
- Study hours
- Stress level
- Sleep patterns
- Absences

##  Student Roadmap
- Step-by-step improvement flowchart
- Academic recovery plan
- Actionable suggestions for better performance

##  Class Insights
- Detect class-level trends
- Identify struggling students
- Discover key academic improvement areas

##  AI Chatbot (Gemini AI)
AI-powered academic advisor that helps with:

- Study strategies
- CGPA improvement
- Stress management
- Screen time control
- Time management
- Career guidance

The chatbot can **link to a specific student profile** and provide **personalized guidance**.

---

#  How the Prediction Works

The system calculates a **Final Performance Score** using multiple factors:

- Attendance
- Midterm scores
- Assignments
- Previous CGPA
- Study hours
- Screen time
- Sleep hours
- Stress level
- Absences
- Internet access
- Extra academic support

The score is then converted into:

- **CGPA**
- **Grade**
- **Pass/Fail status**
- **At-risk prediction**

---

#  Tech Stack

| Technology | Purpose |
|------------|---------|
| Python | Core programming |
| Streamlit | Interactive web dashboard |
| SQLite | Student data storage |
| Pandas | Data analysis |
| Plotly | Data visualization |
| Google Gemini AI | AI academic advisor |

---

# Project Structure

```
EduSense/
│
├── dashboard.py        # Main Streamlit dashboard
├── database.py         # SQLite database logic
├── main.py             # Application launcher
│
├── data/
│   └── students.db     # SQLite database
│
├── reports/            # Generated reports
├── exports/            # Exported files
│
├── requirements.txt
└── README.md
```

---

# Installation

Clone the repository:

```bash
git clone https://github.com/yourusername/edusense.git
cd edusense
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

# ▶️ Run the Application

Run using Python:

```bash
python main.py
```

Or directly run Streamlit:

```bash
streamlit run dashboard.py
```

Open the dashboard in your browser:

```
http://localhost:8501
```

---

# Gemini AI Setup (Optional)

To enable the **AI Chatbot**, add your Gemini API key.

Create the file:

```
.streamlit/secrets.toml
```

Add your key:

```
GEMINI_API_KEY="your_api_key_here"
```

---

# Example Use Cases

- Academic performance monitoring
- Early detection of struggling students
- Personalized study plans
- Student mental health indicators
- Academic counselling support

---

# Future Improvements

- Machine learning prediction models
- Student performance forecasting
- Multi-user login system
- Cloud deployment
- Admin analytics dashboard