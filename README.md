# 🤖 AI CV Reviewer

A multi-agent AI system that provides comprehensive CV analysis, feedback, and recommendations using Python, LangChain, LangGraph, and Streamlit with Anthropic's Claude.

## 🚀 Features

- **Multi-format Support**: Upload PDF, DOCX, or TXT files
- **Intelligent Data Extraction**: Automatically extract structured information from CVs
- **Comprehensive Analysis**: AI-powered analysis of experience, skills, and education
- **Constructive Feedback**: Detailed feedback on CV strengths and areas for improvement
- **Actionable Recommendations**: Specific suggestions for career development
- **Beautiful UI**: Modern, responsive Streamlit interface
- **Export Results**: Download comprehensive reports in JSON format

## 🏗️ Architecture

The application uses a multi-agent architecture with four specialized agents:

1. **Extraction Agent**: Extracts structured data from CV text
2. **Analysis Agent**: Analyzes CV content and provides insights
3. **Feedback Agent**: Generates constructive feedback
4. **Recommendation Agent**: Provides improvement suggestions and career guidance

### Workflow

```
CV Upload → Text Extraction → Data Analysis → Feedback Generation → Recommendations → Results
```

## 🛠️ Technology Stack

- **Python 3.8+**
- **Streamlit**: Web interface
- **LangChain**: LLM framework
- **LangGraph**: Multi-agent orchestration
- **Anthropic Claude**: AI language model
- **Pydantic v2**: Data validation and serialization
- **PyPDF2**: PDF processing
- **python-docx**: DOCX processing

## 📦 Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd cv-reviewer
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**:
   ```bash
   cp env.example .env
   ```
   
   Edit `.env` and add your Anthropic API key:
   ```
   ANTHROPIC_API_KEY=your_anthropic_api_key_here
   ```

## 🚀 Usage

1. **Start the application**:
   ```bash
   streamlit run main.py
   ```

2. **Open your browser** and navigate to `http://localhost:8501`

3. **Upload your CV** (PDF, DOCX, or TXT format)

4. **Click "Start CV Review"** to begin the analysis

5. **Review the results**:
   - Extracted information
   - Analysis results with scores
   - Detailed feedback
   - Improvement recommendations

6. **Download the full report** as JSON for further analysis

## 📁 Project Structure

```
cv-reviewer/
├── app/
│   ├── __init__.py
│   ├── main.py                 # Streamlit main app
│   ├── models.py               # Pydantic data models
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── extraction_agent.py # CV data extraction
│   │   ├── analysis_agent.py   # Data analysis
│   │   ├── feedback_agent.py   # Feedback generation
│   │   └── recommendation_agent.py # Improvement suggestions
│   ├── graph/
│   │   ├── __init__.py
│   │   └── workflow.py         # LangGraph workflow
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── file_processor.py   # File handling
│   │   └── llm_config.py       # LLM configuration
│   └── ui/
│       ├── __init__.py
│       └── components.py       # Streamlit UI components
├── requirements.txt
├── env.example
├── .gitignore
└── README.md
```

## 🔧 Configuration

### Environment Variables

- `ANTHROPIC_API_KEY`: Your Anthropic API key (required)


## 📊 Output Format

The application generates comprehensive reports including:

### Extracted Data
- Personal information (name, email, phone, location)
- Work experience with details
- Education background
- Skills with proficiency levels
- Certifications and languages

### Analysis Results
- Overall CV score (0-100)
- Strengths and weaknesses
- Experience analysis
- Skills analysis
- Education analysis
- Market alignment assessment

### Feedback
- General feedback
- Experience feedback
- Skills feedback
- Education feedback
- Presentation feedback
- Specific improvements
- Positive aspects

### Recommendations
- Skill development suggestions
- Experience gap identification
- Career path suggestions
- Immediate actions
- Long-term goals
- Industry trends

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License.

## 🆘 Support

If you encounter any issues:

1. Check that your Anthropic API key is correctly configured
2. Ensure your CV file is in a supported format
3. Verify the file size is within limits
4. Check the console for error messages

## 🔮 Future Enhancements

- Support for more file formats
- Integration with job boards
- Resume template suggestions
- ATS optimization scoring
- Multi-language support
- Batch processing capabilities
- Advanced analytics dashboard 
