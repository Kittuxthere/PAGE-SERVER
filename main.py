from flask import Flask, request, jsonify, Response
import threading
import time
import requests
import uuid

# --- Flask App Initialization ---
app = Flask(__name__)

# --- Global In-Memory Task Storage ---
running_tasks = {}

# ==============================================================================
# === THE WORKER FUNCTION (RUNS IN A BACKGROUND THREAD) ===
# ==============================================================================
def message_sending_worker(task_id, access_tokens, thread_id, messages, hater_name, time_interval):
    """
    This function is now modified to work EXACTLY like your original script.
    """
    stop_event = running_tasks[task_id]['stop_event']
    
    print(f"✅ [Task: {task_id}] Thread started for conversation: {thread_id}")

    num_messages = len(messages)
    num_tokens = len(access_tokens)
    
    # ### CHANGE 1 HERE ###: Removed '/messages' to match your working script's URL.
    post_url = f'https://graph.facebook.com/v15.0/t_{thread_id}/'
    
    message_index = 0
    while not stop_event.is_set():
        try:
            token_index = message_index % num_tokens
            access_token = access_tokens[token_index]
            
            current_message_text = messages[message_index % num_messages]
            final_message = f"{hater_name} {current_message_text}"

            parameters = {
                'access_token': access_token,
                'message': final_message
            }
            
            # ### CHANGE 2 HERE ###: Changed from `data=parameters` back to `json=parameters`.
            # We are also adding the Content-Type header to be safe.
            response = requests.post(post_url, json=parameters, headers={'Content-Type': 'application/json'})

            current_time_str = time.strftime("%Y-%m-%d %I:%M:%S %p")
            
            if response.ok:
                print(f"\n[Task: {task_id}] [✓] Message Sent! | To: {thread_id}")
            else:
                error_info = response.json().get('error', {}).get('message', 'No specific error from API.')
                print(f"\n[Task: {task_id}] [✗] Failed to Send! | To: {thread_id} | Error: {error_info}")
                
            message_index += 1
            stop_event.wait(timeout=time_interval)

        except requests.exceptions.RequestException as e:
            print(f"\n[Task: {task_id}] [✗] Network Error: {e}")
            print("  └── Retrying in 30 seconds...")
            stop_event.wait(timeout=30)

    if task_id in running_tasks:
        del running_tasks[task_id]
    print(f"🛑 [Task: {task_id}] Thread has been stopped and cleaned up.")

# ==============================================================================
# === HTML, CSS, JAVASCRIPT as a Python String (No Changes Here) ===
# ==============================================================================
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>This Server Made By Mr Jitender</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            background-color: #f0f2f5; margin: 0; padding: 20px; color: #1c1e21;
        }
        .container {
            max-width: 800px; margin: 20px auto; background: #ffffff; padding: 25px 30px;
            border-radius: 12px; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        }
        h1, h2 { color: #007bff; border-bottom: 2px solid #e7e7e7; padding-bottom: 10px; margin-top: 0; }
        .form-group { margin-bottom: 20px; }
        label { display: block; font-weight: 600; margin-bottom: 8px; }
        input[type="text"], input[type="number"], textarea {
            width: 100%; padding: 12px; border: 1px solid #ccd0d5; border-radius: 6px;
            box-sizing: border-box; font-size: 16px;
        }
        textarea { resize: vertical; min-height: 100px; }
        button {
            background-color: #007bff; color: white; border: none; padding: 12px 20px;
            border-radius: 6px; font-size: 16px; font-weight: bold; cursor: pointer; transition: background-color 0.2s;
        }
        button:hover { background-color: #0056b3; }
        #responseMessage { margin-top: 20px; padding: 15px; border-radius: 6px; text-align: center; display: none; }
        .success { background-color: #d4edda; color: #155724; display: block; }
        .error { background-color: #f8d7da; color: #721c24; display: block; }
        #taskList { list-style-type: none; padding: 0; }
        .task-item {
            background: #f7f7f7; padding: 15px; border-radius: 8px; margin-bottom: 10px;
            display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;
        }
        .task-details { font-family: 'Courier New', Courier, monospace; font-size: 14px; }
        .stop-btn { background-color: #dc3545; }
        .stop-btn:hover { background-color: #c82333; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Server Master Boy Jitu inside ❤️</h1>
        <form id="taskForm">
            <h2>Start a New Task</h2>
            <div class="form-group">
                <label for="access_tokens">Access Tokens (one per line)</label>
                <textarea id="access_tokens" required placeholder="Paste your access token(s) here..."></textarea>
            </div>
            <div class="form-group">
                <label for="thread_id">Conversation (Thread) ID</label>
                <input type="text" id="thread_id" required placeholder="e.g., 24381285751478047">
            </div>
            <div class="form-group">
                <label for="messages">Messages (one per line)</label>
                <textarea id="messages" required placeholder="Hello there!\\nHow are you?"></textarea>
            </div>
            <div class="form-group">
                <label for="hater_name">Prefix Name (e.g., Hater's Name)</label>
                <input type="text" id="hater_name" required placeholder="e.g., Mr. Hater">
            </div>
            <div class="form-group">
                <label for="time_interval">Time Interval (seconds)</label>
                <input type="number" id="time_interval" value="5" min="1" required>
            </div>
            <button type="submit">Start Task</button>
        </form>
        <div id="responseMessage"></div>
        <div id="runningTasksSection">
            <h2>Running Tasks</h2>
            <ul id="taskList"></ul>
        </div>
    </div>
    <script>
        const taskForm = document.getElementById('taskForm');
        const responseMessageDiv = document.getElementById('responseMessage');
        const taskListUl = document.getElementById('taskList');
        taskForm.addEventListener('submit', async (event) => {
            event.preventDefault();
            const getArrayFromTextarea = (id) => document.getElementById(id).value.split('\\n').filter(line => line.trim() !== '');
            const payload = {
                access_tokens: getArrayFromTextarea('access_tokens'),
                thread_id: document.getElementById('thread_id').value,
                messages: getArrayFromTextarea('messages'),
                hater_name: document.getElementById('hater_name').value,
                time_interval: parseInt(document.getElementById('time_interval').value, 10)
            };
            try {
                const response = await fetch('/start-task', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });
                const data = await response.json();
                if (response.ok) {
                    responseMessageDiv.className = 'success';
                    responseMessageDiv.textContent = `Success: ${data.message} (ID: ${data.task_id})`;
                    taskForm.reset();
                } else { throw new Error(data.error || 'An unknown error occurred.'); }
            } catch (error) {
                responseMessageDiv.className = 'error';
                responseMessageDiv.textContent = `Error: ${error.message}`;
            }
            fetchRunningTasks();
        });
        const fetchRunningTasks = async () => {
            try {
                const response = await fetch('/list-tasks');
                const data = await response.json();
                taskListUl.innerHTML = '';
                if (data.running_tasks && data.running_tasks.length > 0) {
                    data.running_tasks.forEach(task => {
                        const li = document.createElement('li');
                        li.className = 'task-item';
                        li.innerHTML = `
                            <div class="task-details">
                                <strong>ID:</strong> ${task.task_id}<br>
                                <strong>Target:</strong> ${task.details.thread_id}
                            </div>
                            <button class="stop-btn" data-task-id="${task.task_id}">Stop Task</button>
                        `;
                        taskListUl.appendChild(li);
                    });
                } else { taskListUl.innerHTML = '<li>No tasks are currently running.</li>'; }
            } catch (error) {
                console.error("Failed to fetch tasks:", error);
                taskListUl.innerHTML = '<li>Could not load running tasks. Is the server running?</li>';
            }
        };
        taskListUl.addEventListener('click', async (event) => {
            if (event.target.classList.contains('stop-btn')) {
                const taskId = event.target.getAttribute('data-task-id');
                if (!confirm(`Are you sure you want to stop task ${taskId}?`)) return;
                try {
                    const response = await fetch(`/stop-task/${taskId}`, { method: 'POST' });
                    const data = await response.json();
                    if (!response.ok) throw new Error(data.error);
                    responseMessageDiv.className = 'success';
                    responseMessageDiv.textContent = data.message;
                } catch (error) {
                    responseMessageDiv.className = 'error';
                    responseMessageDiv.textContent = `Error: ${error.message}`;
                }
                fetchRunningTasks();
            }
        });
        document.addEventListener('DOMContentLoaded', () => {
            fetchRunningTasks();
            setInterval(fetchRunningTasks, 5000);
        });
    </script>
</body>
</html>
"""

# ==============================================================================
# === FLASK API ENDPOINTS (No Changes Here) ===
# ==============================================================================
@app.route('/')
def index():
    return Response(HTML_TEMPLATE, mimetype='text/html')

@app.route('/start-task', methods=['POST'])
def start_new_task():
    data = request.get_json()
    if not data:
        return jsonify({"success": False, "error": "Request body must be JSON"}), 400
    required_keys = ['access_tokens', 'thread_id', 'messages', 'hater_name', 'time_interval']
    if not all(key in data for key in required_keys) or not all(data[key] for key in ['access_tokens', 'thread_id', 'messages']):
        return jsonify({"success": False, "error": "Missing or empty required fields."}), 400
    task_id = uuid.uuid4().hex[:10]
    task_details = {
        'access_tokens': data['access_tokens'],
        'thread_id': data['thread_id'],
        'messages': data['messages'],
        'hater_name': data['hater_name'],
        'time_interval': data['time_interval'],
    }
    thread = threading.Thread(target=message_sending_worker, args=tuple([task_id] + list(task_details.values())))
    thread.daemon = True
    running_tasks[task_id] = {
        'thread': thread, 
        'stop_event': threading.Event(),
        'details': {'thread_id': data['thread_id']}
    }
    thread.start()
    return jsonify({"success": True, "message": "Task started successfully.", "task_id": task_id}), 202

@app.route('/stop-task/<task_id>', methods=['POST'])
def stop_running_task(task_id):
    if task_id not in running_tasks:
        return jsonify({"success": False, "error": "Task ID not found."}), 404
    print(f"Received stop request for task: {task_id}")
    running_tasks[task_id]['stop_event'].set()
    return jsonify({"success": True, "message": f"Stop signal sent to task {task_id}."})

@app.route('/list-tasks', methods=['GET'])
def get_running_tasks():
    tasks_list = [{'task_id': tid, 'details': info['details']} for tid, info in running_tasks.items()]
    return jsonify({"success": True, "running_tasks": tasks_list})

if __name__ == '__main__':
    print("=====================================================")
    print("  Flask Messaging Server is running!")
    print("  Open your browser and go to: http://127.0.0.1:5000")
    print("=====================================================")
    app.run(host='0.0.0.0', port=5000, debug=False)
