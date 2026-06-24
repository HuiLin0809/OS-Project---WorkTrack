from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import mysql.connector
import threading
import queue
app = Flask(__name__)
CORS(app)
#DB config
DB_CONFIG = {
    'host': 'localhost',
    'database': 'worktrack_db',
    'user': 'worktrack_user',
    'password': 'worktrack123',
}

#FCFS Queue for process management demo
checkin_queue = queue.Queue()
process_order_counter = [0]
queue_lock = threading.Lock()
def get_db():
	return mysql.connector.connect(**DB_CONFIG)
def queue_worker():
	while True:
		data = checkin_queue.get()
		try:
			with queue_lock:
				process_order_counter[0] += 1
				order = process_order_counter[0]
			conn = get_db()
			cursor = conn.cursor()
			cursor.execute('''
				INSERT INTO checkins
				(employee_id, employee_name, latitude, longitude, process_order)
				VALUES (%s, %s, %s, %s, %s)
			''', (
				data['employee_id'],
				data['employee_name'],
				data['latitude'],
				data['longitude'],
				order
			))
			conn.commit()
			cursor.close()
			conn.close()
			print(f"[FCFS] Processed order#{order}: {data['employee_name']}")
		except Exception as e:
			print(f"[ERROR] {e}")
		finally:
			checkin_queue.task_done()

#start worker thread
worker = threading.Thread(target=queue_worker, daemon=True)
worker.start()
@app.route('/api/checkin', methods=['POST'])
def checkin():
	data = request.get_json()

	required = ['empId', 'empName', 'latitude', 'longitude']
	if not all(k in data for k in required):
		return jsonify({'status': 'error', 'message': 'Missing fields'}), 400

	#Map frontend field names to backend
	checkin_data = {
		'employee_id': data['empId'],
		'employee_name': data['empName'],
		'latitude': data['latitude'],
		'longitude': data['longitude']
	}

	checkin_queue.put(checkin_data)
	position = checkin_queue.qsize()
	print(f"[QUEUE] {data['empName']} added. Position: {position}")

	return jsonify({
		'status': 'success',
		'message': f'Check-in received. Queue position: {position}'
	}), 200
@app.route('/')
def dashboard():
	conn = get_db()
	cursor = conn.cursor(dictionary=True)
	cursor.execute('SELECT * FROM checkins ORDER BY id ASC')
	records = cursor.fetchall()
	cursor.close()
	conn.close()
	return render_template('dashboard.html', records=records)
@app.route('/api/records', methods=['GET'])
def get_records():
	conn = get_db()
	cursor = conn.cursor(dictionary=True)
	cursor.execute('SELECT * FROM checkins ORDER BY id  ASC')
	records = cursor.fetchall()
	cursor.close()
	conn.close()
	return jsonify(records)
if __name__ == '__main__':
	app.run(host='0.0.0.0', port=5000, debug=True)
