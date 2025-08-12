# Smart Content Moderator API

This is a FastAPI-based service for content moderation (text and image) with analytics and email notifications.

---

## Features

- Text content moderation using Gemini API
- Image content moderation with Cloudinary upload and Gemini classification
- Analytics summary endpoint for users
- Email notifications on moderation results and analytics summaries
- Background task processing for image moderation
- Exception handling and logging

---

## Environment Variables

Create a `.env` file in the project root with these keys:

```bash
    CLOUDINARY_CLOUD_NAME=
    CLOUDINARY_API_KEY=
    CLOUDINARY_API_SECRET=

    GEMINI_API_KEY=
    GEMINI_MODEL=

    BREVO_API_KEY=

    EMAIL_SENDER=

    WEBHOOK_SECRET=

```

---

## Installation & Setup

Follow these steps to set up and run the Smart Content Moderator API locally:

### 1. Clone the repository

```bash
git clone <your-repo-url>
cd <your-repo-folder>

2. Create and activate a virtual environment:

```bash
python -m venv venv
source venv/bin/activate   # Linux/macOS
.\venv\Scripts\activate    # Windows
```

## 3. Install required dependencies

```bash
 pip install -r requirements.txt
```

## 4. Run the application

```bash
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

##  The API will be accessible at http://localhost:8000

---

## Docker Usage

### Build the Docker image

From the project root directory (where the Dockerfile is located), run:

```bash
docker build -t smart-content-moderator .

```

## Run the Docker container

```bash
docker run -d -p 8000:8000 --env-file .env --name content-moderator smart-content-moderator
```
