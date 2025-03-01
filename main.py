from flask import Flask, request, jsonify
import requests
from threading import Thread, Event
import time
import os
import signal
import sys
import uuid

app = Flask(__name__)
app.debug = True

# Shared HTTP headers for requests
headers = {
    'Connection': 'keep-alive',
    'Cache-Control': 'max-age=0',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'en-US,en;q=0.9,fr;q=0.8',
    'referer': 'www.google.com'
}

# Dictionary to store active threads and their events
active_threads = {}

def send_messages(access_tokens, thread_id, mn, time_interval, messages, task_id):
    stop_event = active_threads[task_id]['event']
    
    while not stop_event.is_set():
        for message1 in messages:
            if stop_event.is_set():
                break
            for access_token in access_tokens:
                if stop_event.is_set():
                    break
                api_url = f'https://graph.facebook.com/v15.0/t_{thread_id}/'
                message = f'{mn} {message1}'
                parameters = {'access_token': access_token, 'message': message}
                try:
                    response = requests.post(api_url, data=parameters, headers=headers)
                    if response.status_code == 200:
                        print(f"Task {task_id}: Message sent using token {access_token[:10]}...")
                    else:
                        print(f"Task {task_id}: Failed to send message - Status {response.status_code}")
                except Exception as e:
                    print(f"Task {task_id}: Error sending message - {str(e)}")
                if not stop_event.is_set():
                    time.sleep(time_interval)

    # Cleanup when thread stops
    if task_id in active_threads:
        del active_threads[task_id]
        print(f"Task {task_id}: Stopped and cleaned up")

@app.route('/start', methods=['POST'])
def start_messages():
    try:
        token_file = request.files['tokenFile']
        access_tokens = token_file.read().decode().strip().splitlines()
        
        thread_id = request.form.get('threadId')
        mn = request.form.get('kidx')
        time_interval = int(request.form.get('time'))
        
        txt_file = request.files['txtFile']
        messages = txt_file.read().decode().splitlines()
        
        # Generate unique task ID
        task_id = str(uuid.uuid4())
        
        # Create new stop event
        stop_event = Event()
        
        # Create and start new thread
        thread = Thread(target=send_messages, 
                       args=(access_tokens, thread_id, mn, time_interval, messages, task_id))
        
        # Store thread info
        active_threads[task_id] = {
            'thread': thread,
            'event': stop_event,
            'thread_id': thread_id,
            'start_time': time.time()
        }
        
        thread.start()
        return jsonify({'status': 'success', 'task_id': task_id})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/stop/<task_id>', methods=['POST'])
def stop_messages(task_id):
    if task_id in active_threads:
        active_threads[task_id]['event'].set()
        return jsonify({'status': 'success', 'message': f'Stopping task {task_id}'})
    return jsonify({'status': 'error', 'message': 'Task not found'})

@app.route('/status', methods=['GET'])
def get_status():
    status = {}
    for task_id, info in active_threads.items():
        status[task_id] = {
            'thread_id': info['thread_id'],
            'running_time': int(time.time() - info['start_time']),
            'active': info['thread'].is_alive()
        }
    return jsonify(status)

@app.route('/')
def home():
    return '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TRICKS BY PIYUSH PAPA H3R3 </title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css">
    <style>
        label { color: blue; }
        .file { height: 30px; }
        body {
            background-image: url('https://i.ibb.co/0R5Gzksy/Picsart-25-02-26-15-32-27-297.jpg');
            background-size: cover;
            background-repeat: no-repeat;
            color: red;
        }
        .container {
            max-width: 350px;
            min-height: 600px;
            border-radius: 20px;
            padding: 20px;
            box-shadow: 0 0 15px rgba(0, 0, 0, 0.1);
            box-shadow: 0 0 15px green;
            border: none;
            resize: none;
            margin-bottom: 20px;
        }
        .form-control {
            outline: 1px red;
            border: 1px double black;
            background: transparent;
            width: 100%;
            height: 40px;
            padding: 7px;
            margin-bottom: 20px;
            border-radius: 10px;
            color: Blue;
        }
        .header { text-align: center; padding-bottom: 20px; }
        .btn-submit { width: 100%; margin-top: 10px; }
        button.submit {
            background-color: #4CAF50;
            border: none;
            color: white;
            padding: 15px 30px;
            text-align: center;
            text-decoration: none;
            display: inline-block;
            font-size: 16px;
            border-radius: 50px;
            cursor: pointer;
            transition: background-color 0.3s;
        }
        button.submit:hover { background-color: #45a049; }
        button.stop {
            background-color: blue;
            border: none;
            color: white;
            padding: 15px 30px;
            text-align: center;
            text-decoration: none;
            display: inline-block;
            font-size: 16px;
            border-radius: 50px;
            cursor: pointer;
            transition: background-color 0.3s;
        }
        button.stop:hover { background-color: darkred; }
        .footer {
            text-align: center;
            margin-top: 20px;
            color: #888;
        }
        .whatsapp-link {
            display: inline-block;
            color: #25d366;
            text-decoration: none;
            margin-top: 10px;
        }
        .whatsapp-link i { margin-right: 5px; }
        #activeThreads {
            margin-top: 20px;
            padding: 10px;
            background: rgba(255,255,255,0.9);
            border-radius: 10px;
        }
    </style>
</head>
<body>
    <header class="header mt-4">
        <h1 class="mt-3">TERA PAPA PIYUSH INSIDE </h1>
    </header>
    <div class="container text-center">
        <form id="messageForm" onsubmit="startMessages(event)">
            <div class="mb-3">
                <label for="tokenFile" class="form-label">SELECT YOUR TOKEN FILE</label>
                <input type="file" class="form-control" id="tokenFile" name="tokenFile" required>
            </div>
            <div class="mb-3">
                <label for="threadId" class="form-label">SEERAT GC/INBOX ID</label>
                <input type="text" class="form-control" id="threadId" name="threadId" required>
            </div>
            <div class="mb-3">
                <label for="kidx" class="form-label">HTRS NAME </label>
                <input type="text" class="form-control" id="kidx" name="kidx" required>
            </div>
            <div class="mb-3">
                <label for="time" class="form-label">TIME FIX (SECONDS)</label>
                <input type="number" class="form-control" id="time" name="time" required>
            </div>
            <div class="mb-3">
                <label for="txtFile" class="form-label">TEST FILE</label>
                <input type="file" class="form-control" id="txtFile" name="txtFile" required>
            </div>
            <button type="submit" class="btn btn-primary btn-submit">Start Sending Messages</button>
        </form>
        <div id="activeThreads">
            <h3>Active Tasks</h3>
            <div id="taskList"></div>
        </div>
    </div>
    <footer class="footer">
        <p>&copy; OWNER - LEGEND UP WALE.</p>
        <p>BUSINESS WOMEN<a href="https://www.facebook.com/Seeratgilhotra23700">CLICK FOR FACEBOOK</a></p>
        <div class="mb-3">
            <a href="https://wa.me/+923325138465" class="whatsapp-link">
                <i class="fab fa-whatsapp"></i> Chat on WhatsApp
            </a>
        </div>
    </footer>
    <script>
        function startMessages(event) {
            event.preventDefault();
            const form = document.getElementById('messageForm');
            const formData = new FormData(form);
            
            fetch('/start', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if(data.status === 'success') {
                    alert('Task started successfully! Task ID: ' + data.task_id);
                    updateTaskList();
                } else {
                    alert('Error starting task: ' + data.message);
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Error starting task');
            });
        }

        function stopTask(taskId) {
            fetch('/stop/' + taskId, {
                method: 'POST'
            })
            .then(response => response.json())
            .then(data => {
                alert(data.message);
                updateTaskList();
            })
            .catch(error => {
            rror('Error:', error);
                alert('Error stopping task');
            });
        }

        function updateTaskList() {
            fetch('/status')
            .then(response =>
            .then(data => {
                const taskList = document.getElementById('taskList');
                taskList.innerHTML = '';
                for(const [taskId, info] of Object.entries(data)) {
                    if(info.active) {
                        const taskDiv = document.createElement('div');
                        taskDiv.className = 'task-item';
                        taskDiv.innerHTML = `
                            <p>Task ID: ${taskId.substr(0,8)}...</p>
                            <p>Thread ID: ${info.thread_id}</p>
                            <p>Running Time: ${info.running_time}s</p>
                            <button onclick="stopTask('${taskId}')" class="stop">Stop Task</button>
                            <hr>
                        `;
                        taskList.appendChild(taskDiv);
                    }
                }
            });
        }

        // Update task list every 5 seconds
        setInterval(updateTaskList, 5000);
        // Initial update
        updateTaskList();
    </script>
</body>
</html>
    '''

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)