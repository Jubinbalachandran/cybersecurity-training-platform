"""
Cybersecurity Awareness Training Platform
=========================================

A comprehensive platform for managing cybersecurity training modules, 
tracking user progress, and generating security reports.

Features:
- Training module management
- User progress tracking
- Security reporting
- Local SQLite database
- Web-based interface using Flask
"""

import os
import sqlite3
from datetime import datetime
from flask import Flask, render_template_string, jsonify

# Initialize Flask app
app = Flask(__name__)

# Database setup
DB_NAME = 'cybersecurity_training.db'

def init_db():
    """Initialize the database with required tables"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Create training modules table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS modules (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            duration INTEGER,
            category TEXT,
            content TEXT
        )
    ''')
    
    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            department TEXT,
            risk_level TEXT DEFAULT 'low',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create user progress table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            module_id INTEGER,
            status TEXT DEFAULT 'not-started',
            score REAL,
            completed_at TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (module_id) REFERENCES modules (id)
        )
    ''')
    
    # Create reports table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            report_type TEXT,
            data TEXT,
            generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Insert sample data if tables are empty
    cursor.execute("SELECT COUNT(*) FROM modules")
    if cursor.fetchone()[0] == 0:
        sample_modules = [
            ("Phishing Awareness", "Learn to identify and avoid phishing attempts", 15, "Email Security", "Content for phishing awareness..."),
            ("Password Security", "Best practices for creating and managing passwords", 10, "Access Control", "Content for password security..."),
            ("Social Engineering", "Recognize and defend against social engineering tactics", 20, "Human Risk", "Content for social engineering..."),
            ("Data Protection", "Handling sensitive information securely", 25, "Data Security", "Content for data protection..."),
            ("Remote Work Security", "Secure practices for working from home", 18, "Network Security", "Content for remote work security...")
        ]
        cursor.executemany(
            "INSERT INTO modules (title, description, duration, category, content) VALUES (?, ?, ?, ?, ?)",
            sample_modules
        )
    
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        sample_users = [
            ("Alex Johnson", "alex.j@company.com", "Engineering", "low"),
            ("Maria Garcia", "maria.g@company.com", "Marketing", "high"),
            ("James Wilson", "james.w@company.com", "Sales", "medium"),
            ("Sarah Chen", "sarah.c@company.com", "HR", "low"),
            ("Robert Davis", "robert.d@company.com", "Finance", "high")
        ]
        cursor.executemany(
            "INSERT INTO users (name, email, department, risk_level) VALUES (?, ?, ?, ?)",
            sample_users
        )
    
    conn.commit()
    conn.close()

# HTML Templates as strings
BASE_TEMPLATE = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Cybersecurity Awareness Platform</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
</head>
<body class="bg-gray-100">
    <div class="flex h-screen">
        <!-- Sidebar -->
        <div class="w-64 bg-white shadow-md">
            <div class="p-4 border-b">
                <h1 class="text-xl font-bold text-blue-600 flex items-center">
                    <i class="fas fa-shield-alt mr-2"></i> CyberAware
                </h1>
            </div>
            <nav class="p-4">
                <ul class="space-y-2">
                    <li>
                        <a href="/" class="flex items-center p-2 text-gray-700 rounded hover:bg-gray-200 {{ 'bg-blue-100' if request.endpoint == 'dashboard' else '' }}">
                            <i class="fas fa-chart-bar mr-3"></i> Dashboard
                        </a>
                    </li>
                    <li>
                        <a href="/modules" class="flex items-center p-2 text-gray-700 rounded hover:bg-gray-200 {{ 'bg-blue-100' if request.endpoint == 'modules' else '' }}">
                            <i class="fas fa-book-open mr-3"></i> Training Modules
                        </a>
                    </li>
                    <li>
                        <a href="/users" class="flex items-center p-2 text-gray-700 rounded hover:bg-gray-200 {{ 'bg-blue-100' if request.endpoint == 'users' else '' }}">
                            <i class="fas fa-users mr-3"></i> Users
                        </a>
                    </li>
                    <li>
                        <a href="/reports" class="flex items-center p-2 text-gray-700 rounded hover:bg-gray-200 {{ 'bg-blue-100' if request.endpoint == 'reports' else '' }}">
                            <i class="fas fa-chart-pie mr-3"></i> Reports
                        </a>
                    </li>
                </ul>
            </nav>
        </div>

        <!-- Main Content -->
        <div class="flex-1 flex flex-col overflow-hidden">
            <!-- Header -->
            <header class="bg-white shadow">
                <div class="flex justify-between items-center p-4">
                    <h2 class="text-xl font-semibold capitalize">
                        {% if request.endpoint == 'dashboard' %}Dashboard
                        {% elif request.endpoint == 'modules' %}Training Modules
                        {% elif request.endpoint == 'users' %}User Management
                        {% elif request.endpoint == 'reports' %}Security Reports
                        {% else %}Cybersecurity Platform
                        {% endif %}
                    </h2>
                    <div class="flex items-center space-x-4">
                        <button class="p-2 rounded-full hover:bg-gray-200">
                            <i class="fas fa-bell"></i>
                        </button>
                        <button class="p-2 rounded-full hover:bg-gray-200">
                            <i class="fas fa-search"></i>
                        </button>
                        <div class="flex items-center">
                            <div class="w-8 h-8 rounded-full bg-gray-300 flex items-center justify-center">
                                <i class="fas fa-user"></i>
                            </div>
                            <span class="ml-2">Admin</span>
                        </div>
                    </div>
                </div>
            </header>

            <!-- Content -->
            <main class="flex-1 overflow-y-auto p-6">
                {% block content %}{% endblock %}
            </main>
        </div>
    </div>
</body>
</html>'''

DASHBOARD_TEMPLATE = '''{% extends "base.html" %}
{% block content %}
<div class="space-y-6">
    <!-- Stats Overview -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div class="bg-white rounded-lg shadow p-4">
            <div class="flex items-center">
                <div class="p-2 bg-blue-100 rounded-lg">
                    <i class="fas fa-users text-blue-600"></i>
                </div>
                <div class="ml-4">
                    <p class="text-sm text-gray-500">Total Users</p>
                    <p class="text-2xl font-bold">{{ total_users }}</p>
                </div>
            </div>
        </div>
        
        <div class="bg-white rounded-lg shadow p-4">
            <div class="flex items-center">
                <div class="p-2 bg-green-100 rounded-lg">
                    <i class="fas fa-book-open text-green-600"></i>
                </div>
                <div class="ml-4">
                    <p class="text-sm text-gray-500">Training Modules</p>
                    <p class="text-2xl font-bold">{{ total_modules }}</p>
                </div>
            </div>
        </div>
        
        <div class="bg-white rounded-lg shadow p-4">
            <div class="flex items-center">
                <div class="p-2 bg-yellow-100 rounded-lg">
                    <i class="fas fa-graduation-cap text-yellow-600"></i>
                </div>
                <div class="ml-4">
                    <p class="text-sm text-gray-500">Completed Trainings</p>
                    <p class="text-2xl font-bold">{{ completed_trainings }}</p>
                </div>
            </div>
        </div>
        
        <div class="bg-white rounded-lg shadow p-4">
            <div class="flex items-center">
                <div class="p-2 bg-red-100 rounded-lg">
                    <i class="fas fa-exclamation-triangle text-red-600"></i>
                </div>
                <div class="ml-4">
                    <p class="text-sm text-gray-500">High Risk Users</p>
                    <p class="text-2xl font-bold">{{ high_risk_users }}</p>
                </div>
            </div>
        </div>
    </div>

    <!-- Charts Placeholder -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div class="bg-white rounded-lg shadow p-6">
            <h3 class="text-lg font-semibold mb-4">Training Progress</h3>
            <div class="h-64 flex items-center justify-center bg-gray-100 rounded">
                <p class="text-gray-500">Training Progress Chart</p>
            </div>
        </div>
        
        <div class="bg-white rounded-lg shadow p-6">
            <h3 class="text-lg font-semibold mb-4">User Risk Distribution</h3>
            <div class="h-64 flex items-center justify-center bg-gray-100 rounded">
                <p class="text-gray-500">Risk Distribution Chart</p>
            </div>
        </div>
    </div>

    <!-- Recent Activity -->
    <div class="bg-white rounded-lg shadow">
        <div class="p-4 border-b">
            <h3 class="text-lg font-semibold">Recent Training Activity</h3>
        </div>
        <div class="p-4">
            <div class="space-y-4">
                <div class="flex items-center justify-between p-3 border rounded-lg">
                    <div class="flex items-center">
                        <div class="p-2 bg-green-100 rounded-lg">
                            <i class="fas fa-check-circle text-green-600"></i>
                        </div>
                        <div class="ml-4">
                            <p class="font-medium">Phishing Awareness</p>
                            <p class="text-sm text-gray-500">Completed by Alex Johnson</p>
                        </div>
                    </div>
                    <div class="text-sm text-gray-500">
                        2023-05-15
                    </div>
                </div>
                <div class="flex items-center justify-between p-3 border rounded-lg">
                    <div class="flex items-center">
                        <div class="p-2 bg-green-100 rounded-lg">
                            <i class="fas fa-check-circle text-green-600"></i>
                        </div>
                        <div class="ml-4">
                            <p class="font-medium">Data Protection</p>
                            <p class="text-sm text-gray-500">Completed by Sarah Chen</p>
                        </div>
                    </div>
                    <div class="text-sm text-gray-500">
                        2023-04-22
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>

<script>
// Fetch stats data and update dashboard
fetch('/api/stats')
    .then(response => response.json())
    .then(data => {
        const userEl = document.querySelector('.bg-blue-100 + div .text-2xl');
        const moduleEl = document.querySelector('.bg-green-100 + div .text-2xl');
        const trainingEl = document.querySelector('.bg-yellow-100 + div .text-2xl');
        const riskEl = document.querySelector('.bg-red-100 + div .text-2xl');
        
        if (userEl) userEl.textContent = data.total_users;
        if (moduleEl) moduleEl.textContent = data.total_modules;
        if (trainingEl) trainingEl.textContent = data.completed_trainings;
        if (riskEl) riskEl.textContent = data.high_risk_users;
    });
</script>
{% endblock %}'''

MODULES_TEMPLATE = '''{% extends "base.html" %}
{% block content %}
<div class="space-y-6">
    <div class="flex justify-between items-center">
        <h2 class="text-2xl font-bold">Training Modules</h2>
        <button class="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700">
            <i class="fas fa-plus mr-2"></i> Create Module
        </button>
    </div>
    
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6" id="modules-container">
        <!-- Modules will be loaded here -->
    </div>
</div>

<script>
// Fetch modules data and populate the page
fetch('/api/modules')
    .then(response => response.json())
    .then(modules => {
        const container = document.getElementById('modules-container');
        container.innerHTML = '';
        
        modules.forEach(module => {
            const moduleCard = document.createElement('div');
            moduleCard.className = 'bg-white rounded-lg shadow hover:shadow-md transition-shadow';
            moduleCard.innerHTML = `
                <div class="p-5">
                    <div class="flex justify-between items-start">
                        <h3 class="text-lg font-semibold">${module.title}</h3>
                        <span class="bg-gray-200 text-gray-800 text-xs px-2 py-1 rounded">Not Started</span>
                    </div>
                    <p class="text-gray-600 text-sm mt-2">${module.description}</p>
                    <div class="flex justify-between text-sm text-gray-500 mt-4">
                        <span class="flex items-center">
                            <i class="far fa-clock mr-1"></i> ${module.duration} min
                        </span>
                        <span>${module.category}</span>
                    </div>
                </div>
                <div class="px-5 py-3 bg-gray-50 border-t flex justify-between">
                    <button class="text-blue-600 hover:text-blue-800">
                        <i class="fas fa-play mr-1"></i> Preview
                    </button>
                    <button class="bg-blue-600 text-white px-3 py-1 rounded text-sm hover:bg-blue-700">
                        Assign
                    </button>
                </div>
            `;
            container.appendChild(moduleCard);
        });
    });
</script>
{% endblock %}'''

USERS_TEMPLATE = '''{% extends "base.html" %}
{% block content %}
<div class="space-y-6">
    <div class="flex justify-between items-center">
        <h2 class="text-2xl font-bold">User Management</h2>
        <button class="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700">
            <i class="fas fa-plus mr-2"></i> Add User
        </button>
    </div>
    
    <div class="bg-white rounded-lg shadow overflow-hidden">
        <table class="min-w-full divide-y divide-gray-200">
            <thead class="bg-gray-50">
                <tr>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">User</th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Department</th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Risk Level</th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
                </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200" id="users-table">
                <!-- Users will be loaded here -->
            </tbody>
        </table>
    </div>
</div>

<script>
// Fetch users data and populate the table
fetch('/api/users')
    .then(response => response.json())
    .then(users => {
        const tableBody = document.getElementById('users-table');
        tableBody.innerHTML = '';
        
        users.forEach(user => {
            const row = document.createElement('tr');
            row.className = 'hover:bg-gray-50';
            row.innerHTML = `
                <td class="px-6 py-4 whitespace-nowrap">
                    <div class="flex items-center">
                        <div class="flex-shrink-0 h-10 w-10">
                            <div class="bg-gray-200 border-2 border-dashed rounded-xl w-10 h-10"></div>
                        </div>
                        <div class="ml-4">
                            <div class="text-sm font-medium text-gray-900">${user.name}</div>
                            <div class="text-sm text-gray-500">${user.email}</div>
                        </div>
                    </div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    ${user.department}
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                    <span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full 
                        ${user.risk_level === 'high' ? 'bg-red-100 text-red-800' : 
                          user.risk_level === 'medium' ? 'bg-yellow-100 text-yellow-800' : 
                          'bg-green-100 text-green-800'}">
                        ${user.risk_level.charAt(0).toUpperCase() + user.risk_level.slice(1)} Risk
                    </span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                    <button class="text-blue-600 hover:text-blue-900">View</button>
                </td>
            `;
            tableBody.appendChild(row);
        });
    });
</script>
{% endblock %}'''

REPORTS_TEMPLATE = '''{% extends "base.html" %}
{% block content %}
<div class="space-y-6">
    <h2 class="text-2xl font-bold">Security Reports</h2>
    
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div class="bg-white rounded-lg shadow p-6">
            <h3 class="text-lg font-semibold mb-4">Phishing Simulation Results</h3>
            <div class="h-64 flex items-center justify-center bg-gray-100 rounded">
                <p class="text-gray-500">Phishing Simulation Chart</p>
            </div>
        </div>
        
        <div class="bg-white rounded-lg shadow p-6">
            <h3 class="text-lg font-semibold mb-4">Training Completion Rates</h3>
            <div class="h-64 flex items-center justify-center bg-gray-100 rounded">
                <p class="text-gray-500">Completion Rates Chart</p>
            </div>
        </div>
    </div>
    
    <div class="bg-white rounded-lg shadow">
        <div class="p-4 border-b">
            <h3 class="text-lg font-semibold">Incident Response Metrics</h3>
        </div>
        <div class="p-6">
            <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div class="border rounded-lg p-4 text-center">
                    <div class="text-3xl font-bold text-blue-600">2.4h</div>
                    <div class="text-sm text-gray-500">Avg. Detection Time</div>
                </div>
                <div class="border rounded-lg p-4 text-center">
                    <div class="text-3xl font-bold text-green-600">4.1h</div>
                    <div class="text-sm text-gray-500">Avg. Resolution Time</div>
                </div>
                <div class="border rounded-lg p-4 text-center">
                    <div class="text-3xl font-bold text-purple-600">92%</div>
                    <div class="text-sm text-gray-500">Incidents Contained</div>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}'''

# Routes
@app.route('/')
def dashboard():
    """Dashboard with overview statistics"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Get statistics
    cursor.execute("SELECT COUNT(*) FROM users")
    total_users = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM modules")
    total_modules = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM user_progress WHERE status='completed'")
    completed_trainings = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM users WHERE risk_level='high'")
    high_risk_users = cursor.fetchone()[0]
    
    conn.close()
    
    return render_template_string(DASHBOARD_TEMPLATE, 
                          total_users=total_users,
                          total_modules=total_modules,
                          completed_trainings=completed_trainings,
                          high_risk_users=high_risk_users)

@app.route('/modules')
def modules():
    """Display all training modules"""
    return render_template_string(MODULES_TEMPLATE)

@app.route('/users')
def users():
    """Display all users"""
    return render_template_string(USERS_TEMPLATE)

@app.route('/reports')
def reports():
    """Display security reports"""
    return render_template_string(REPORTS_TEMPLATE)

@app.route('/api/modules')
def api_modules():
    """API endpoint for modules data"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM modules")
    modules = cursor.fetchall()
    conn.close()
    
    # Convert to JSON-serializable format
    modules_list = []
    for module in modules:
        modules_list.append({
            'id': module[0],
            'title': module[1],
            'description': module[2],
            'duration': module[3],
            'category': module[4]
        })
    
    return jsonify(modules_list)

@app.route('/api/users')
def api_users():
    """API endpoint for users data"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    conn.close()
    
    # Convert to JSON-serializable format
    users_list = []
    for user in users:
        users_list.append({
            'id': user[0],
            'name': user[1],
            'email': user[2],
            'department': user[3],
            'risk_level': user[4]
        })
    
    return jsonify(users_list)

@app.route('/api/stats')
def api_stats():
    """API endpoint for dashboard statistics"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM users")
    total_users = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM modules")
    total_modules = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM user_progress WHERE status='completed'")
    completed_trainings = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM users WHERE risk_level='high'")
    high_risk_users = cursor.fetchone()[0]
    
    conn.close()
    
    return jsonify({
        'total_users': total_users,
        'total_modules': total_modules,
        'completed_trainings': completed_trainings,
        'high_risk_users': high_risk_users
    })

if __name__ == '__main__':
    # Initialize database
    init_db()
    
    # Run the application
    app.run(debug=True, host='0.0.0.0', port=5000)