# AgileTrack – Django Task Tracker

A full-stack agile-style task management app built with Django + SQLite.

## Features
- **User Authentication** – Register, Login, Logout
- **Role-Based Access** – Admin, Manager, Developer roles
- **Projects** – Create projects, add team members, track progress
- **Tasks** – Full CRUD with status tracking (To Do → In Progress → Done)
- **Kanban Board** – Visual board view with column filters
- **Deadlines** – Set deadlines, overdue highlighting
- **Comments** – Add comments on any task
- **Dashboard** – Stats overview, my tasks, active projects

## Quick Setup

```bash
# 1. Install Django
pip install -r requirements.txt

# 2. Run migrations
python manage.py makemigrations accounts
python manage.py makemigrations projects
python manage.py makemigrations tasks
python manage.py migrate

# 3. Create a superuser (Admin)
python manage.py createsuperuser

# 4. Start the server
python manage.py runserver

# 5. Open in browser
# http://127.0.0.1:8000
```

## Project Structure
```
tasktracker/
├── config/           # Django settings & URL config
├── accounts/         # Custom User model, auth, roles
├── projects/         # Project CRUD + team management
├── tasks/            # Task CRUD + comments + kanban
├── templates/        # All HTML templates
│   ├── base.html
│   ├── dashboard/
│   ├── tasks/
│   ├── projects/
│   └── accounts/
├── static/
│   ├── css/style.css
│   └── js/app.js
├── manage.py
└── requirements.txt
```

## Roles & Permissions

| Action              | Developer | Manager | Admin |
|---------------------|-----------|---------|-------|
| View own tasks      | ✅        | ✅      | ✅    |
| Create tasks        | ✅        | ✅      | ✅    |
| View all tasks      | ❌        | ✅      | ✅    |
| Create projects     | ❌        | ✅      | ✅    |
| Edit projects       | ❌        | ✅      | ✅    |
| Delete projects     | ❌        | ❌      | ✅    |
| View team           | ❌        | ✅      | ✅    |
| Django admin panel  | ❌        | ❌      | ✅*   |

*Superuser only

## Default URLs
- `/` → Dashboard
- `/accounts/login/` → Login
- `/accounts/register/` → Register
- `/dashboard/tasks/` → Task List
- `/dashboard/tasks/kanban/` → Kanban Board
- `/projects/` → Projects
- `/admin/` → Django Admin
