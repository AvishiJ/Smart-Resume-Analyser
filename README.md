### Smart Resume Analyzer

The **Smart Resume Analyzer** is a Streamlit-based web application designed to analyze resumes and provide insights and recommendations based on the content. Here are its key features:
![full-page](https://github.com/user-attachments/assets/3ffc2419-69c6-49fe-9790-f2a1f0f1e098)

#### For Normal Users:
- **Resume Analysis**: Upload a PDF resume to extract and display basic information such as name, email, contact details, and estimated number of pages.
- **Skills Analysis**: Identify skills mentioned in the resume and recommend additional skills based on predefined categories like Data Science, Web Development, etc.
- **Job Field Prediction**: Predict the job field (e.g., Data Science, Web Development) based on the skills found in the resume.
- **Resume Writing Tips**: Provide tips and recommendations to improve the resume score based on the presence of essential sections like Objectives, Hobbies, Achievements, and Projects.
- **Course Recommendations**: Recommend relevant online courses and certificates based on the predicted job field.
- **Bonus Videos**: Offer randomly selected YouTube videos for resume writing and interview preparation tips.

![admin-fulll-page](https://github.com/user-attachments/assets/7b748b32-eb26-4f7a-8bf4-614fa2156a84)

#### For Admin Users:
- **Admin Panel**: Access an administrative interface with login credentials.
- **View User Data**: View and download user data including resume scores, predicted fields, and recommended skills and courses.
- **Data Visualization**: Generate interactive pie charts to visualize predicted job fields and user experience levels based on analyzed data.

### Technologies Used:
- **Python Libraries**: Streamlit, NLTK, spaCy, Pandas, Plotly, SQLite.
- **Data Extraction**: PDF parsing using pdfminer.
- **YouTube Integration**: Embed YouTube videos based on selected recommendations.
- **Database**: SQLite for storing user data and recommendations.
- **UI/UX**: Utilizes Streamlit for frontend development, providing an interactive and user-friendly interface.

This application serves as a practical tool for both job seekers and recruiters, offering actionable insights to enhance resume quality and job prospects based on current industry demands.
