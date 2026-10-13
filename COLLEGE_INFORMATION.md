# Sir BPTI Bhavnagar chatbot knowledge guide

This project is customized primarily for the publicly listed Information Technology (IT) Diploma Department. It is not a live connection to the college's internal systems.

## Official links used
- IT Department home: https://sites.google.com/view/itdeptsirbpti/home
- IT Department overview: https://sites.google.com/view/itdeptsirbpti/about-department
- Academics and semester resources: https://sites.google.com/view/itdeptsirbpti/academics
- IT Department vision and mission: https://sites.google.com/view/itdeptsirbpti/about-department/dept-vision-mission
- Student Corner / timetable: https://sites.google.com/view/itdeptsirbpti/student-corner/time-table
- Institute vision/mission page: https://generaldept.wixsite.com/bpti

## Information currently represented in the chatbot
- Institute overview and location as shown in the starter knowledge entries
- IT Diploma course duration and the sanctioned intake stated on the department page
- Semester 1 and Semester 3 subject lists where represented in the project knowledge
- Academics page for semester 1–6, syllabi, practicals, assignments and tutorials
- Department facilities: computer labs, internet access, audio-visual teaching methods and expert lectures (as described by the department page)
- Viditam TechFest and Industry Defined Problem (IDP) activities (as described by the department page)
- Department vision/mission and public contact details listed in existing starter answers
- Admission, fee, exam, scholarship, hostel/transport and timetable guidance, with reminders to verify current details
- Basic programming / IT learning support

## Details deliberately not invented
Current fee amounts, admission dates, seat availability, staff postings, class timings, holiday dates, examination dates/results, scholarship deadlines, hostel availability, transport routes, and live notices can change. The chatbot directs students to official sources or the college office rather than inventing an answer.

## Updating college information
Open `app.py` and add a new tuple to `STARTER_INTENTS` with:
1. a unique intent name,
2. a short description,
3. common English/Gujarati/Gujlish question patterns,
4. a concise answer with its official source URL.

Do not put private student records, passwords, or confidential internal information in the public chatbot.
