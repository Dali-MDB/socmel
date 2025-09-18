# SocMel Backend (FastAPI)

SocMel is a social platform that blends the best of Instagram and Discord. Users can create posts on their personal timeline or inside community spaces, chat in real-time via DMs, group chats, and space rooms, and grow their networks via follows and invitations. This repository contains the backend service implemented with FastAPI, SQLAlchemy, and WebSockets.

## What this project is about

- A social feed of posts from users you follow and spaces you belong to
- Spaces (like Discord servers) that contain Rooms for topical conversations and posts
- Real-time messaging with DMs, group chats, and space room chats
- Follow system with approval workflow (pending/accept/reject)
- Media handling (Cloudinary) for profile pictures and post attachments
- Background jobs for periodic cleanup (notes and orphan attachments)
- Basic account security flows (email/password change with verification codes)

## Core Features

- Posts
  - Create posts to your own profile or to a Space
  - Like, comment, reply, and react to comments
  - Upload/delete post images (Cloudinary)
  - Privacy groundwork in place; more privacy controls planned
- Spaces and Rooms
  - Create, edit, delete Spaces (owner-managed)
  - Invite and admit members via expirable, limited-use invitation tokens
  - Create, edit, delete Rooms within a Space
  - Members-only post feeds and room messaging
- Messaging
  - WebSocket-based real-time messaging
  - Direct messages (DMs) between users
  - Group chat with membership management
  - Space room messages delivered to all online members
  - Fetch message history for DMs, group chats, and space rooms
- Social Graph
  - Follow requests with pending state, accept/reject, unfollow, and remove follower
  - Personalized feed from followed users and joined spaces
- Users & Profiles
  - Register, login (OAuth2 password flow), view/edit profile
  - Upload/replace/remove profile pictures (Cloudinary)
- Security
  - Verification codes for changing email/password
  - JWT-based auth with middleware that enriches requests with auth context
- Background Tasks
  - APScheduler jobs: hourly notes cleanup and daily orphan attachment cleanup

## Architecture Overview

- FastAPI app composed of modular routers under `app/manage` and `app/authentication.py`
- SQLAlchemy models under `app/models` with Alembic migrations in `alembic/`
- Pydantic schemas for request/response validation under `app/schemas`
- WebSockets for real-time messaging, orchestrated by `AdvancedConnectionManager`
- Cloudinary integration for media storage
- APScheduler for periodic maintenance jobs
- Rate limiting via SlowAPI

### Key Components

- `main.py`
  - App factory with lifespan context: starts/stops APScheduler
  - Registers routers: auth, posts, spaces, users, security, follows, messages, groups, notes
  - SlowAPI middleware and limiter
  - Auth middleware attaches `request.state.is_authenticated` and `request.state.cur_user`
- `app/manage/connection_manager.py`
  - `AdvancedConnectionManager` maintains active websockets, group and space membership maps
  - Methods to broadcast messages to groups and spaces, and direct send to a user
- `app/manage/direct_messaging.py`
  - `/messages/ws` WebSocket endpoint taking `token` query param
  - Persists DMs, group, and room messages; broadcasts via connection manager
  - REST endpoints to fetch history per DM, group, or room
- `app/manage/groups_manage.py`
  - Create/view/manage group chats; membership add/remove/leave; transfer ownership
- `app/manage/spaces_manage.py`
  - Create/edit/delete spaces; room CRUD; invitation creation and join flow
  - Space membership management; broadcasts membership changes to WebSocket manager
- `app/manage/posts_manage.py`
  - Post CRUD for user and space posts; likes; comments and replies; reactions
  - Post feed: unauthenticated global feed, authenticated personalized feed
  - Post attachments upload/delete (Cloudinary)
- `app/manage/users_manage.py`
  - View/edit profile, upload/remove profile picture
- `app/manage/follows_manage.py`
  - Follow requests, accept/reject, cancel, unfollow, remove follower
- `app/manage/security_manage.py`
  - Verification code issuance; change/reset email/password flows
- `app/tasks/tasks.py`
  - APScheduler jobs: hourly `clean_notes`, daily `clean_orphan_post_attachments`

## Data Model (high level)

- Users, Follows
- Posts, Comments, Reactions, PostAttachment
- Spaces, Rooms, SpaceInvitation
- Messages: `DmMessage`, `GroupChat`, `GroupChatMessage`, `RoomMessage`
- Notes (temporary), Security: `EmailVerificationCode`

Check `app/models/` and `alembic/versions/` for exact fields and migrations.

## Real-time Messaging

- Connect to `/messages/ws?token=...` after obtaining an access token
- On connect, the server registers your group memberships and can broadcast
- Message payload types:
  - `{ "type": "dm", "receiver_id": int, "message": str }`
  - `{ "type": "group", "group_id": int, "message": str, "parent_id"?: int }`
  - `{ "type": "space", "space_id": int, "room_id": int, "message": str, "parent_id"?: int }`
- Server persists messages, then emits typed JSON to recipients; timestamps are ISO strings
- History endpoints:
  - `GET /messages/history/dm/{receiver_id}/`
  - `GET /messages/history/group/{group_id}/`
  - `GET /messages/history/space/{space_id}/room/{room_id}/`

## API Overview (selected)

- Auth: `POST /auth/register/`, `POST /auth/login/`, `GET /auth/current_user/`
- Users: `GET /users/me/`, `PUT /users/me/`, `POST /users/pfp/`, `DELETE /users/pfp/`
- Posts: CRUD, likes, comments, reactions, feeds under `/posts/...`
- Spaces: CRUD, rooms CRUD, invitations, membership under `/spaces/...`
- Groups: create/manage under `/groups/...`
- Messaging: WebSocket `/messages/ws` and history endpoints
- Follows: requests/accept/reject/following/followers under `/follows/...`
- Security: verification codes, change email/password under `/security/...`

Use an OpenAPI viewer (FastAPI docs) at `/docs` for full endpoint details.

## Setup & Run

### Prerequisites
- Python 3.11+
- FastApi
- PostgreSQL (or compatible DB supported by SQLAlchemy URL)
- Cloudinary account (for media)

### Environment variables
Create a `.env` in the backend root with:

```
DATABASE_URL=postgresql+psycopg2://user:pass@host:5432/db
SECRET_KEY=your-secret
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRES_MINUTES=...
CLOUD_NAME=...
API_KEY=...
API_SECRET=...
```

### Install and run

```bash
python -m venv .venv
. .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
alembic upgrade head
uvicorn main:app --reload
```

The app starts APScheduler automatically via FastAPI lifespan.

## Rate Limiting

- SlowAPI is configured with a key function that uses user ID if authenticated, otherwise client IP.
- Example test endpoint: `GET /limit` limited to `2/minute`.

## Background Jobs

- `clean_notes`: deletes Notes older than 24 hours (hourly)
- `clean_orphan_post_attachments`: deletes attachments without a post (daily)

## Roadmap

- Message attachments (images/files) in DMs, groups, and space rooms
- Post privacy controls (followers-only, space-role-only, custom lists)
- Richer notifications and presence indicators
- Search across users, posts, spaces, and messages
- Moderation tools for space owners

## Contributing

- Use feature branches and open PRs
- Keep code readable and typed where applicable
- Add/adjust Alembic migrations for schema changes

## License
