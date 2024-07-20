import streamlit as st
import nltk
import spacy
import pandas as pd
import base64
import re
import time
from datetime import datetime
from pdfminer.high_level import extract_text
import os,random
import sqlite3
from PIL import Image
from sqlite3 import Error
from streamlit_tags import st_tags
from Courses import ds_course, web_course, android_course, ios_course, uiux_course, resume_videos, interview_videos
import pafy
import plotly.express as px
import youtube_dl

# Download necessary NLTK data
nltk.download('stopwords')
nltk.download('punkt')

# Load spaCy model
nlp = spacy.load('en_core_web_sm')

def fetch_yt_video(link):
    st.video(link)

def get_table_download_link(df, filename, text):
    """Generates a link allowing the data in a given panda dataframe to be downloaded
    in:  dataframe
    out: href string
    """
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()  # some strings <-> bytes conversions necessary here
    # href = f'<a href="data:file/csv;base64,{b64}">Download Report</a>'
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">{text}</a>'
    return href


# Function to create an SQLite database connection
def create_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)
    return conn

# Function to insert data into the database
def insert_data(conn, name, email, res_score, timestamp, no_of_pages, reco_field, cand_level, skills, recommended_skills, courses):
    DB_table_name = 'user_data'
    insert_sql = f"""
    INSERT INTO {DB_table_name} (
        Name, Email_ID, resume_score, Timestamp, Page_no, Predicted_Field, User_level, Actual_skills, Recommended_skills, Recommended_courses
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    rec_values = (
        name, email, str(res_score), timestamp, str(no_of_pages), reco_field, cand_level, skills, recommended_skills, courses
    )
    try:
        cursor = conn.cursor()
        cursor.execute(insert_sql, rec_values)
        conn.commit()
    except Error as e:
        print(e)


# Function to display PDF
def show_pdf(file_path):
    with open(file_path, "rb") as f:
        base64_pdf = base64.b64encode(f.read()).decode('utf-8')
    pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="700" height="1000" type="application/pdf"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)

# Function to extract information from resume
def extract_info(text):
    # Extract name (assuming the first two words are the name)
    name = ' '.join(text.split()[:2])
    
    # Extract email
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    email = re.findall(email_pattern, text)
    email = email[0] if email else "Not found"
    
    # Extract phone number (simple pattern, may need to be adjusted)
    phone_pattern = r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b'
    phone = re.findall(phone_pattern, text)
    phone = phone[0] if phone else "Not found"
    
    # Count pages (this is a rough estimate)
    pages = len(text) // 3000 + 1
    
    # Extract skills (you might want to expand this list)
    skills = ['python', 'java', 'c++', 'sql', 'javascript', 'html', 'css','c','matlab','r','numpy','pandas','scikit-learn','photoshop', 'illustrator', 'indesign', 
'premiere pro','after effects','wordpress','data mining', 'data analysis', 'machine learning','sphinx','latex','mathematics', 'team management'
'maple','git','cvs','htcondor','swift','objective-c','xcode','cccoa touch','sqlite','plist','nsuserdefaults','xml','json','rest','soap','interpersonal skills','communication skills', 'public speaking','german', 'leadership','analytical' ,'microsoft excel','power bi','deep learning','matplotlib'
    ]
    found_skills = [skill for skill in skills if skill in text.lower()]
    
    return {
        'name': name,
        'email': email,
        'mobile_number': phone,
        'no_of_pages': pages,
        'skills': found_skills
    }

def course_recommender(course_list):
    st.subheader("**Courses & Certificates🎓 Recommendations**")
    c = 0
    rec_course = []
    no_of_reco = st.slider('Choose Number of Course Recommendations:', 1, 10, 4)
    random.shuffle(course_list)
    for c_name, c_link in course_list:
        c += 1
        st.markdown(f"({c}) [{c_name}]({c_link})")
        rec_course.append(c_name)
        if c == no_of_reco:
            break
    return rec_course

# Main function to run the Streamlit app
def main():
    st.title("Smart Resume Analyser")
    st.sidebar.markdown("# Choose User")
    activities = ["Normal User", "Admin"]
    choice = st.sidebar.selectbox("Choose among the given options:", activities)
    
    img = Image.open('./Logo/resume1.jpg')
    img = img.resize((500, 250))
    st.image(img)

    # Initialize the database
    database = r"sra.db"
    conn = create_connection(database)

    #Creating the table with name as user_data
    if conn is not None:
        DB_table_name = 'user_data'
        create_table_sql = f"""
        CREATE TABLE IF NOT EXISTS {DB_table_name} (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            Name TEXT NOT NULL,
            Email_ID TEXT NOT NULL,
            resume_score TEXT NOT NULL,
            Timestamp TEXT NOT NULL,
            Page_no TEXT NOT NULL,
            Predicted_Field TEXT NOT NULL,
            User_level TEXT NOT NULL,
            Actual_skills TEXT NOT NULL,
            Recommended_skills TEXT NOT NULL,
            Recommended_courses TEXT NOT NULL
        );"""
        cursor = conn.cursor()
        cursor.execute(create_table_sql)    
    else:
        st.error("Error: Could not establish connection to database.")


    if choice == 'Normal User':
        pdf_file = st.file_uploader("Choose your Resume", type=["pdf"])
        if pdf_file is not None:
            save_image_path = './Uploaded_Resumes/' + pdf_file.name
            with open(save_image_path, "wb") as f:
                f.write(pdf_file.getbuffer())
            with st.expander("View Resume"):
                show_pdf(save_image_path)

            resume_text = extract_text(save_image_path)
            resume_data = extract_info(resume_text)

            if resume_data:
                st.header("**Resume Analysis**")
                st.success(f"Hello {resume_data['name']}")
                st.subheader("**Your Basic Info**")
                st.text(f"Name: {resume_data['name']}")
                st.text(f"Email: {resume_data['email']}")
                st.text(f"Contact: {resume_data['mobile_number']}")
                st.text(f"Resume pages: {resume_data['no_of_pages']}")

                cand_level = ''
                if resume_data['no_of_pages'] == 1:
                    cand_level = "Fresher"
                    st.markdown('''<h4 style='text-align: left; color: #d73b5c;'>You are looking Fresher.</h4>''', unsafe_allow_html=True)
                elif resume_data['no_of_pages'] == 2:
                    cand_level = "Intermediate"
                    st.markdown('''<h4 style='text-align: left; color: #1ed760;'>You are at intermediate level!</h4>''', unsafe_allow_html=True)
                elif resume_data['no_of_pages'] >= 3:
                    cand_level = "Experienced"
                    st.markdown('''<h4 style='text-align: left; color: #fba171;'>You are at experienced level!</h4>''', unsafe_allow_html=True)

                st.subheader("**Skills found in your resume**")
                st.write(", ".join(resume_data['skills']))

                st.subheader("**💡Skills Recommendation💡**")

                # Skill shows
                keywords = st_tags(label='### Skills that you have',
                                   text='See our skills recommendation',
                                   value=resume_data['skills'], key='1')

                # Skill keywords for different fields
                ds_keyword = ['tensorflow', 'keras', 'pytorch', 'machine learning', 'deep learning', 'flask', 'streamlit','Data Visualization', 'Predictive Analysis', 'Statistical Modeling',
                                              'data mining', 'data analytics', 'quantitative analysis', 'web scraping','keras','pytorch', 'probability', 'scikit-learn', 'tensorflow','analytical' ,'microsoft excel','power bi','matplotlib']
                web_keyword = ['react', 'django', 'node js', 'react js', 'php', 'laravel', 'magento', 'wordpress', 'javascript', 'angular js', 'c#', 'flask']
                android_keyword = ['android', 'android development', 'flutter', 'kotlin', 'xml', 'kivy','java','r','matlab','json']
                ios_keyword = ['ios', 'ios development', 'swift', 'cocoa','xcode','objective-c','cccoa touch','sqlite','plist','nsuserdefaults','xml','json','rest','soap']
                uiux_keyword = ['ux', 'adobe xd', 'figma', 'zeplin', 'balsamiq', 'ui', 'prototyping', 'wireframes', 'storyframes', 'adobe photoshop', 'photoshop', 'editing', 'adobe illustrator', 'illustrator', 'adobe after effects', 'after effects', 'adobe premier pro', 'premier pro', 'adobe indesign', 'indesign', 'wireframe', 'solid', 'grasp', 'user research', 'user experience','indesign','wordpress']

                # Initialize counters for each field
                skill_count = {
                    'Data Science': 0,
                    'Web Development': 0,
                    'Android Development': 0,
                    'IOS Development': 0,
                    'UI-UX Development': 0
                }

                # Calculate skill counts for each field
                for skill in resume_data['skills']:
                    if skill in ds_keyword:
                        skill_count['Data Science'] += 1
                    if skill in web_keyword:
                        skill_count['Web Development'] += 1
                    if skill in android_keyword:
                        skill_count['Android Development'] += 1
                    if skill in ios_keyword:
                        skill_count['IOS Development'] += 1
                    if skill in uiux_keyword:
                        skill_count['UI-UX Development'] += 1

                # Determine the field with the maximum matching skills
                predicted_field = max(skill_count, key=skill_count.get)
                recommended_skills = []
                # Show the predicted field only if it has more than 4 matching skills
                if skill_count[predicted_field] > 4:
                    st.success(f"** Our analysis says you are looking for {predicted_field} Jobs **")
                    
                    recommended_skills = []
                    if predicted_field == 'Data Science':
                        recommended_skills = list(set(ds_keyword) - set(resume_data['skills']))
                        recommended_courses = ds_course
                    elif predicted_field == 'Web Development':
                        recommended_skills = list(set(web_keyword) - set(resume_data['skills']))
                        recommended_courses = web_course
                    elif predicted_field == 'Android Development':
                        recommended_skills = list(set(android_keyword) - set(resume_data['skills']))
                        recommended_courses = android_course
                    elif predicted_field == 'IOS Development':
                        recommended_skills = list(set(ios_keyword) - set(resume_data['skills']))
                        recommended_courses = ios_course
                    elif predicted_field == 'UI-UX Development':
                        recommended_skills = list(set(uiux_keyword) - set(resume_data['skills']))
                        recommended_courses = uiux_course

                    # st.subheader("**Recommended skills for you**")
                    recommended_keywords = st_tags(label='### Recommended skills for you.',
                                                       text='generated from system',
                                                       value=recommended_skills, key='2')                   
                    course_recommender(recommended_courses)
                    
                else:
                    st.warning("No strong job field prediction can be made based on your skills. Please add more relevant skills to your resume.")

                ## Insert into table
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                ### Resume writing recommendation
                st.subheader("**Resume Tips & Ideas💡**")
                resume_score = 0
                if 'Objective' in resume_text:
                    resume_score = resume_score + 20
                    st.markdown(
                        '''<h4 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added Objective</h4>''',
                        unsafe_allow_html=True)
                else:
                    st.markdown(
                        '''<h4 style='text-align: left; color: #fabc10;'>[-] Recommendation:- Add your career objective, it will give your career intension to the Recruiters.</h4>''',
                        unsafe_allow_html=True)

                if 'Declaration' in resume_text:
                    resume_score = resume_score + 20
                    st.markdown(
                        '''<h4 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added Delcaration✍/h4>''',
                        unsafe_allow_html=True)
                else:
                    st.markdown(
                        '''<h4 style='text-align: left; color: #fabc10;'>[-] Recommendation:- Add Declaration✍. It will give the assurance that everything written on your resume is true and fully acknowledged by you</h4>''',
                        unsafe_allow_html=True)

                if 'Hobbies' or 'Interests' in resume_text:
                    resume_score = resume_score + 20
                    st.markdown(
                        '''<h4 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added your Hobbies⚽</h4>''',
                        unsafe_allow_html=True)
                else:
                    st.markdown(
                        '''<h4 style='text-align: left; color: #fabc10;'>[-] Recommendation :- Add Hobbies⚽. It will show your persnality to the Recruiters and give the assurance that you are fit for this role or not.</h4>''',
                        unsafe_allow_html=True)

                if 'Achievements' in resume_text:
                    resume_score = resume_score + 20
                    st.markdown(
                        '''<h4 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added your Achievements🏅 </h4>''',
                        unsafe_allow_html=True)
                else:
                    st.markdown(
                        '''<h4 style='text-align: left; color: #fabc10;'>[-] Recommendation:- Add Achievements🏅. It will show that you are capable for the required position.</h4>''',
                        unsafe_allow_html=True)

                if 'Projects' in resume_text:
                    resume_score = resume_score + 20
                    st.markdown(
                        '''<h4 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added your Projects👨‍💻 </h4>''',
                        unsafe_allow_html=True)
                else:
                    st.markdown(
                        '''<h4 style='text-align: left; color: #fabc10;'>[-] Recommendation:- Add Projects👨‍💻. It will show that you have done work related the required position or not.</h4>''',
                        unsafe_allow_html=True)

                st.subheader("**Resume Score📝**")
                st.markdown(
                    """
                    <style>
                        .stProgress > div > div > div > div {
                            background-color: #d73b5c;
                        }
                    </style>""",
                    unsafe_allow_html=True,
                )
                my_bar = st.progress(0)
                score = 0
                for percent_complete in range(resume_score):
                    score += 1
                    time.sleep(0.1)
                    my_bar.progress(percent_complete + 1)
                st.success('** Your Resume Writing Score: ' + str(score) + '**')
                st.warning(
                    "** Note: This score is calculated based on the content that you have added in your Resume. **")
                st.balloons()

                insert_data(conn,resume_data['name'], resume_data['email'], str(resume_score), timestamp,
                            str(resume_data['no_of_pages']), predicted_field, cand_level, str(resume_data['skills']),
                            str(recommended_skills), str(recommended_courses))
       
        #YOU TUBE VIDEOS RECOMMENDATIONS

                ## Resume writing video
                st.header("**Bonus Video for Resume Writing Tips💡**")
                resume_vid = random.choice(resume_videos)
                fetch_yt_video(resume_vid)

                ## Interview Preparation Video
                st.header("**Bonus Video for Interview👨‍💼 Tips💡**")
                interview_vid = random.choice(interview_videos)
                fetch_yt_video(interview_vid)

                conn.commit()
            else:
                st.error('Something went wrong..')   

    elif choice == "Admin":
        st.success("Welcome to Admin Panel")
        # Add admin functionality here
        ad_user = st.text_input("Username")
        ad_password = st.text_input("Password", type='password')
        if st.button('Login'):
            if ad_user == 'avishi' and ad_password == 'ml123':
                st.success("Welcome Avishi")
                # Display Data
                cursor.execute('''SELECT*FROM user_data''')
                data = cursor.fetchall()
                st.header("**User's👨‍💻 Data**")
                df = pd.DataFrame(data, columns=['ID', 'Name', 'Email', 'Resume Score', 'Timestamp', 'Total Page',
                                                 'Predicted Field', 'User Level', 'Actual Skills', 'Recommended Skills',
                                                 'Recommended Course'])
                st.dataframe(df)
                st.markdown(get_table_download_link(df, 'User_Data.csv', 'Download Report'), unsafe_allow_html=True)
                ## Admin Side Data
                query = 'select * from user_data;'
                plot_data = pd.read_sql(query, conn)

                ## Pie chart for predicted field recommendations
                # Prepare data for the pie chart
                predicted_field_data = plot_data['Predicted_Field'].value_counts().reset_index()
                predicted_field_data.columns = ['Predicted_Field', 'Count']

                # Pie chart for predicted field recommendations
                st.subheader("📈 **Pie-Chart for Predicted Field Recommendations**")
                fig = px.pie(predicted_field_data, values='Count', names='Predicted_Field', title='Predicted Field according to the Skills')
                st.plotly_chart(fig)

                # Prepare data for the user experience level pie chart
                user_level_data = plot_data['User_level'].value_counts().reset_index()
                user_level_data.columns = ['User_level', 'Count']

                # Pie chart for User's Experienced Level
                st.subheader("📈 ** Pie-Chart for User's👨‍💻 Experienced Level**")
                fig = px.pie(user_level_data, values='Count', names='User_level', title="Pie-Chart📈 for User's👨‍💻 Experienced Level")
                st.plotly_chart(fig)

            else:
                st.error("Wrong ID & Password Provided")

# Entry point of the Streamlit app
if __name__ == "__main__":
    main()