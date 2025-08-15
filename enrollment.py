from flask import Flask,request,jsonify
from datetime import date 
import mysql.connector
import os

app=Flask(__name__)

def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST","localhost"),
        user=os.getenv("DB_USER","root"),
        password=os.getenv("DB_PASSWORD",""),
        database=os.getenv("DB_NAME","studentDB")
    )
    
#POST /enroll -> Enroll a student in a course

@app.route('/enroll', methods=['POST'])
def enroll_student():
    data = request.get_json()
    student_id = data.get("student_id")
    course_id = data.get("course_id")
    if not student_id or not course_id:
        return jsonify({"error": "student_id and course_id are required"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    # Check if student exists
    cursor.execute("SELECT * FROM students WHERE id=%s", (student_id,))
    if not cursor.fetchone():
        cursor.close()
        conn.close()
        return jsonify({"error": f"Student with id {student_id} not found"}), 404

    # Check if course exists
    cursor.execute("SELECT * FROM courses WHERE id=%s", (course_id,))
    if not cursor.fetchone():
        cursor.close()
        conn.close()
        return jsonify({"error": f"Course with id {course_id} not found"}), 404

    # Check if already enrolled
    cursor.execute("""
        SELECT * FROM enrollments
        WHERE student_id = %s AND course_id=%s
    """, (student_id, course_id))
    if cursor.fetchone():
        cursor.close()
        conn.close()
        return jsonify({"error": "Student is already enrolled in this course"}), 409

    # Insert enrollment
    try:
        cursor.execute("""
            INSERT INTO enrollments (student_id, course_id, enrollment_date)
            VALUES (%s, %s, %s)
        """, (student_id, course_id, date.today()))
        conn.commit()
        return jsonify({
            "message": "Enrollment successful",
            "student_id": student_id,
            "course_id": course_id,
            "enrollment_date": str(date.today())
        }), 201
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()
        
 #GET /enrollment -> list all enrollment with student and course names
@app.route('/enrollments',methods=['GET']) 
def get_enrollments():
    conn=get_db_connection()
    cursor=conn.cursor(dictionary=True)
    try:
        cursor.execute( """
         SELECT e.id AS enrollment_id,
                s.id AS srudent_id, s.name AS student_name,
                c.id AS course_id, c.title AS course_title
        FROM enrollments e
        JOIN students s ON e.student_id = s.id
        JOIN courses c ON e.course_id = c.id
         """ )
        enrollments = cursor.fetchall()
        return jsonify(enrollments), 200
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error":str(e)}), 500
    finally:
        cursor.close()
        conn.close()
    
if __name__=="__main__":
    app.run(debug=True)