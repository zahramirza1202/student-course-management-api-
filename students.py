from flask import Flask,request,jsonify
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
#GET /students->list all students    
@app.route('/students',methods=['GET'])
def get_students():
    conn=get_db_connection()
    cursor=conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM students")
    students= cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(students),200

    
#GET /students/<id> ->get student by ID
@app.route('/students/<int:student_id>', methods=['GET'])
def get_student(student_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM students WHERE id = %s", (student_id,))
    student = cursor.fetchone()
    cursor.close()
    conn.close()

    if student:
        return jsonify(student), 200
    else:
        return jsonify({"error": "Student not found"}), 404


#POST /students -> add a new student
@app.route('/students', methods=['POST'])
def add_student():
    data=request.get_json()
    name=data.get("name")
    email=data.get("email")
    if not name or not email:
        return jsonify({"error": "Name and email are required"}),400
    
    try:
        conn=get_db_connection()
        cursor=conn.cursor()
        cursor.execute("INSERT INTO students (name, email) VALUES (%s,%s)",(name,email))
        conn.commit()
        new_id=cursor.lastrowid
        cursor.close()
        conn.close()
        return jsonify ({"message": "Student added","id":new_id}), 202
    except mysql.connector.IntegrityError:
        return jsonify({"error": "Email already exists"}), 400

    
#PUT /students/<id> -> update student details
@app.route('/students/<int:student_id>', methods=['PUT'])
def update_student(student_id):
    data=request.get_json()
    name=data.get("name")
    email=data.get("email")
    
    conn=get_db_connection()
    cursor=conn.cursor()
    cursor.execute("SELECT*FROM students WHERE id=%s",(student_id,))
    if not cursor.fetchone():
        cursor.close()
        conn.close()
        return jsonify ({"error": "Students not found"}), 404
    
    cursor.execute("UPDATE students SET name=%s, email=%s where id=%s", (name,email,student_id))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"message": "Student updated"}), 200

# DELETE /students/<id> -> delete student and their enrollments
@app.route('/students/<int:student_id>', methods=['DELETE'])
def delete_student(student_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Check if the student exists
    cursor.execute("SELECT * FROM students WHERE id = %s", (student_id,))
    if not cursor.fetchone():
        cursor.close()
        conn.close()
        return jsonify({"error": "Student not found"}), 404

    try:
        # First delete enrollments linked to the student
        cursor.execute("DELETE FROM enrollments WHERE student_id = %s", (student_id,))

        # Then delete the student
        cursor.execute("DELETE FROM students WHERE id = %s", (student_id,))

        conn.commit()
        return jsonify({"message": "Student and their enrollments deleted"}), 200

    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500

    finally:
        cursor.close()
        conn.close()
if __name__ == "__main__":
    app.run(debug=True)