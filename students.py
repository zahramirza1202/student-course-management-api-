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
    
if __name__=="__main__":
    app.run(debug=True)