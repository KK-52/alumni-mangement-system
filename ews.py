import streamlit as st
import pandas as pd
import datetime
import os
import time
import resume_analyzer
import requests

st.write("🔍 Debug Info:", st.session_state)  # Debugging step

def inject_custom_css():
    custom_css = """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600&display=swap');
    body {
        font-family: 'Poppins', sans-serif;
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        transition: background 0.5s ease;
    }
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 10px 20px;
        border-radius: 10px;
        transition: all 0.3s;
        border: none;
    }
    .stButton > button:hover {
        transform: scale(1.05);
        box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.2);
    }
    .dark-mode {
        background: #222;
        color: white;
    }
    .stTextInput input, .stSelectbox select {
        border-radius: 8px;
        padding: 8px;
        transition: all 0.3s;
    }
    .stTextInput input:focus, .stSelectbox select:focus {
        border-color: #764ba2;
        box-shadow: 0px 0px 8px rgba(118, 75, 162, 0.5);
    }
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)

# Function to toggle dark mode
def dark_mode_toggle():
    toggle_js = """
    <script>
    function toggleDarkMode() {
        let body = document.body;
        if (body.classList.contains('dark-mode')) {
            body.classList.remove('dark-mode');
        } else {
            body.classList.add('dark-mode');
        }
    }
    </script>
    <button onclick="toggleDarkMode()" style="position: fixed; top: 20px; right: 20px; padding: 8px 16px; background: #ff9f43; color: white; border: none; border-radius: 8px; cursor: pointer;">🌙 Toggle Dark Mode</button>
    """
    st.markdown(toggle_js, unsafe_allow_html=True)


inject_custom_css()
dark_mode_toggle()
def load_css(file_name):
    with open(file_name, "r") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Call the function to apply the styles
load_css("styles.css")
inject_custom_css()
dark_mode_toggle()




# File paths
ALUMNI_FILE = "alumni_data.csv"
MESSAGE_FILE = "messages.csv"
VACANCY_FILE = "vacancies.csv"
APPLICATIONS_FILE = "applications.csv"
EVENTS_FILE = "events.csv"
STUDENT_FILE = "students.csv"
STUDENT_MESSAGE_FILE = "student_messages.csv"
REPORTED_MESSAGES_FILE = "reported_messages.csv"
MEETINGS_FILE = "meetings.csv"
ALUMNI_POINTS_FILE = "alumni_points.csv"


# Load alumni database
if os.path.exists(ALUMNI_FILE):
    alumni_db = pd.read_csv(ALUMNI_FILE)
else:
    st.error("Database file not found!")
    alumni_db = pd.DataFrame()

# Load messages database
# Ensure messages.csv exists with the correct columns
if not os.path.exists(MESSAGE_FILE):
    pd.DataFrame(columns=["NAME", "BATCH", "DEPARTMENT", "EMAIL ID", "MESSAGE", "TIMESTAMP"]).to_csv(MESSAGE_FILE, index=False)

# Load messages database
def load_messages():
    return pd.read_csv(MESSAGE_FILE)

messages_db = load_messages()

if not os.path.exists(STUDENT_MESSAGE_FILE):
    pd.DataFrame(columns=["NAME", "BATCH", "DEPARTMENT", "EMAIL ID", "MESSAGE", "TIMESTAMP"]).to_csv(STUDENT_MESSAGE_FILE, index=False)

# Load student messages
def load_student_messages():
    return pd.read_csv(STUDENT_MESSAGE_FILE)

student_messages_db = load_student_messages()


# Load students database
if os.path.exists(STUDENT_FILE):
    student_db = pd.read_csv(STUDENT_FILE)
else:
    st.error("Student database file not found!")
    student_db = pd.DataFrame()

if not os.path.exists(REPORTED_MESSAGES_FILE):
    pd.DataFrame(columns=["REPORTER", "REPORTED_USER", "EMAIL ID", "MESSAGE", "TIMESTAMP", "REASON"]).to_csv(REPORTED_MESSAGES_FILE, index=False)

# Function to load reported messages
def load_reported_messages():
    return pd.read_csv(REPORTED_MESSAGES_FILE)

# Load the reported messages into a DataFrame
reported_messages_db = load_reported_messages()

# Ensure the meetings file exists
if not os.path.exists(MEETINGS_FILE):
    pd.DataFrame(columns=["STUDENT NAME", "BATCH", "DEPARTMENT", "EMAIL ID", "MESSAGE", "TIMESTAMP"]).to_csv(MEETINGS_FILE, index=False)
# Function to load meeting requests
def load_meetings():
    return pd.read_csv(MEETINGS_FILE)

meetings_db = load_meetings()

if not os.path.exists(ALUMNI_POINTS_FILE):
    columns = [
        "NAME", "EMAIL ID", "TOTAL POINTS", "HIRING IN SAME COMPANY",
        "HIRING IN ANOTHER COMPANY", "ADMISSION IN SAME INSTITUTION",
        "ADMISSION IN FOREIGN INSTITUTION", "CAREER GUIDANCE", 
        "MENTORSHIP", "VERIFIED"
    ]
    pd.DataFrame(columns=columns).to_csv(ALUMNI_POINTS_FILE, index=False)

# Load the file
points_db = pd.read_csv(ALUMNI_POINTS_FILE)


# Backend API URL
BACKEND_URL = "http://127.0.0.1:8000"


# Load vacancies database
if not os.path.exists(VACANCY_FILE):
    pd.DataFrame(columns=["COMPANY NAME", "QUALIFICATION", "SKILLSET", "ROLE", "NUMBER OF VACANCIES"]).to_csv(VACANCY_FILE, index=False)

# Ensure applications.csv exists
if not os.path.exists(APPLICATIONS_FILE):
    pd.DataFrame(columns=["COMPANY NAME", "QUALIFICATION", "SKILLSET", "ROLE", "NUMBER OF VACANCIES", "ATTACHED RESUME"]).to_csv(APPLICATIONS_FILE, index=False)

# Ensure events.csv exists
if not os.path.exists(EVENTS_FILE):
    pd.DataFrame(columns=["EVENT NAME", "EVENT DATE"]).to_csv(EVENTS_FILE, index=False)

def update_alumni_points(alumni_email, activity):
    # Load existing points database
    points_file = "alumni_points.csv"
    
    if os.path.exists(points_file):
        points_db = pd.read_csv(points_file)
    else:
        points_db = pd.DataFrame(columns=["NAME", "EMAIL ID", "TOTAL POINTS", 
                                          "HIRING IN SAME COMPANY", "HIRING IN ANOTHER COMPANY",
                                          "ADMISSION IN SAME INSTITUTION", "ADMISSION IN FOREIGN INSTITUTION",
                                          "CAREER GUIDANCE", "MENTORSHIP","VERIFIED"])

    # Define points for each activity
    points_dict = {
        "Hired a Student (Same Company)": 5,
        "Hired a Student (Another Company)": 7,
        "Secured Admission (Same Institution)": 5,
        "Secured Admission (Foreign Country)": 6,
        "Gave Career Guidance": 5,
        "Mentored a Student": 6
    }

    # Check if the alumni already has an entry
    if alumni_email in points_db["EMAIL ID"].values:
        alumni_index = points_db[points_db["EMAIL ID"] == alumni_email].index[0]
        points_db.at[alumni_index, "TOTAL POINTS"] += points_dict[activity]
        points_db.at[alumni_index, activity.replace(" ", "_").upper()] += 1
    else:
        # Get alumni name from alumni_db
        alumni_name = alumni_db[alumni_db["EMAIL ID"] == alumni_email]["NAME"].values[0]
        new_entry = [alumni_name, alumni_email, points_dict[activity], 
                     1 if activity == "Hired a Student (Same Company)" else 0,
                     1 if activity == "Hired a Student (Another Company)" else 0,
                     1 if activity == "Secured Admission (Same Institution)" else 0,
                     1 if activity == "Secured Admission (Foreign Country)" else 0,
                     1 if activity == "Gave Career Guidance" else 0,
                     1 if activity == "Mentored a Student" else 0]
        points_db.loc[len(points_db)] = new_entry

    # Save back to CSV
    points_db.to_csv(points_file, index=False)

# Ensure email and user session state exist
if "email" not in st.session_state:
    st.session_state["email"] = None  # Default value is None

if "user" not in st.session_state:
    st.session_state["user"] = None  # Default value is None



# Function to check login credentials
def authenticate_user(email, user_type):
    if user_type == "Alumni" and email in alumni_db["EMAIL ID"].values:
        return "Alumni"
    elif user_type == "Admin":  # Any email can log in as Admin
        return "Admin"
    elif user_type == "Student" and email in student_db["email id"].values:
        return "Student"
    return None

# Sidebar for login/signup
st.sidebar.title("")
st.title("AI Powered Smart Alumni & Career Management System")
st.title("Powered by LIGHTBUZZ ")
user_type = st.sidebar.radio("Login as:", ("Alumni", "Admin","Student"))
email = st.sidebar.text_input("Email ID")
password = st.sidebar.text_input("Password", type="password") 

if st.sidebar.button("Login"):
    if password:
        user_role = authenticate_user(email, user_type)
        if user_role:
            st.session_state["email"] = email.strip()  # ✅ Ensure email is stored
            st.session_state["user"] = email.split("@")[0]  
            st.session_state["role"] = user_role
            st.session_state["logged_in"] = True
            st.rerun()
        else:
            st.sidebar.error("Invalid credentials!")
    else:
        st.sidebar.error("⚠ Please enter a password!")








# If user is logged in, show dashboard
if st.session_state.get("logged_in"):
    if st.session_state["role"] == "Alumni":
        st.title("🎓 Alumni Dashboard")
        menu = ["College Details", "Update Profile", "Chat with College","Chat with Students", "Search Friends","Student Analysis", "View Events", "Hire Students","Received Applications","Resume Analysis","Alumni Contributions","Leaderboard"]
        choice = st.selectbox("Navigate", menu)
        # Fetch alumni details
        user_data = alumni_db[alumni_db["EMAIL ID"] == email].iloc[0]

        # Check for birthday message
        today = datetime.date.today().strftime("%Y-%m-%d")
        birthday_msg = None
        if user_data["DATE OF BIRTH"] == today:
            birthday_msg = f"🎉 Happy Birthday, {user_data['NAME']}! Wishing you success and happiness on your special day."

        if choice == "College Details":
            st.write("### 🏛 College Information")
            st.write("NIRF Rating: 25\nNAAC Accreditation: A++\nPlacement Rate: 85%")

        elif choice == "Update Profile":
            st.write("### ✏ Update Your Profile")
            country = st.text_input("Country of Residence", user_data["COUNTRY OF RESIDENCE"])
            company = st.text_input("Company Name", user_data["COMPANY NAME"])
            job = st.text_input("Designation", user_data["JOB TITLE"])

            if st.button("Update Profile"):
                old_company = user_data["COMPANY NAME"]
                old_job = user_data["JOB TITLE"]

                # Update CSV
                alumni_db.loc[alumni_db["EMAIL ID"] == email, ["COUNTRY OF RESIDENCE", "COMPANY NAME", "JOB TITLE"]] = [country, company, job]
                alumni_db.to_csv(ALUMNI_FILE, index=False)

                # Check for job change and send congrats message
                if old_company != company or old_job != job:
                    job_msg = f"🎉 Congratulations, {user_data['NAME']}, on your new role at {company}! Wishing you success."
                    new_message = pd.DataFrame([[user_data["NAME"], user_data["BATCH"], user_data["DEPARTMENT"], email, job_msg, datetime.datetime.now()]], columns=messages_db.columns)
                    new_message.to_csv(MESSAGE_FILE, mode="a", header=False, index=False)

                st.success("✅ Profile Updated!")

        elif choice == "Chat with College":
            st.write("### 💬 Chat with College Admin")
            if birthday_msg:
                st.success(birthday_msg)

            user_messages = messages_db[messages_db["EMAIL ID"] == email]
            for _, msg in user_messages.iterrows():
                st.write(f"💬 {msg['MESSAGE']}")

            chat_message = st.text_area("Type your message...")
            if st.button("Send Message"):
                new_message = pd.DataFrame([[user_data["NAME"], user_data["BATCH"], user_data["DEPARTMENT"], email, chat_message, datetime.datetime.now()]], columns=messages_db.columns)
                new_message.to_csv(MESSAGE_FILE, mode="a", header=False, index=False)
                st.success("✅ Message Sent!")


        elif choice == "Chat with Students":
            st.write("### 💬 Chat with Students")

            student_list = student_messages_db["EMAIL ID"].unique()
            selected_student = st.selectbox("Choose Student", student_list)

            user_messages = student_messages_db[
                (student_messages_db["EMAIL ID"] == selected_student) |
                (student_messages_db["EMAIL ID"] == st.session_state["user"])
            ]

            for _, msg in user_messages.iterrows():
                st.write(f"💬 {msg['NAME']} ({msg['EMAIL ID']}): {msg['MESSAGE']}")
                # Report button for each message
                if st.button(f"🚨 Report", key=f"report_{msg['TIMESTAMP']}"):
                    report_reason = st.text_area(f"Reason for reporting message from {msg['EMAIL ID']}:", key=f"reason_{msg['TIMESTAMP']}")
                    if st.button(f"Submit Report", key=f"submit_{msg['TIMESTAMP']}"):
                        new_report = pd.DataFrame([[st.session_state["user"], msg["NAME"], msg["EMAIL ID"], msg["MESSAGE"], msg["TIMESTAMP"], report_reason]],
                                                  columns=["REPORTER", "REPORTED_USER", "EMAIL ID", "MESSAGE", "TIMESTAMP", "REASON"])
                        new_report.to_csv(REPORTED_MESSAGES_FILE, mode="a", header=False, index=False)
                        st.warning("⚠️ Message reported successfully! Admin will review it.")

            chat_message = st.text_area("Type your message...")

            if st.button("Reply to Student"):
                new_message = pd.DataFrame([[st.session_state["user"], "", "", st.session_state["user"], chat_message, datetime.datetime.now()]], 
                                           columns=["NAME", "BATCH", "DEPARTMENT", "EMAIL ID", "MESSAGE", "TIMESTAMP"])
                new_message.to_csv(STUDENT_MESSAGE_FILE, mode="a", header=False, index=False)
                st.success("✅ Reply Sent!")


        elif choice == "Hire Students":
            st.subheader("📢 Post Job Vacancies")
            company = st.text_input("Company Name")
            qualification = st.text_input("Qualification Required")
            skillset = st.text_area("Desired Skillset")
            role = st.text_input("Job Role")
            vacancies = st.number_input("Number of Vacancies", min_value=1, step=1)

            if st.button("Submit Hiring Request"):
                new_vacancy = pd.DataFrame([[company, qualification, skillset, role, vacancies]], 
                               columns=["COMPANY NAME", "QUALIFICATION", "SKILLSET", "ROLE", "NUMBER OF VACANCIES"])
                new_vacancy.to_csv(VACANCY_FILE, mode="a", header=False, index=False)
                st.success("✅ Hiring request submitted successfully!")

            # Claim Points for Hiring Students
            if st.button("🏆 Claim Points"):
                if "email" not in st.session_state or not st.session_state["email"]:  
                    st.error("⚠ Please log in before claiming points.")
                else:
                    st.write("🏆 Select the type of contribution:")
                    contribution_type = st.radio(
                        "Select your contribution",
                        [
                            "Hired Student in My Company (5 Points)",
                            "Hired Student in Another Company (7 Points)",
                            "Secured Admission in My Institution (5 Points)",
                            "Secured Admission in Foreign Institution (6 Points)",
                            "Career Guidance Session (5 Points)",
                            "Mentorship for Placement/Higher Studies (6 Points)"
                        ]
                    )

        # Assign points based on selection
                    points_mapping = {
                        "Hired Student in My Company (5 Points)": ("HIRING IN SAME COMPANY", 5),
                        "Hired Student in Another Company (7 Points)": ("HIRING IN ANOTHER COMPANY", 7),
                        "Secured Admission in My Institution (5 Points)": ("ADMISSION IN SAME INSTITUTION", 5),
                        "Secured Admission in Foreign Institution (6 Points)": ("ADMISSION IN FOREIGN INSTITUTION", 6),
                        "Career Guidance Session (5 Points)": ("CAREER GUIDANCE", 5),
                        "Mentorship for Placement/Higher Studies (6 Points)": ("MENTORSHIP", 6),
                    }

                    column_name, points = points_mapping[contribution_type]

        # Create a new entry for admin verification
                    new_entry = pd.DataFrame(
                        [[
                            st.session_state["user"], st.session_state["email"], 0, 0, 0, 0, 0, 0, 0, "No"
                        ]],
                        columns=points_db.columns
                    )

        # Set the respective contribution column
                    new_entry[column_name] = points

        # Append to CSV
                    new_entry.to_csv(ALUMNI_POINTS_FILE, mode="a", header=False, index=False)
                    st.success("✅ Points claim sent for admin approval!")


        elif choice == "Resume Analysis":
            st.subheader("📄 AI-Powered Resume Analysis")

    # **1️⃣ Upload Resumes**
            st.header("📤 Upload Resumes")
            uploaded_files = st.file_uploader("Upload multiple resumes (PDFs)", type=["pdf"], accept_multiple_files=True)

            if st.button("Upload Resumes"):
                if uploaded_files:
                    files = [("files", (file.name, file.getvalue(), "application/pdf")) for file in uploaded_files]
                    response = requests.post(f"{BACKEND_URL}/upload_resumes/", files=files)
                    st.success(response.json().get("message", "Error uploading resumes"))
                else:
                    st.warning("Please upload at least one resume.")

            # **2️⃣ Add Job Requirement**
            st.header("📝 Add Job Requirement")
            req_name = st.text_input("Requirement Name")
            req_description = st.text_area("Describe the job requirement")

            if st.button("Add Requirement"):
                if req_name and req_description:
                    data = {"requirement_name": req_name, "description": req_description}
                    response = requests.post(f"{BACKEND_URL}/add_requirement/", data=data)
                    st.success(response.json().get("message", "Error adding requirement"))
                else:
                    st.warning("Please provide a requirement name and description.")

            # **3️⃣ Recommend Candidates**
            st.header("🔍 Recommend Candidates")
            req_match = st.text_input("Enter the Requirement Name to Match Resumes")

            if st.button("Find Matches"):
                if req_match:
                    data = {"requirement_name": req_match}
                    response = requests.post(f"{BACKEND_URL}/recommend/", data=data)
                    result = response.json()

                    if "error" in result:
                        st.error(result["error"])
                    else:
                        st.subheader("🏆 Top Recommended Candidates")
                        for candidate in result["top_candidates"]:
                            st.write(f"**Rank {candidate['rank']}: {candidate['resume']}**")
                            st.write(f"📊 Similarity Score: {candidate['similarity_score']:.2f}")
                            st.write(f"💡 {candidate['message']}")

                            # **Display Summary**
                            summary = candidate["summary"]
                            st.write("📌 **Top Skills:**", ", ".join(summary["top_skills"]))
                            
                            st.write("🔹 **Experience Highlights:**")
                            for exp in summary["experience_highlights"]:
                                st.write(f"- {exp}")

                            st.write("---")
                else:
                    st.warning("Please enter a requirement name.")

        elif choice == "Received Applications":
            st.subheader("📥 Resumes Received for Hiring")

            if os.path.exists(APPLICATIONS_FILE):
                applications_db = pd.read_csv(APPLICATIONS_FILE)

                if not applications_db.empty:
                    st.write("### 📑 List of Received Resumes")
                    for index, row in applications_db.iterrows():
                        st.write(f"📌 **Company:** {row['COMPANY NAME']}")
                        st.write(f"💼 **Role:** {row['ROLE']}")

                # Check if resume file exists before showing the download button
                        resume_path = row['ATTACHED RESUME']
                        if os.path.exists(resume_path):
                            with open(resume_path, "rb") as file:
                                resume_bytes = file.read()

                            st.download_button(
                                label="📄 Download Resume",
                                data=resume_bytes,
                                file_name=os.path.basename(resume_path),
                                mime="application/pdf"
                            )
                        else:
                            st.warning("⚠ Resume file not found!")

                        st.write("---")
                else:
                    st.info("No resumes received yet.")
            else:
                st.info("No resumes received yet.")


        
        elif choice == "View Events":
            st.subheader("📆 Upcoming Events")
    
    # Load events
            if os.path.exists(EVENTS_FILE):
                events_db = pd.read_csv(EVENTS_FILE)
                if not events_db.empty:
                    for index, row in events_db.iterrows():
                        st.write(f"📌 **{row['EVENT NAME']}** - 📅 {row['EVENT DATE']}")
                
                        if st.button(f"Register for {row['EVENT NAME']}", key=index):
                    # Send confirmation message
                           registration_msg = f"✅ You have successfully registered for '{row['EVENT NAME']}' on {row['EVENT DATE']}!"
                    
                    # Save the message to the chat database
                           new_message = pd.DataFrame([[user_data["NAME"], user_data["BATCH"], user_data["DEPARTMENT"], email, registration_msg, datetime.datetime.now()]], 
                                               columns=messages_db.columns)
                           new_message.to_csv(MESSAGE_FILE, mode="a", header=False, index=False)
                    
                           st.success(f"✅ Registered for '{row['EVENT NAME']}' successfully!")
                else:
                    st.warning("⚠ No upcoming events at the moment.")
            else:
                st.warning("⚠ No upcoming events at the moment.")

        elif choice == "Search Friends":
            st.subheader("🔍 Search Friends")
    
            # Load Alumni Data
            alumni_db = pd.read_csv(ALUMNI_FILE)
    
            # Search Input
            search_query = st.text_input("Enter Name, Batch, Department, or Company")
    
            # Filter Results
            if search_query:
                filtered_alumni = alumni_db[
                    alumni_db.apply(lambda row: search_query.lower() in row.astype(str).str.lower().to_list(), axis=1)
                ]
                if not filtered_alumni.empty:
                    st.write("### 🎓 Search Results")
                    st.dataframe(filtered_alumni)

                    # Resume Attachment Feature
                    selected_index = st.selectbox("Select an Alumni", filtered_alumni.index, format_func=lambda x: f"{filtered_alumni.loc[x, 'NAME']} - {filtered_alumni.loc[x, 'COMPANY NAME']}")
            
                    if st.button("Attach Resume & Respond"):
                        resume_file = st.file_uploader("Upload Resume (PDF)", type=["pdf"])
                        if resume_file:
                            save_path = f"resumes/{resume_file.name}"
                            with open(save_path, "wb") as f:
                                f.write(resume_file.getbuffer())

                            alumni_db.loc[selected_index, "ATTACHED RESUME"] = save_path
                            alumni_db.to_csv(APPLICATIONS_FILE, mode="a", header=False, index=False)
                            st.success("✅ Resume attached and sent to alumni!")

                else:
                    st.warning("⚠ No matching alumni found.")
            else:
                st.info("🔹 Type a keyword to search alumni.")

            # Power BI Report Embed
            st.write("### 📊 Alumni Insights - Power BI Dashboard")
    
            # Replace <EMBED_URL> with the actual Power BI embed link
            POWER_BI_EMBED_URL = "https://app.powerbi.com/reportEmbed?reportId=2c79391e-8a8b-42fd-9519-df8599b4d468&autoAuth=true&ctid=085c606c-851a-4f29-9538-639c1a6f40ee"
    
            st.components.v1.iframe(POWER_BI_EMBED_URL, width=850, height=450)



        elif choice == "Student Analysis":
           st.subheader("📊 Student Analysis - Power BI")
           # Power BI Embedded Report Link for Alumni
           STUDENT_ANALYSIS_POWER_BI_URL = "https://app.powerbi.com/reportEmbed?reportId=9ca7b9f1-281f-431e-8fa5-2286c32bd3c6&autoAuth=true&ctid=085c606c-851a-4f29-9538-639c1a6f40ee"
           # Embed Power BI dashboard using iframe
           st.components.v1.iframe(STUDENT_ANALYSIS_POWER_BI_URL, width=850, height=450)
           st.info("🔹 This dashboard provides insights into student profiles for hiring, higher education mentorship, and career guidance.")


        elif choice == "Alumni Contributions":
            st.write("### 🎯 Alumni Contributions")
    
            activity = st.selectbox("Select Activity", ["Hired a Student (Same Company)", 
                                                "Hired a Student (Another Company)", 
                                                "Secured Admission (Same Institution)", 
                                                "Secured Admission (Foreign Country)",
                                                "Gave Career Guidance",
                                                "Mentored a Student"])
            if st.button("Submit Contribution"):
                # Update points in alumni_points.csv
                update_alumni_points(st.session_state["user"], activity)
                st.success("✅ Contribution recorded and points awarded!")
        
        elif choice == "Leaderboard":
            st.write("### 🏆 Alumni Leaderboard")
            if os.path.exists(ALUMNI_POINTS_FILE):
                leaderboard_db = pd.read_csv(ALUMNI_POINTS_FILE)
                leaderboard_db = leaderboard_db[leaderboard_db["VERIFIED"] == "Yes"]
                leaderboard_db = leaderboard_db[["NAME", "EMAIL ID", "TOTAL POINTS"]].sort_values(by="TOTAL POINTS", ascending=False)

                st.table(leaderboard_db)
            else:
                 st.warning("⚠ No verified contributions yet.")
            




        

    elif st.session_state["role"] == "Admin":
        st.title("🛠 Admin Dashboard")
        menu = ["View Alumni Messages", "Update Events","Update Meetings","Chat with Alumni","Chat with Students", "Search Alumni","Search Students Analysis", "View Vacancies","Vacancy Dashboard","View Reported Messages","Manage Alumni Contributions"]
        choice = st.selectbox("Navigate", menu)

        if choice == "View Alumni Messages":
            st.write("### 📩 Messages from Alumni")
            for _, msg in messages_db.iterrows():
                st.write(f"📩 {msg['NAME']} (Batch {msg['BATCH']}, {msg['DEPARTMENT']}):")
                st.write(f"💬 {msg['MESSAGE']}")
                st.write("---")

        elif choice == "Update Events":
            st.write("### 📅 Manage Events")
            event = st.text_input("Event Name")
            date = st.date_input("Event Date")
            if st.button("Add Event"):
                new_event = pd.DataFrame([[event, date]], columns=["EVENT NAME", "EVENT DATE"])
                new_event.to_csv(EVENTS_FILE, mode="a", header=False, index=False)
                st.success(f"✅ Event '{event}' added for {date}!")
        
        elif choice == "Update Meetings":
           st.write("### 📅 Manage Career Guidance Meetings")

           meeting_topic = st.text_input("Meeting Topic")
           meeting_date = st.date_input("Meeting Date")
           meeting_time = st.time_input("Meeting Time")
           meeting_link = st.text_input("Meeting Link (Google Meet/Zoom, etc.)")

           if st.button("Add Meeting"):
                new_meeting = pd.DataFrame([[meeting_topic, meeting_date, meeting_time, meeting_link]], 
                                           columns=["MEETING TOPIC", "MEETING DATE", "MEETING TIME", "MEETING LINK"])
                new_meeting.to_csv(MEETINGS_FILE, mode="a", header=False, index=False)
                st.success(f"✅ Meeting '{meeting_topic}' added for {meeting_date} at {meeting_time}!")


        elif choice == "Chat with Alumni":
            st.write("### 💬 Chat with Alumni")
            alumni_email = st.selectbox("Select Alumni", alumni_db["EMAIL ID"].unique())
            chat_message = st.text_area("Admin Message")
            if st.button("Send Message"):
                alum_data = alumni_db[alumni_db["EMAIL ID"] == alumni_email].iloc[0]
                admin_msg = f"📢 College Admin: {chat_message}"
                new_message = pd.DataFrame([[alum_data["NAME"], alum_data["BATCH"], alum_data["DEPARTMENT"], alumni_email, admin_msg, datetime.datetime.now()]], columns=messages_db.columns)
                new_message.to_csv(MESSAGE_FILE, mode="a", header=False, index=False)
                st.success("✅ Message Sent to Alumni!")

        elif choice == "Chat with Students":
            st.write("### 💬 Chat with Students")

            student_list = student_messages_db["EMAIL ID"].unique()
            selected_student = st.selectbox("Choose Student", student_list)

            user_messages = student_messages_db[
                (student_messages_db["EMAIL ID"] == selected_student) |
                (student_messages_db["EMAIL ID"] == "Admin")
            ]

            for _, msg in user_messages.iterrows():
                st.write(f"💬 {msg['NAME']} ({msg['EMAIL ID']}): {msg['MESSAGE']}")

            chat_message = st.text_area("Type your message...")

            if st.button("Reply to Student"):
                new_message = pd.DataFrame([[st.session_state["user"], "", "", "Admin", chat_message, datetime.datetime.now()]], 
                                           columns=["NAME", "BATCH", "DEPARTMENT", "EMAIL ID", "MESSAGE", "TIMESTAMP"])
                new_message.to_csv(STUDENT_MESSAGE_FILE, mode="a", header=False, index=False)
                st.success("✅ Reply Sent!")
            

                
        elif choice == "View Vacancies":
            st.subheader("📋 Job Vacancies")

            vacancies_db = pd.read_csv(VACANCY_FILE)

            if not vacancies_db.empty:
                st.write("### 🔍 Job Openings Submitted by Alumni")
                selected_index = st.selectbox(
                    "Select a Vacancy", 
                    vacancies_db.index, 
                    format_func=lambda x: f"{vacancies_db.loc[x, 'COMPANY NAME']} - {vacancies_db.loc[x, 'ROLE']}"
                )

        # File uploader should be outside the button condition
                resume_file = st.file_uploader("Upload Resume (PDF)", type=["pdf"])

                if resume_file and st.button("Attach Resume & Respond"):
                    try:
                # Ensure the "resumes" directory exists
                        os.makedirs("resumes", exist_ok=True)

                # Save the uploaded PDF resume
                        save_path = f"resumes/{resume_file.name}"
                        with open(save_path, "wb") as f:
                            f.write(resume_file.getbuffer())

                # Load applications.csv, or create if it doesn’t exist
                        if os.path.exists(APPLICATIONS_FILE):
                            applications_db = pd.read_csv(APPLICATIONS_FILE)
                        else:
                            applications_db = pd.DataFrame(columns=vacancies_db.columns.tolist() + ["ATTACHED RESUME"])

                # Get selected vacancy details and update resume column
                        vacancy_data = vacancies_db.loc[[selected_index]].copy()
                        vacancy_data["ATTACHED RESUME"] = save_path

                # Concatenate to add new row
                        applications_db = pd.concat([applications_db, vacancy_data], ignore_index=True)

                # Save back to CSV
                        applications_db.to_csv(APPLICATIONS_FILE, index=False)

                        st.success("✅ Resume attached and saved successfully!")
                    except Exception as e:
                        st.error(f"❌ Error saving resume: {str(e)}")

        
        elif choice == "Search Alumni":
            st.subheader("🔍 Search Alumni")
    
            # Load Alumni Data
            alumni_db = pd.read_csv(ALUMNI_FILE)
    
            # Search Input
            search_query = st.text_input("Enter Name, Batch, Department, or Company")
    
            # Filter Results
            if search_query:
                filtered_alumni = alumni_db[
                    alumni_db.apply(lambda row: search_query.lower() in row.astype(str).str.lower().to_list(), axis=1)
                ]
                if not filtered_alumni.empty:
                    st.write("### 🎓 Search Results")
                    st.dataframe(filtered_alumni)

                    # Resume Attachment Feature
                    selected_index = st.selectbox("Select an Alumni", filtered_alumni.index, format_func=lambda x: f"{filtered_alumni.loc[x, 'NAME']} - {filtered_alumni.loc[x, 'COMPANY NAME']}")
            
                    if st.button("Attach Resume & Respond"):
                        resume_file = st.file_uploader("Upload Resume (PDF)", type=["pdf"])
                        if resume_file:
                            save_path = f"resumes/{resume_file.name}"
                            with open(save_path, "wb") as f:
                                f.write(resume_file.getbuffer())

                            alumni_db.loc[selected_index, "ATTACHED RESUME"] = save_path
                            alumni_db.to_csv(APPLICATIONS_FILE, mode="a", header=False, index=False)
                            st.success("✅ Resume attached and sent to alumni!")

                else:
                    st.warning("⚠ No matching alumni found.")
            else:
                st.info("🔹 Type a keyword to search alumni.")

            # Power BI Report Embed
            st.write("### 📊 Alumni Insights - Power BI Dashboard")
    
            # Replace <EMBED_URL> with the actual Power BI embed link
            POWER_BI_EMBED_URL = "https://app.powerbi.com/reportEmbed?reportId=69f327b5-00f2-44b0-946e-e9052c45607b&autoAuth=true&ctid=085c606c-851a-4f29-9538-639c1a6f40ee"
    
            st.components.v1.iframe(POWER_BI_EMBED_URL, width=850, height=450)


        elif choice == "Search Students Analysis":
            st.subheader("📊 Search Students Analysis - Power BI")

            # Power BI Embedded Report Link for Admin
            SEARCH_STUDENTS_POWER_BI_URL = "https://app.powerbi.com/reportEmbed?reportId=9ca7b9f1-281f-431e-8fa5-2286c32bd3c6&autoAuth=true&ctid=085c606c-851a-4f29-9538-639c1a6f40ee"

            # Embed Power BI dashboard using iframe
            st.components.v1.iframe(SEARCH_STUDENTS_POWER_BI_URL, width=850, height=450)

            st.info("🔹 This dashboard provides insights into student career progress, placements, and educational trends for administrative tracking.")


        elif choice == "View Reported Messages":
           st.write("### 🚨 Reported Messages")

           reported_messages_db = pd.read_csv(REPORTED_MESSAGES_FILE)
    
           if reported_messages_db.empty:
               st.info("✅ No reported messages.")
           else:
                for _, report in reported_messages_db.iterrows():
                    st.write(f"**📩 Message:** {report['MESSAGE']}")
                    st.write(f"👤 Reported User: {report['REPORTED_USER']} ({report['EMAIL ID']})")
                    st.write(f"📌 Reported by: {report['REPORTER']}")
                    st.write(f"📝 Reason: {report['REASON']}")
                    st.write("---")


        elif choice == "Vacancy Dashboard":
            st.subheader("📊 Vacancy Dashboard - Power BI")

    # Power BI Embedded Report Link
            VACANCY_POWER_BI_URL = "https://app.powerbi.com/reportEmbed?reportId=9f162f17-971e-4eff-b714-ea84b23db6f2&autoAuth=true&ctid=085c606c-851a-4f29-9538-639c1a6f40ee"

    # Embed Power BI dashboard using iframe
            st.components.v1.iframe(VACANCY_POWER_BI_URL, width=1000, height=600)

            st.info("🔹 This dashboard provides insights into job vacancies, applications, and hiring trends.")


        elif choice == "Manage Alumni Contributions":
            st.write("### 🎖 Manage Alumni Contributions")

            if os.path.exists(ALUMNI_POINTS_FILE):
                points_db = pd.read_csv(ALUMNI_POINTS_FILE)
        
                pending_contributions = points_db[points_db["VERIFIED"] == "No"]

                if not pending_contributions.empty:
                    for index, row in pending_contributions.iterrows():
                        st.write(f"👤 **{row['NAME']}** ({row['EMAIL ID']}) requested verification for:")
                        for col in ["HIRING IN SAME COMPANY", "HIRING IN ANOTHER COMPANY", "ADMISSION IN SAME INSTITUTION", 
                                    "ADMISSION IN FOREIGN INSTITUTION", "CAREER GUIDANCE", "MENTORSHIP"]:
                            if row[col] > 0:
                                st.write(f"- {col.replace('_', ' ')}: {row[col]} points")
            
                        if st.button(f"✅ Approve {row['NAME']}", key=index):
                            points_db.at[index, "TOTAL POINTS"] += sum(row[3:9])  # Add points to total
                            points_db.at[index, "VERIFIED"] = "Yes"
                            points_db.to_csv(ALUMNI_POINTS_FILE, index=False)
                            st.success(f"✅ Approved points for {row['NAME']}!")
                            st.rerun()
                else:
                     st.info("No pending contributions for approval.")
            else:
                 st.warning("⚠ No alumni contributions found.")

                    








    elif st.session_state["role"] == "Student":
        st.title("🎓 Student Dashboard")
        menu = ["Career Guidance","Chat with Admin/Alumni", "Search Alumni Analysis", "Student Details"]
        choice = st.selectbox("Navigate", menu)

        if choice == "Career Guidance":
            st.subheader("📆 Upcoming Career Guidance Meetings")

            if os.path.exists(MEETINGS_FILE):
                meetings_db = load_meetings()  # Load the meetings data
                if not meetings_db.empty:
                    for index, row in meetings_db.iterrows():
                        st.write(f"🎓 **{row['MEETING TOPIC']}** - 📅 {row['MEETING DATE']} at ⏰ {row['MEETING TIME']}")
                        st.write(f"🔗 [Join Meeting]({row['MEETING LINK']})")

                        if st.button(f"Register for {row['MEETING TOPIC']}", key=f"register_{index}"):
                            registration_msg = f"✅ You have successfully registered for '{row['MEETING TOPIC']}' on {row['MEETING DATE']} at {row['MEETING TIME']}!"
                    
                            new_message = pd.DataFrame([[st.session_state["user"], "", "", email, registration_msg, datetime.datetime.now()]], 
                                                       columns=["NAME", "BATCH", "DEPARTMENT", "EMAIL ID", "MESSAGE", "TIMESTAMP"])
                            new_message.to_csv(MESSAGE_FILE, mode="a", header=False, index=False)
                    
                            st.success(f"✅ Registered for '{row['MEETING TOPIC']}' successfully!")
                else:
                    st.warning("⚠ No upcoming meetings at the moment.")
            else:
                st.warning("⚠ No upcoming meetings at the moment.")

        elif choice == "Chat with Admin/Alumni":
            st.write("### 💬 Chat with Admin or Alumni")

            chat_option = st.radio("Select recipient:", ["Admin", "Alumni"])

            if chat_option == "Alumni":
                alumni_list = alumni_db["EMAIL ID"].tolist()
                selected_alumni = st.selectbox("Choose Alumni", alumni_list)
            else:
                selected_alumni = "Admin"  # If chatting with admin, set recipient as "Admin"

            user_messages = student_messages_db[
                (student_messages_db["EMAIL ID"] == email) |
                (student_messages_db["EMAIL ID"] == selected_alumni)
            ]

            for _, msg in user_messages.iterrows():
                st.write(f"💬 {msg['NAME']} ({msg['EMAIL ID']}): {msg['MESSAGE']}")
              # Report button is available ONLY when chatting with an Alumni
                if chat_option == "Alumni":
                    if st.button(f"🚨 Report", key=f"report_{msg['TIMESTAMP']}"):
                        report_reason = st.text_area(f"Reason for reporting {msg['EMAIL ID']}:", key=f"reason_{msg['TIMESTAMP']}")
                        if st.button(f"Submit Report", key=f"submit_{msg['TIMESTAMP']}"):
                            new_report = pd.DataFrame([[st.session_state["user"], msg["NAME"], msg["EMAIL ID"], msg["MESSAGE"], msg["TIMESTAMP"], report_reason]],
                                                      columns=["REPORTER", "REPORTED_USER", "EMAIL ID", "MESSAGE", "TIMESTAMP", "REASON"])
                            new_report.to_csv(REPORTED_MESSAGES_FILE, mode="a", header=False, index=False)
                            st.warning("⚠️ Message reported successfully! Admin will review it.")   

            chat_message = st.text_area("Type your message...")
            if st.button("Send Message"):
                new_message = pd.DataFrame([[st.session_state["user"], "", "", email, chat_message, datetime.datetime.now()]], 
                                           columns=["NAME", "BATCH", "DEPARTMENT", "EMAIL ID", "MESSAGE", "TIMESTAMP"])
                new_message.to_csv(STUDENT_MESSAGE_FILE, mode="a", header=False, index=False)
                st.success("✅ Message Sent!")
                
        elif choice == "Search Alumni Analysis":
            st.subheader("📊 Search Alumni Analysis - Power BI")

            # Power BI Embedded Report Link for Admin
            SEARCH_ALUMNI_POWER_BI_URL = "https://app.powerbi.com/reportEmbed?reportId=69f327b5-00f2-44b0-946e-e9052c45607b&autoAuth=true&ctid=085c606c-851a-4f29-9538-639c1a6f40ee"

            # Embed Power BI dashboard using iframe
            st.components.v1.iframe(SEARCH_ALUMNI_POWER_BI_URL, width=850, height=450)

            st.info("🔹 This dashboard provides insights into Alumni career progress, achievments, and trends for domain tracking.")

        elif choice == "Student Details":
            st.write("### 📋 Your Details")
            student_data = student_db[student_db["email id"] == email].iloc[0]
            st.write(f"**Name:** {student_data['Name']}")
            st.write(f"**Department:** {student_data['Department']}")
            st.write(f"**Year of Study:** {student_data['Year of study']}")
            st.write(f"**CGPA:** {student_data['cgpa']}")
            st.write(f"**Interested Domain:** {student_data['intrested domain']}")
            st.write(f"**Interested Country:** {student_data['intrested country']}")
            st.write(f"**Passing Year:** {student_data['passing year']}")



st.sidebar.button("Logout", on_click=lambda: st.session_state.clear())
