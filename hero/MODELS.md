# Models Documentation

This document describes the Django models used in the Hero app.

## Overview

The Hero app contains two main models for managing contact messages and project portfolio items.

---

## Contact Model

The `Contact` model stores contact form submissions from visitors.

### Fields

| Field | Type | Options | Description |
|-------|------|---------|-------------|
| `name` | CharField | max_length=200 | Contact person's full name |
| `email` | EmailField | - | Contact person's email address |
| `phone` | CharField | max_length=50, blank=True | Contact person's phone number (optional) |
| `message` | TextField | - | The contact message content |
| `created_at` | DateTimeField | auto_now_add=True | Timestamp when the message was received |

### Meta Options

- **verbose_name**: Contact
- **verbose_name_plural**: Contacts

### Methods

- `__str__()`: Returns a string representation in the format `"Name <email>"`

### Usage

```python
contact = Contact.objects.create(
    name="John Doe",
    email="john@example.com",
    phone="123-456-7890",
    message="I'm interested in your services."
)
```

---

## Project Model

The `Project` model stores portfolio projects with details and metadata.

### Fields

| Field | Type | Options | Description |
|-------|------|---------|-------------|
| `title` | CharField | max_length=200 | Project title/name |
| `description` | TextField | blank=True | Detailed project description |
| `image` | ImageField | upload_to='projects/', blank=True, null=True | Project showcase image |
| `repo_url` | URLField | blank=True | URL to project repository (GitHub, etc.) |
| `created_at` | DateTimeField | auto_now_add=True | Timestamp when the project was added |

### Meta Options

- **verbose_name**: Project
- **verbose_name_plural**: Projects

### Methods

- `__str__()`: Returns the project title

### Usage

```python
project = Project.objects.create(
    title="E-commerce Website",
    description="A fully responsive e-commerce platform built with Django.",
    repo_url="https://github.com/user/project",
    image=image_file
)
```

---

## Database Relationships

- **Contact** → One-directional (no foreign keys)
- **Project** → One-directional (no foreign keys)

Both models are independent and don't have relationships with each other.

---

## Admin Panel

Both models are registered with the Django admin panel for easy management through the admin interface.

- Access the admin panel at `/admin/`
- Manage contacts and projects directly through the web interface
- All fields are displayed with automatic form generation based on field types
