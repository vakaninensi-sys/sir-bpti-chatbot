# Sir BPTI Bhavnagar College Chatbot

A runnable Flask + SQLite student project customized for Sir Bhavsinhji Polytechnic Institute (Sir BPTI), Bhavnagar, with an expanded question-and-answer knowledge base focused mainly on the Information Technology (IT) Diploma Department.

## Features
- Responsive chat interface
- New Chat and Clear Chat buttons; the local SQLite chat history is cleared when used
- Knowledge responses for college/department overview, IT Diploma, semester study links, verified subject examples, facilities, activities, vision/mission, student notices, admission guidance, fees, scholarships, exam resources, faculty lookup guidance, campus facilities and contact information
- English, Gujarati and Gujarati-in-English (Gujlish) question patterns for many common questions
- Basic programming/IT topic help
- SQLite database created automatically at first run
- No paid API key required

## Run on Windows
1. Extract this ZIP into a new folder.
2. Open the extracted `college_chatbot_project` folder.
3. Click the File Explorer address bar, type `cmd`, and press Enter.
4. Run these commands one at a time:

   ```bat
   py -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt
   python app.py
   ```

5. Keep the black Command Prompt window open and open `http://127.0.0.1:5000` in Chrome.
6. To stop the server, click Command Prompt and press `Ctrl+C`.

## Official source links
- IT Department home: https://sites.google.com/view/itdeptsirbpti/home
- Department overview: https://sites.google.com/view/itdeptsirbpti/about-department
- Academics / semester resources: https://sites.google.com/view/itdeptsirbpti/academics
- Department vision and mission: https://sites.google.com/view/itdeptsirbpti/about-department/dept-vision-mission
- Student Corner / timetable: https://sites.google.com/view/itdeptsirbpti/student-corner/time-table
- Institute vision/mission page: https://generaldept.wixsite.com/bpti

## Important accuracy note
This is a local rule-based chatbot, not a live college database or a generative AI service. Publicly available IT Department information and official links are included. It cannot guarantee that literally every college detail is included. Fees, admission dates, current seat availability, faculty postings, timetables, holidays, exam/results, scholarship deadlines and other changing information should be verified from the latest official notice or college office. Read `COLLEGE_INFORMATION.md` for the knowledge scope and update instructions.

## Main files
- `app.py` — Flask server, question matching, knowledge entries and SQLite database logic
- `templates/index.html` — chat interface and Clear/New Chat actions
- `static/style.css` — responsive styling
- `requirements.txt` — Python dependency
- `COLLEGE_INFORMATION.md` — included knowledge scope, source links and update instructions

The `chatbot.db` file is created automatically on first run. If you update `STARTER_INTENTS` in `app.py`, the app adds new patterns and updates the matching stored responses when it next starts.
