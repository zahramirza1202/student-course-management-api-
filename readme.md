# Student Course Management API
This is my ongoing assignment for building a REST API using Python Flask and MySQL.

## Current Progress
- Set up Flask application with blueprint structure
- Implemented GET `/students` and GET `/students/<id>` endpoints
- Added POST, PUT, and DELETE routes for students ✅

## Current Progress
- Structured Flask application using Blueprints for modular design
• Students module:
- GET /students – fetch all students
- GET /students/<id> – fetch specific student
- POST /students – add new student
- PUT /students/<id> – update student details
- DELETE /students/<id> – remove student
• Courses module:
- GET /courses – fetch all courses
- GET /courses/<id> – fetch specific course
- POST /courses – add new course
• Enrollments module:
- GET /enrollments – fetch all enrollments
- POST /enrollments – enroll student in a course