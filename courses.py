from flask import Flask, request, jsonify
import mysql.connector
import os

app = Flask(__name__)

def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", ""),
        database=os.getenv("DB_NAME", "studentDB")
    )

# GET /courses -> list all courses
@app.route('/courses', methods=['GET'])
def get_courses():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM courses")
    courses = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(courses), 200

# GET /courses/<id> -> get course by ID
@app.route('/courses/<int:course_id>', methods=['GET'])
def get_course(course_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM courses WHERE id = %s", (course_id,))
    course = cursor.fetchone()
    cursor.close()
    conn.close()
    if course:
        return jsonify(course), 200
    else:
        return jsonify({"error": "Course not found"}), 404

# POST /courses -> add a new course
@app.route('/courses', methods=['POST'])
def add_course():
    data = request.get_json()
    title = data.get("title")
    description = data.get("description")
    if not title or not description:
        return jsonify({"error": "Title and description are required"}), 400
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO courses (title, description) VALUES (%s, %s)", (title, description))
        conn.commit()
        new_id = cursor.lastrowid
        cursor.close()
        conn.close()
        return jsonify({"message": "Course added", "id": new_id}), 201
    except mysql.connector.IntegrityError:
        return jsonify({"error": "Title already exists"}), 400

# PUT /courses/<id> -> update course details
@app.route('/courses/<int:course_id>', methods=['PUT'])
def update_course(course_id):
    data = request.get_json()
    title = data.get("title")
    description = data.get("description")
    if not title or not description:
        return jsonify({"error": "Title and description are required"}), 400
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM courses WHERE id = %s", (course_id,))
    if not cursor.fetchone():
        cursor.close()
        conn.close()
        return jsonify({"error": "Course not found"}), 404
    cursor.execute("UPDATE courses SET title = %s, description = %s WHERE id = %s", (title, description, course_id))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"message": "Course updated"}), 200

# DELETE /courses/<id> -> delete course and related enrollments
@app.route('/courses/<int:course_id>', methods=['DELETE'])
def delete_course(course_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM courses WHERE id = %s", (course_id,))
    if not cursor.fetchone():
        cursor.close()
        conn.close()
        return jsonify({"error": "Course not found"}), 404
    try:
        cursor.execute("DELETE FROM enrollments WHERE course_id = %s", (course_id,))
        cursor.execute("DELETE FROM courses WHERE id = %s", (course_id,))
        conn.commit()
        return jsonify({"message": "Course and related enrollments deleted successfully"}), 200
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    app.run(debug=True)