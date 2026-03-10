# ProjectNexus - Project Management SaaS Platform

A comprehensive, production-grade project management platform inspired by Jira and Asana. Built for teams that need powerful project tracking with Kanban boards, Scrum sprints, time tracking, Gantt charts, and real-time collaboration.

## Features

- **Workspaces** - Multi-tenant workspace isolation with role-based access control
- **Kanban Boards** - Drag-and-drop task management with customizable columns
- **Scrum Sprints** - Full sprint lifecycle management with backlog grooming
- **Backlog Management** - Prioritized product backlog with drag-and-drop reordering
- **Time Tracking** - Built-in time logging per task with reports and summaries
- **Gantt Charts** - Interactive project timeline visualization with dependencies
- **Burndown Charts** - Sprint progress tracking with ideal vs actual burndown
- **Velocity Charts** - Team velocity measurement across sprints
- **Real-time Collaboration** - WebSocket-powered live updates across all connected clients
- **File Attachments** - Drag-and-drop file uploads on tasks
- **Comments & Activity** - Threaded task comments with full activity history
- **Notifications** - In-app and real-time notifications for task assignments, mentions, and updates
- **Project Analytics** - Comprehensive dashboards with cycle time, throughput, and distribution metrics
- **Labels & Priorities** - Customizable labels and priority levels for task categorization

## Tech Stack

### Backend
- **Django 5.0** - Web framework
- **Django REST Framework** - API layer
- **Django Channels** - WebSocket support for real-time features
- **Celery** - Asynchronous task processing
- **PostgreSQL** - Primary database
- **Redis** - Caching, Celery broker, and WebSocket channel layer

### Frontend
- **React 18** - UI framework
- **Redux Toolkit** - State management
- **React Router v6** - Client-side routing
- **Recharts** - Chart and graph visualizations
- **React Beautiful DnD** - Drag-and-drop functionality
- **Axios** - HTTP client

### Infrastructure
- **Docker & Docker Compose** - Containerization
- **Nginx** - Reverse proxy and static file serving
- **Gunicorn** - WSGI HTTP server
- **Daphne** - ASGI server for WebSocket connections

## Architecture

```
                    +-------------+
                    |    Nginx    |
                    |  (Reverse   |
                    |   Proxy)    |
                    +------+------+
                           |
              +------------+------------+
              |                         |
       +------+------+          +------+------+
       |   React     |          |   Django    |
       |  Frontend   |          |   Backend   |
       |  (Static)   |          |  (Gunicorn) |
       +-------------+          +------+------+
                                       |
                          +------------+------------+
                          |            |            |
                   +------+---+  +----+----+  +----+----+
                   |PostgreSQL|  |  Redis  |  | Celery  |
                   +----------+  +---------+  +---------+
```

## Getting Started

### Prerequisites

- Docker and Docker Compose installed
- Git

### Quick Start

1. Clone the repository:
```bash
git clone https://github.com/your-org/projectnexus.git
cd projectnexus
```

2. Copy the environment file and configure:
```bash
cp .env.example .env
# Edit .env with your settings
```

3. Build and start all services:
```bash
docker-compose up --build
```

4. Run database migrations:
```bash
docker-compose exec backend python manage.py migrate
```

5. Create a superuser:
```bash
docker-compose exec backend python manage.py createsuperuser
```

6. Access the application:
   - Frontend: http://localhost
   - Backend API: http://localhost/api/
   - Admin Panel: http://localhost/admin/
   - API Documentation: http://localhost/api/docs/

### Local Development (without Docker)

#### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

#### Frontend
```bash
cd frontend
npm install
npm start
```

#### Celery Worker
```bash
cd backend
celery -A config worker -l info
```

## API Endpoints

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register/` | Register a new account |
| POST | `/api/auth/login/` | Login and receive JWT tokens |
| POST | `/api/auth/token/refresh/` | Refresh access token |
| GET | `/api/auth/me/` | Get current user profile |

### Workspaces
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/workspaces/` | List user workspaces |
| POST | `/api/workspaces/` | Create a workspace |
| GET | `/api/workspaces/:id/` | Workspace details |
| POST | `/api/workspaces/:id/invite/` | Invite a member |

### Projects
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/projects/` | List projects in workspace |
| POST | `/api/projects/` | Create a project |
| GET | `/api/projects/:id/` | Project details |
| GET | `/api/projects/:id/board/` | Get project board |

### Tasks
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/tasks/` | List tasks (filterable) |
| POST | `/api/tasks/` | Create a task |
| PATCH | `/api/tasks/:id/` | Update a task |
| POST | `/api/tasks/:id/move/` | Move task between columns |
| POST | `/api/tasks/:id/comments/` | Add a comment |
| POST | `/api/tasks/:id/attachments/` | Upload an attachment |

### Sprints
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/sprints/` | List sprints |
| POST | `/api/sprints/` | Create a sprint |
| POST | `/api/sprints/:id/start/` | Start a sprint |
| POST | `/api/sprints/:id/complete/` | Complete a sprint |

### Time Tracking
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/time/entries/` | Log a time entry |
| GET | `/api/time/entries/` | List time entries |
| GET | `/api/time/reports/` | Get time reports |

### Analytics
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/analytics/burndown/:sprint_id/` | Sprint burndown data |
| GET | `/api/analytics/velocity/:project_id/` | Velocity chart data |
| GET | `/api/analytics/dashboard/:project_id/` | Project dashboard metrics |

## WebSocket Events

Connect to `ws://localhost/ws/tasks/<project_id>/` for real-time task updates:

- `task.created` - New task created
- `task.updated` - Task fields updated
- `task.moved` - Task moved between columns
- `task.deleted` - Task removed
- `comment.added` - New comment on a task

Connect to `ws://localhost/ws/notifications/` for user notifications:

- `notification.new` - New notification received
- `notification.read` - Notification marked as read

## Environment Variables

See `.env.example` for the full list of configurable environment variables.

## Testing

```bash
# Run backend tests
docker-compose exec backend python manage.py test

# Run frontend tests
docker-compose exec frontend npm test
```

## Deployment

For production deployment:

1. Set `DJANGO_SETTINGS_MODULE=config.settings.production` in your environment
2. Configure a production PostgreSQL database
3. Set up Redis for caching and Celery
4. Configure proper `SECRET_KEY` and `ALLOWED_HOSTS`
5. Enable HTTPS via Nginx or a load balancer
6. Set `DEBUG=False`

## License

This project is licensed under the MIT License. See the LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request
