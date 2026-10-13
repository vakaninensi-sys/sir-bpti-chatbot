from flask import Flask, render_template, request, jsonify
import sqlite3
import re
from difflib import SequenceMatcher
from datetime import datetime
from pathlib import Path

app = Flask(__name__)
BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "chatbot.db"

# These are starter answers based on the supplied project report.
# Edit/add rows in the seed data below to match your college's real information.
STARTER_INTENTS = [
    ("bpti_about", "About Sir BPTI Bhavnagar", ["bpti", "sir bpti", "sir bhavsinhji polytechnic institute", "about bpti", "bhavnagar polytechnic", "college information", "college details", "કોલેજ વિશે", "બિપિટી", "બીપીટીઆઈ"],
     "Sir Bhavsinhji Polytechnic Institute (Sir BPTI) is located at Vidhyanagar, Bhavnagar, Gujarat 364002. This chatbot focuses especially on the Information Technology (IT) Diploma Department. Official IT department website: https://sites.google.com/view/itdeptsirbpti/home"),
    ("it_diploma", "Diploma in Information Technology", ["it diploma", "diploma in information technology", "information technology course", "it department", "it branch", "duration of it diploma", "how many years is it diploma", "આઈટી ડિપ્લોમા", "આઇટી બ્રાન્ચ"],
     "Sir BPTI's Information Technology Department offers a 3-year full-time Diploma in Information Technology. The department page lists a total sanctioned intake of 180 students (120 first shift and 60 second shift). Check the official department page for current details: https://sites.google.com/view/itdeptsirbpti/about-department"),
    ("it_subjects", "IT subjects and semesters", ["it subjects", "subjects in it", "semester subjects", "syllabus", "semester 1", "semester 2", "semester 3", "semester 4", "semester 5", "semester 6", "academics", "વિષયો", "સિલેબસ"],
     "The IT Department website has separate pages for Semesters 1 to 6 with subjects, syllabus, practicals, assignments, and tutorials. Open: https://sites.google.com/view/itdeptsirbpti/academics. For example, Semester 1 lists Mathematics-I, Communication Skills in English, Engineering Chemistry, Python Programming, Introduction to IT Systems, and Web Development using PHP."),
    ("it_facilities", "IT department facilities", ["it lab", "computer lab", "internet facility", "labs in it", "it facilities", "practical facilities", "facilities in it department"],
     "The official IT Department page says the labs have computers and that internet access and audio-visual teaching methods are provided. Expert lectures from IT industry professionals are also arranged. Source: https://sites.google.com/view/itdeptsirbpti/about-department"),
    ("it_activities", "IT department activities", ["viditam", "tech fest", "it event", "coding competition", "department activities", "it activities", "industry visit", "idp", "internship"],
     "The IT Department website describes Viditam, a department tech fest with activities such as coding competitions, debugging/program-solving, treasure hunts, and gaming. It also describes Industry Defined Problem (IDP) exposure in the last two semesters. Check the department website for current events: https://sites.google.com/view/itdeptsirbpti/home"),
    ("bpti_contact", "Sir BPTI IT Department contact", ["bpti contact", "it department contact", "it department phone", "phone number", "contact number", "college address", "where is bpti", "address", "સંપર્ક", "સરનામું"],
     "Sir BPTI, IT Department, Sir BPTI Campus, Vidhyanagar, Bhavnagar, Gujarat 364002. The IT Department website lists phone numbers (0278) 251 5393, 2426742, and 2524371. Please verify contact details on the official department site: https://sites.google.com/view/itdeptsirbpti/home"),
    ("bpti_vision", "Institute vision and mission", ["vision", "mission", "bpti vision", "bpti mission", "institute mission"],
     "Sir BPTI's stated vision is to become a premier institute in Diploma Engineering by producing technical professionals able to meet challenges and serve society and industry. Its mission includes industry-oriented, value-based technical education, innovative teaching, and stronger institute-industry links. Source: https://generaldept.wixsite.com/bpti"),
    ("it_sem1", "Semester 1 IT subjects", ["semester 1 subjects", "sem 1 subjects", "subjects in sem 1", "first semester subjects", "sem1", "semester one", "સેમ 1 વિષયો", "સેમેસ્ટર 1"],
     "Official IT Department website lists Semester 1 subjects: Induction Programme with Essence of Indian Knowledge, Mathematics-I, Communication Skills in English, Sports and Yoga, Engineering Chemistry, Python Programming, Introduction to I.T. Systems, and Web Development using PHP. Subject codes, syllabus, practicals and assignments: https://sites.google.com/view/itdeptsirbpti/academics/semester-1"),
    ("it_sem3", "Semester 3 IT subjects", ["semester 3 subjects", "sem 3 subjects", "subjects in sem 3", "third semester subjects", "sem3", "semester three", "સેમ 3 વિષયો", "સેમેસ્ટર 3"],
     "Official IT Department website lists Semester 3 subjects: Digital Marketing, Cryptography and Web Security, Data Structures with Python, Database Management, Object Oriented Programming with JAVA, and Operating Systems. Details and syllabus: https://sites.google.com/view/itdeptsirbpti/academics/semester-3"),
    ("it_all_semesters", "All semester study resources", ["all semester subjects", "semester 2 subjects", "semester 4 subjects", "semester 5 subjects", "semester 6 subjects", "sem 2", "sem 4", "sem 5", "sem 6", "syllabus link", "study material", "practicals", "assignments", "tutorials", "બધા સેમેસ્ટર", "સિલેબસ લિંક"],
     "The official IT Department Academics page has separate links for Semesters 1 to 6. Open the relevant semester to see its subjects, syllabus, practicals, assignments, tutorials and learning resources: https://sites.google.com/view/itdeptsirbpti/academics. I will not guess the subject list for semesters where I could not verify the page contents."),
    ("it_vision_mission", "IT Department vision and mission", ["it department vision", "it department mission", "department vision", "department mission", "vision of it", "mission of it"],
     "The IT Department vision is to become a reputed center of IT engineering education focused on academic excellence, employability, expertise and moral values. Its mission includes turning theory into real-world applications, strengthening institute-industry interaction, and imparting ethical values. Official source: https://sites.google.com/view/itdeptsirbpti/about-department/dept-vision-mission"),
    ("student_corner", "Student corner and notices", ["student corner", "timetable", "time table", "exam timetable", "mid semester exam", "online fees payment", "important formats", "college notice", "notices", "student notice", "ટાઈમ ટેબલ", "નોટિસ"],
     "The official IT Department website has a Student Corner and links for timetable and student notices. Timetables and notices can change by academic term, so check the latest post here: https://sites.google.com/view/itdeptsirbpti/student-corner/time-table and the main website https://sites.google.com/view/itdeptsirbpti/home"),
    ("it_department_overview", "IT department overview and intake", ["it department overview", "about it department", "total intake", "intake of it", "how many seats in it", "number of seats", "it course seats", "આઈટી માં કેટલી સીટ"],
     "The official IT Department page describes a 3-year full-time Diploma in Information Technology. It lists a total sanctioned intake of 180 students: 120 in the first shift and 60 in the second shift. This is the website's listed sanctioned intake; current admission availability should be checked separately. Source: https://sites.google.com/view/itdeptsirbpti/about-department"),
    ("greeting", "Greeting and welcome", ["hello", "hi", "hey", "good morning", "good afternoon", "good evening", "kem cho", "નમસ્તે", "હેલો"],
     "Hello! 👋 Welcome to the Sir BPTI Bhavnagar College Chatbot. Ask me about the IT Diploma, semester 1–6 study links, verified semester subjects, department facilities, Viditam TechFest, student notices, vision and mission, contact details, admission guidance, or basic programming."),
    ("admission", "Admission enquiry", ["admission", "how to take admission", "admission process", "apply for college", "પ્રવેશ", "પ્રવેશ પ્રક્રિયા"],
     "For admission, check the college's official admission notice and eligibility criteria. Keep your previous marksheets, ID proof, photographs, and required certificates ready. Exact dates and rules should be confirmed from the college office."),
    ("courses", "Courses offered", ["course", "courses", "branch", "branches", "what can i study", "available course", "કોર્સ", "બ્રાન્ચ"],
     "Sir BPTI's IT Department offers a 3-year full-time Diploma in Information Technology. For other branches and the latest official course list, please check the institute prospectus or official website."),
    ("fees", "Fee details", ["fees", "fee structure", "tuition fee", "college fee", "ફી", "કેટલી ફી"],
     "Fees can change by course, semester, and category. Please check the latest fee circular or contact the college office for the exact amount."),
    ("timing", "College timing", ["college timing", "timings", "opening time", "when does college start", "college time", "સમય"],
     "I don't have verified live college timings in this demo. Please check your timetable, latest notice, or ask the college office."),
    ("holiday", "Holiday information", ["holiday", "is college closed", "vacation", "રજા", "રજાઓ"],
     "For confirmed holidays, please check the latest college notice or academic calendar. I don't want to give you an unverified date."),
    ("events", "College activities and events", ["annual day", "sports day", "event", "events", "cultural activity", "function", "college activity", "પ્રોગ્રામ"],
     "The project report describes helping students get updates about annual day, sports day, cultural activities, training, placement events, and special announcements. Add your college's current notices to the knowledge base for exact dates."),
    ("facilities", "Campus facilities", ["facility", "facilities", "library", "lab", "laboratory", "computer lab", "canteen", "hostel", "સુવિધા"],
     "I can help with general campus-facility enquiries. For exact availability of the library, labs, canteen, hostel, or transport, please confirm with your college."),
    ("placement", "Training and placement", ["placement", "placements", "campus interview", "training", "job", "company visit", "પ્લેસમેન્ટ"],
     "The report identifies training and placement announcements as important student information. For current drives, eligibility, and schedules, check the placement cell's latest notice."),
    ("contact", "College contact", ["contact", "phone number", "email", "address", "college office", "સંપર્ક"],
     "Sir BPTI IT Department, Sir BPTI Campus, Vidhyanagar, Bhavnagar, Gujarat 364002. The department website lists (0278) 251 5393, 2426742, and 2524371. Please verify these details on https://sites.google.com/view/itdeptsirbpti/home."),
    ("programming", "Programming basics", ["what is programming", "programming language", "what is coding", "coding", "programming"],
     "Programming is the process of writing instructions that a computer can execute. A programming language, such as Python, Java, or C, is used to write those instructions."),
    ("python", "Python language", ["python", "what is python", "python language"],
     "Python is a high-level, general-purpose programming language known for readable syntax. It is used in web development, automation, data analysis, AI, and machine learning."),
    ("java", "Java language", ["java", "what is java", "java language"],
     "Java is a high-level, object-oriented programming language. Java programs commonly run on the Java Virtual Machine (JVM)."),
    ("database", "Database basics", ["database", "what is database", "dbms", "sql", "sqlite"],
     "A database stores and organizes information so it can be retrieved and updated. DBMS means Database Management System; SQL is commonly used to work with relational databases."),
    ("chatbot", "What is a chatbot", ["chatbot", "what is chatbot", "how does this bot work", "what can you do"],
     "A chatbot is a software application that communicates with users through messages. This project receives a question, checks it against stored intents and keywords, chooses a suitable response, and saves the conversation in a database."),
    ("thanks", "Thanks", ["thanks", "thank you", "thankyou", "આભાર", "thank u"],
     "You're welcome! 😊 Ask me anything else about college enquiries or basic programming."),
    ("goodbye", "Goodbye", ["bye", "goodbye", "see you", "ચાલો બાય"],
     "Goodbye! 👋 Have a great day. You can come back whenever you have another question."),

    ("official_websites", "Official college and department websites", ["official website", "college website", "website link", "website of bpti", "it department website", "official link", "website", "official site", "college ni website", "website link aapo", "college ni link", "bpti ni website"],
     "Official IT Department website: https://sites.google.com/view/itdeptsirbpti/home\nIT Department Academics (Semesters 1–6): https://sites.google.com/view/itdeptsirbpti/academics\nInstitute information/vision and mission page: https://generaldept.wixsite.com/bpti\nPlease use the official pages for the latest notices and confirm any time-sensitive details with the college."),
    ("semester2", "Semester 2 IT study resources", ["semester 2", "sem 2", "sem2", "second semester", "sem 2 subjects", "semester 2 subjects", "2nd sem", "sem 2 no syllabus", "sem 2 na subject", "બીજા સેમેસ્ટર", "સેમ 2"],
     "Semester 2 IT subjects and learning material: open the official Academics page and choose Semester 2: https://sites.google.com/view/itdeptsirbpti/academics. The page may include subject details, syllabus, practicals, assignments and tutorials. I will not guess a subject list if it is not confirmed on the page."),
    ("semester4", "Semester 4 IT study resources", ["semester 4", "sem 4", "sem4", "fourth semester", "sem 4 subjects", "semester 4 subjects", "4th sem", "sem 4 no syllabus", "sem 4 na subject", "ચોથા સેમેસ્ટર", "સેમ 4"],
     "Semester 4 IT subjects and learning material: open the official Academics page and choose Semester 4: https://sites.google.com/view/itdeptsirbpti/academics. Use the official page for the current subject list, syllabus, practicals, assignments and tutorials."),
    ("semester5", "Semester 5 IT study resources", ["semester 5", "sem 5", "sem5", "fifth semester", "sem 5 subjects", "semester 5 subjects", "5th sem", "sem 5 no syllabus", "sem 5 na subject", "પાંચમા સેમેસ્ટર", "સેમ 5"],
     "Semester 5 IT subjects and learning material: open the official Academics page and choose Semester 5: https://sites.google.com/view/itdeptsirbpti/academics. Check the official page for the current subject list, syllabus, practicals, assignments and tutorials."),
    ("semester6", "Semester 6 IT study resources", ["semester 6", "sem 6", "sem6", "sixth semester", "sem 6 subjects", "semester 6 subjects", "6th sem", "final semester", "sem 6 no syllabus", "sem 6 na subject", "છઠ્ઠા સેમેસ્ટર", "સેમ 6"],
     "Semester 6 IT subjects and learning material: open the official Academics page and choose Semester 6: https://sites.google.com/view/itdeptsirbpti/academics. Check the official page for current subjects, syllabus, practicals, assignments and tutorials."),
    ("exam_resources", "Exam and syllabus resources", ["exam", "exam date", "exam schedule", "gtu exam", "exam form", "hall ticket", "result", "rechecking", "reassessment", "syllabus link", "paper", "previous paper", "old paper", "practical exam", "exam ni mahiti", "result kyare", "પરિક્ષા", "પરિણામ"],
     "For current exam dates, hall tickets, results, exam forms and reassessment rules, check the latest official college/GTU notices. IT Department study resources and semester links are here: https://sites.google.com/view/itdeptsirbpti/academics. This chatbot does not have live exam/result data."),
    ("admission_eligibility", "Admission eligibility and process", ["eligibility", "who can take admission", "diploma admission", "first year admission", "direct second year", "acpc", "admission form", "admission last date", "admission date", "admission fees", "admission process gujarat", "admission mate shu joie", "પ્રવેશ માટે"],
     "Admission eligibility, process, dates, seat availability and documents can change each year. Check the latest official admission authority/college notice and confirm with the college office. IT Department overview: https://sites.google.com/view/itdeptsirbpti/about-department. This chatbot does not have live admission status."),
    ("department_faculty", "Faculty and department staff information", ["faculty", "professor", "teacher", "hod", "head of department", "staff name", "lecturer", "teacher name", "faculty list", "hod name", "hod kon che", "teacher kon che", "faculty details"],
     "For the current HOD and faculty list, please check the staff/faculty details on the official IT Department website: https://sites.google.com/view/itdeptsirbpti/home. Staff postings can change, so I will not invent names or titles."),
    ("scholarships", "Scholarship guidance", ["scholarship", "mysy", "digital gujarat", "scholarship form", "scholarship last date", "scholarship eligibility", "fee refund", "scholarship for diploma", "સ્કોલરશીપ", "મુખ્યમંત્રી યુવા સ્વાવલંબન", "ડિજિટલ ગુજરાત"],
     "Scholarship eligibility, income limits, marks requirements and deadlines depend on the specific scheme and current rules. Check the official MYSY or Digital Gujarat portal and the latest government notice; the college office can help confirm which scheme applies to diploma students. This chatbot does not store personal application status or live deadlines."),
    ("hostel_transport", "Hostel and transport information", ["hostel", "hostel facility", "bus", "transport", "college bus", "hostel fees", "hostel available", "hostel che", "bus facility", "રહેવાની સુવિધા", "બસ સુવિધા"],
     "I do not have verified current details about hostel availability, transport routes or charges. Please confirm these directly with the college office and check the latest official notices. I will not assume that a facility is available."),
    ("library_campus", "Library and campus facilities", ["library", "library timing", "library books", "campus facilities", "canteen", "sports ground", "wifi", "internet", "computer lab", "lab facility", "library che", "canteen che", "college ma suvidha"],
     "The IT Department website mentions computer laboratories, internet access and audio-visual teaching methods. For current library hours, canteen availability, sports facilities and other campus services, please verify with the college. Department source: https://sites.google.com/view/itdeptsirbpti/about-department"),
    ("programming_help", "Programming and IT subject help", ["python code", "java code", "html", "css", "javascript", "c programming", "sql query", "dbms help", "data structure", "operating system", "cyber security", "cryptography", "digital marketing", "web development", "programming help", "it subject help"],
     "I can answer basic IT questions and help explain Python, Java, HTML/CSS, SQL, data structures, operating systems and other diploma topics. Send the exact topic or question, and mention your semester if you want a GTU-style answer. For official syllabus details, use https://sites.google.com/view/itdeptsirbpti/academics."),
    ("what_is_programming", "What is programming", ["what is programming", "programming meaning", "programming shu che", "programming language", "what is a programming language"],
     "Programming is the process of writing instructions that a computer can follow to perform a task. A programming language such as Python, Java or C is used to write those instructions."),
    ("python_basics", "Python basics", ["what is python", "python meaning", "python basics", "python shu che", "python features"],
     "Python is a high-level, general-purpose programming language known for readable syntax. It is used for automation, web development, data analysis, AI and machine learning. Example: print(\"Hello, World!\") displays Hello, World!"),
    ("java_basics", "Java basics", ["what is java", "java meaning", "java basics", "java programming", "java shu che"],
     "Java is a high-level, object-oriented programming language. Java source code is compiled to bytecode that runs on the Java Virtual Machine (JVM), helping Java programs run on different supported platforms."),
    ("html_css", "HTML and CSS", ["what is html", "html meaning", "what is css", "css meaning", "html css", "web page structure"],
     "HTML defines the structure and content of a web page. CSS controls its presentation, such as colours, spacing, fonts and layout. HTML is markup; CSS is a style-sheet language."),
    ("sql_dbms", "SQL and DBMS basics", ["what is sql", "sql meaning", "what is dbms", "dbms meaning", "database management system", "sql query"],
     "A DBMS is software used to create, store, organise and manage databases. SQL is a language commonly used to query and update relational databases. Example: SELECT * FROM students; retrieves all columns and rows from a table named students."),
    ("data_structures", "Data structures basics", ["what is data structure", "data structures", "stack and queue", "what is stack", "what is queue", "linked list", "tree data structure"],
     "A data structure organises data so it can be accessed and modified efficiently. Common examples include arrays, linked lists, stacks (last in, first out), queues (first in, first out), trees and graphs."),
    ("operating_system", "Operating system basics", ["what is operating system", "os meaning", "operating system functions", "what is os"],
     "An operating system (OS) manages computer hardware and software resources. Its responsibilities include process management, memory management, file management, device management and providing a user interface. Examples include Windows, Linux, Android and macOS."),
    ("cyber_security", "Cyber security basics", ["what is cyber security", "cyber security meaning", "what is cryptography", "web security", "online safety"],
     "Cyber security protects computers, networks, applications and data from unauthorised access or attacks. Good basics include using unique passwords, enabling multi-factor authentication, updating software and avoiding suspicious links. Cryptography protects information using techniques such as encryption."),
    ("nlp_explanation", "NLP and chatbot working", ["what is nlp", "how does chatbot work", "how chatbot works", "what is natural language processing", "chatbot working", "how do you understand questions"],
     "Natural Language Processing (NLP) is a field of AI that helps computers process human language. This demo chatbot currently uses keyword patterns and fuzzy text matching against a prepared knowledge base; it does not use a live ChatGPT/OpenAI API unless one is separately configured."),
    ("privacy_clear_chat", "Clear or start a new chat", ["clear chat", "delete chat", "new chat", "remove history", "clear history", "chat delete", "old chat delete", "chat clear kem karvu", "જૂની ચેટ કાઢો", "ચેટ ક્લિયર"],
     "Use the Clear Chat or New Chat button above the conversation to remove the saved chat history from this local app. If the button does not respond, restart the app and try again. Clearing this chatbot's local history does not delete messages from any other app."),
]

def connect_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with connect_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS intents (
                intent_id INTEGER PRIMARY KEY AUTOINCREMENT,
                intent_name TEXT NOT NULL UNIQUE,
                description TEXT
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS responses (
                response_id INTEGER PRIMARY KEY AUTOINCREMENT,
                intent_id INTEGER NOT NULL,
                response_text TEXT NOT NULL,
                FOREIGN KEY(intent_id) REFERENCES intents(intent_id)
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS intent_patterns (
                pattern_id INTEGER PRIMARY KEY AUTOINCREMENT,
                intent_id INTEGER NOT NULL,
                pattern_text TEXT NOT NULL,
                FOREIGN KEY(intent_id) REFERENCES intents(intent_id)
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS chat_history (
                chat_id INTEGER PRIMARY KEY AUTOINCREMENT,
                message TEXT NOT NULL,
                response_text TEXT NOT NULL,
                timestamp TEXT NOT NULL
            )
        """)
        for name, description, patterns, response in STARTER_INTENTS:
            existing = conn.execute(
                "SELECT intent_id FROM intents WHERE intent_name = ?", (name,)
            ).fetchone()
            if existing:
                intent_id = existing["intent_id"]
                # Refresh the canned response and add any new patterns on app updates.
                conn.execute("UPDATE intents SET description = ? WHERE intent_id = ?", (description, intent_id))
                conn.execute("UPDATE responses SET response_text = ? WHERE intent_id = ?", (response, intent_id))
                for pattern in patterns:
                    found = conn.execute(
                        "SELECT 1 FROM intent_patterns WHERE intent_id = ? AND pattern_text = ?",
                        (intent_id, pattern.lower())
                    ).fetchone()
                    if not found:
                        conn.execute(
                            "INSERT INTO intent_patterns (intent_id, pattern_text) VALUES (?, ?)",
                            (intent_id, pattern.lower())
                        )
            else:
                cur = conn.execute(
                    "INSERT INTO intents (intent_name, description) VALUES (?, ?)",
                    (name, description)
                )
                intent_id = cur.lastrowid
                conn.execute(
                    "INSERT INTO responses (intent_id, response_text) VALUES (?, ?)",
                    (intent_id, response)
                )
                conn.executemany(
                    "INSERT INTO intent_patterns (intent_id, pattern_text) VALUES (?, ?)",
                    [(intent_id, pattern.lower()) for pattern in patterns]
                )

def normalize(text):
    text = (text or "").lower().strip()
    text = re.sub(r"[^\w\s]", " ", text, flags=re.UNICODE)
    return re.sub(r"\s+", " ", text).strip()

def score_pattern(user_text, pattern):
    user_norm = normalize(user_text)
    pattern_norm = normalize(pattern)
    if not user_norm or not pattern_norm:
        return 0.0
    if user_norm == pattern_norm:
        return 1.0
    if pattern_norm in user_norm:
        return min(0.96, 0.72 + len(pattern_norm) / max(len(user_norm), 1) * 0.24)
    user_words = set(user_norm.split())
    pattern_words = set(pattern_norm.split())
    overlap = len(user_words & pattern_words) / max(len(pattern_words), 1)
    similarity = SequenceMatcher(None, user_norm, pattern_norm).ratio()
    return max(overlap * 0.78, similarity * 0.82)

def get_answer(message):
    with connect_db() as conn:
        rows = conn.execute("""
            SELECT i.intent_name, p.pattern_text, r.response_text
            FROM intents i
            JOIN intent_patterns p ON p.intent_id = i.intent_id
            JOIN responses r ON r.intent_id = i.intent_id
        """).fetchall()

    best_score = 0.0
    best_answer = None
    for row in rows:
        score = score_pattern(message, row["pattern_text"])
        if score > best_score:
            best_score = score
            best_answer = row["response_text"]

    # Lightweight rule-based matching; no external AI API or internet connection required.
    if best_score >= 0.38 and best_answer:
        return best_answer

    return ("I could not find a verified answer to that exact question yet. 🤔 I can help with Sir BPTI Bhavnagar, the IT Diploma, semester 1–6 study links, verified semester subjects, labs, department activities, student notices, vision and mission, admission guidance, contact details, fees, and basic programming. "
            "For exact college-specific dates or details, please add verified information to the database.")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True) or {}
    message = (data.get("message") or "").strip()
    if not message:
        return jsonify({"error": "Please type a message first."}), 400
    if len(message) > 1000:
        return jsonify({"error": "Please keep your message under 1000 characters."}), 400

    response = get_answer(message)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with connect_db() as conn:
        conn.execute(
            "INSERT INTO chat_history (message, response_text, timestamp) VALUES (?, ?, ?)",
            (message, response, timestamp)
        )
    return jsonify({"message": message, "response": response, "timestamp": timestamp})

@app.route("/api/history")
def history():
    with connect_db() as conn:
        rows = conn.execute(
            "SELECT message, response_text, timestamp FROM chat_history ORDER BY chat_id DESC LIMIT 30"
        ).fetchall()
    return jsonify([dict(row) for row in reversed(rows)])

@app.route("/api/clear", methods=["POST"])
def clear_history():
    with connect_db() as conn:
        conn.execute("DELETE FROM chat_history")
    return jsonify({"ok": True})

@app.route("/health")
def health():
    return jsonify({"status": "ok", "app": "College Enquiry Chatbot"})

init_db()

if __name__ == "__main__":
    app.run(debug=True)
