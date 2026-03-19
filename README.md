# 📋 NextStep CRM

**A multi-user CRM with role-based access for managing companies, contacts, interactions, and follow-ups — built with Flask and Bootstrap 5.**

![Version](https://img.shields.io/badge/version-v0.26.0--beta-blue)
![Python](https://img.shields.io/badge/python-3.9%2B-green)
![Flask](https://img.shields.io/badge/flask-3.1-lightgrey)
![Licence](https://img.shields.io/badge/licence-MIT-orange)

NextStep CRM is a portfolio project that demonstrates a full-featured CRM built without any JavaScript frameworks or build tools. It covers company and contact management, interaction logging, follow-up scheduling, a cash module, an Eisenhower Matrix, a Kanban board, Google Workspace integration, file attachments, user management with RBAC, and more — all in a responsive, dark-mode-capable interface.

---

## Table of Contents

- [Screenshots](#screenshots)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Installation](#installation)
- [Project Structure](#project-structure)
- [Acknowledgements](#acknowledgements)
- [Version History](#version-history)
- [Licence](#licence)

---

## Screenshots

### Dashboard & Views

<a href="screenshots/Dashboard.png"><img src="screenshots/Dashboard.png" width="280"></a>
<a href="screenshots/Dashboard-Dark-Mode.png"><img src="screenshots/Dashboard-Dark-Mode.png" width="280"></a>
<a href="screenshots/calendar-month.png"><img src="screenshots/calendar-month.png" width="280"></a>
<a href="screenshots/calendar-week.png"><img src="screenshots/calendar-week.png" width="280"></a>
<a href="screenshots/agenda.png"><img src="screenshots/agenda.png" width="280"></a>
<a href="screenshots/quartely-overview.png"><img src="screenshots/quartely-overview.png" width="280"></a>

### Client Management

<a href="screenshots/client-dashboard.png"><img src="screenshots/client-dashboard.png" width="280"></a>
<a href="screenshots/client-dashboard2-add-quick-action.png"><img src="screenshots/client-dashboard2-add-quick-action.png" width="280"></a>
<a href="screenshots/add-client.png"><img src="screenshots/add-client.png" width="280"></a>
<a href="screenshots/interactions.png"><img src="screenshots/interactions.png" width="280"></a>
<a href="screenshots/log-interaction.png"><img src="screenshots/log-interaction.png" width="280"></a>

### Follow-ups & Productivity

<a href="screenshots/follow-ups-list-view.png"><img src="screenshots/follow-ups-list-view.png" width="280"></a>
<a href="screenshots/Follow-ups-Eisenhower-Matrix-View.png"><img src="screenshots/Follow-ups-Eisenhower-Matrix-View.png" width="280"></a>
<a href="screenshots/add-followup.png"><img src="screenshots/add-followup.png" width="280"></a>
<a href="screenshots/quick-functions.png"><img src="screenshots/quick-functions.png" width="280"></a>

### Attachments & Settings

<a href="screenshots/attachment-upload.png"><img src="screenshots/attachment-upload.png" width="280"></a>
<a href="screenshots/document-preview.png"><img src="screenshots/document-preview.png" width="280"></a>
<a href="screenshots/settings.png"><img src="screenshots/settings.png" width="280"></a>

### Mobile Responsive

<a href="screenshots/Dashboard-Dark-Mode-mobile.png"><img src="screenshots/Dashboard-Dark-Mode-mobile.png" width="140"></a>
<a href="screenshots/agenda-mobile.png"><img src="screenshots/agenda-mobile.png" width="140"></a>
<a href="screenshots/calendar-list-mobile.png"><img src="screenshots/calendar-list-mobile.png" width="140"></a>
<a href="screenshots/quartely-overview-mobile.png"><img src="screenshots/quartely-overview-mobile.png" width="140"></a>
<a href="screenshots/client-dv-mobile1.png"><img src="screenshots/client-dv-mobile1.png" width="140"></a>
<a href="screenshots/client-dv-mobile2.png"><img src="screenshots/client-dv-mobile2.png" width="140"></a>
<a href="screenshots/client-dashboard2-add-quick-action-mobile.png"><img src="screenshots/client-dashboard2-add-quick-action-mobile.png" width="140"></a>
<a href="screenshots/log-interaction-mobile.png"><img src="screenshots/log-interaction-mobile.png" width="140"></a>

---

## Features

### Core
- **Company Management** — Full CRUD with status tracking (lead, prospect, active, inactive), internal IDs, configurable list columns, and activation controls
- **Contact Management** — People linked to companies with phone, email, position, and social accounts
- **Interaction Logging** — Log phone calls, emails, meetings, and custom interaction types against each company
- **Follow-up Scheduling** — Set due dates, times, and priorities; mark tasks complete; highlight overdue items automatically
- **Cash Module** — Cash in/out transactions per company with accounts and bank payment methods
- **Cascade Delete** — Removing a company cleanly deletes all associated contacts, interactions, follow-ups, and attachments
- **Custom Fields** — Define additional company fields from Settings to capture data specific to your workflow
- **File Attachments** — Upload and manage documents on companies, contacts, and follow-ups with categories, tags, and in-browser preview

### User Management & Authentication
- **3-Role RBAC** — User (own records), Manager (all records), Admin (settings + user management)
- **Authentication** — Session-based login with Flask-Login and bcrypt password hashing
- **Ownership Filtering** — Users see only their own companies/contacts/follow-ups; managers see all
- **Record Access Control** — `can_access_record()` decorator enforces ownership
- **User CRUD** — Create, edit, toggle active/inactive, reset password, delegate and reassign records

### Google Workspace Integration
- **Google Calendar** — Bidirectional sync of follow-ups and interactions with FullCalendar event source
- **Google Meet** — Link generation via Calendar API conferenceData with "Join Meeting" buttons
- **Google Docs** — Create blank or from admin-configured templates, link/unlink to companies
- **Google Drive** — Upload to Drive, browse/link existing files, cloud icon indicators on attachments

### Data Import/Export
- **CSV Export** — Export companies, contacts, and follow-ups to CSV
- **CSV Import** — Bulk import with validation, error reporting, and downloadable error CSV
- **Templates** — Downloadable CSV templates for each entity type

### Views & Dashboards
- **Dashboard** — At-a-glance stats, today's tasks, overdue follow-ups, and recent interactions
- **Calendar** — Interactive monthly/weekly calendar powered by FullCalendar.js with colour-coded events
- **Agenda** — Daily planner view with grouped tasks and overdue highlights
- **Quarterly Overview** — Q1–Q4 strategic calendar with activity density and per-company breakdowns
- **Eisenhower Matrix** — Four-quadrant priority matrix for follow-ups (Do First / Schedule / Delegate / Eliminate)
- **Kanban Board** — Drag-and-drop pipeline board with columns per company status
- **Company Profile** — 360-degree two-column layout with sidebar stats and activity timeline

### Productivity
- **Quick Functions** — One-click company interaction logging (catalogue sent, price list sent, follow-up call, etc.) — fully configurable from Settings
- **Quick Add Panel** — Slide-over form panels with AJAX submit for creating companies, contacts, and follow-ups from any page
- **Completion-to-Outcome Flow** — Completing a follow-up prompts an optional interaction log with pre-filled context
- **Confirm-Action Modal** — Reusable confirmation pattern for destructive actions across the app

### Settings & Customisation
- **Interaction Types** — Add, edit, and delete interaction types from Settings
- **Custom Company Fields** — Define extra fields (text, URL types with icons) that appear on the company form
- **Attachment Categories & Tags** — Organise uploaded files with configurable categories and tags
- **UI Preferences** — Sticky navbar, configurable pagination (10/25/50/100 per page), back-to-top button
- **Colour Scheme** — Light, Dark, and System (follows OS preference) themes with instant switching and persistence

### UX
- **Toast Notifications** — Non-blocking success/error feedback throughout
- **Mobile Responsive** — Stacked card layout for tables on small screens, full-width offcanvas panels, mobile sidebar fix
- **AJAX Everywhere** — Status updates, quick functions, toggles, and theme switching without page reloads
- **Clickable Links** — Phone numbers and email addresses rendered as `tel:` and `mailto:` links
- **Pagination** — Configurable page sizes across all list views
- **HTTPS Support** — Optional SSL/TLS with self-signed certificates

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | Python 3.9+, Flask 3.1, Flask-SQLAlchemy 3.1, SQLAlchemy 2.0 |
| Database | SQLite (auto-created, no migrations) |
| Frontend | Jinja2, Bootstrap 5.3.3 (CDN), Bootstrap Icons 1.11.3 |
| Calendar | FullCalendar.js (CDN) |
| Drag & Drop | SortableJS (CDN) |
| Auth | Flask-Login, bcrypt (session-based, 3-role RBAC) |
| Google | google-auth, google-auth-oauthlib, google-api-python-client |
| CSRF | Flask-WTF CSRFProtect (global) |
| Build Tools | None — no npm/node, all CDN |

---

## Installation

```bash
# Clone the repository
git clone https://github.com/AmigoUK/NextStep-CRM.git
cd NextStep-CRM

# Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the application
python3 app.py
```

The app will be available at `http://localhost:5001`.

### Sample Data

To populate the database with sample users, companies, contacts, and follow-ups:

```bash
python3 seed.py
```

Default credentials: `admin` / `admin123`, `manager1` / `manager123`, `user1` / `user123`, `user2` / `user123`

---

## Project Structure

```
NextStep-CRM/
├── app.py                      # Application factory + entry point
├── config.py                   # Configuration (SECRET_KEY, DATABASE_URL)
├── extensions.py               # SQLAlchemy, CSRFProtect, LoginManager
├── seed.py                     # Sample data seeder (users, companies, contacts, follow-ups)
├── requirements.txt
├── certs/                      # SSL certificates for HTTPS (cert.pem, key.pem)
├── models/
│   ├── __init__.py             # Model exports
│   ├── company.py              # Company model (replaces old Client)
│   ├── contact.py              # Contact (person linked to company)
│   ├── interaction.py          # Interaction model (calls, emails, meetings)
│   ├── followup.py             # FollowUp model + PRIORITIES
│   ├── cash_transaction.py     # CashTransaction model (cash in/out)
│   ├── invoice.py              # Invoice model
│   ├── user.py                 # User model (username, role: user|manager|admin)
│   ├── social_account.py       # SocialAccount model
│   ├── quick_function.py       # QuickFunction model + defaults
│   ├── interaction_type.py     # InteractionType model
│   ├── custom_field.py         # CustomField model
│   ├── attachment.py           # Attachment model
│   ├── attachment_category.py  # AttachmentCategory model
│   ├── attachment_tag.py       # AttachmentTag model
│   ├── app_settings.py         # AppSettings singleton (theme, UI prefs)
│   ├── google_oauth_config.py  # GoogleOAuthConfig singleton
│   ├── google_credential.py    # GoogleCredential per-user (encrypted tokens)
│   ├── google_calendar_sync.py # GoogleCalendarSync (CRM ↔ Calendar links)
│   ├── google_doc.py           # GoogleDoc (links Docs to CRM records)
│   ├── google_drive_file.py    # GoogleDriveFile (links Drive files to records)
│   └── doc_template.py         # DocTemplate (admin-configured templates)
├── blueprints/
│   ├── auth/                   # Login, logout, rate limiting, decorators
│   ├── dashboard/              # Dashboard, calendar, agenda, quarterly
│   ├── companies/              # Company CRUD, kanban, quick actions
│   ├── contacts/               # Contact CRUD + filters
│   ├── interactions/           # Interaction CRUD
│   ├── followups/              # FollowUp CRUD, matrix, completion flow
│   ├── cash/                   # Cash in/out transactions
│   ├── orders/                 # Orders and invoice tracking
│   ├── attachments/            # File upload, download, preview, delete
│   ├── users/                  # User management (manager+)
│   ├── data_io/                # CSV import/export (admin-only)
│   ├── google/                 # Google Workspace (OAuth, Calendar, Meet, Docs, Drive)
│   └── settings/               # Settings page, interaction types, custom fields, UI prefs
├── services/                   # Shared business logic services
├── templates/
│   ├── base.html               # Bootstrap 5 layout with dark mode support
│   ├── auth/                   # Login page
│   ├── partials/               # Navbar, flash messages, modals, pagination, confirm-action
│   ├── dashboard/              # Dashboard, calendar, agenda, quarterly views
│   ├── companies/              # Company list, detail, form templates
│   ├── contacts/               # Contact list, detail, form templates
│   ├── interactions/           # Interaction list, form templates
│   ├── followups/              # Follow-up list, form, matrix templates
│   ├── cash/                   # Cash dashboard, transaction list, form
│   ├── accounts/               # Accounts dashboard, invoice views
│   ├── users/                  # User list, form templates
│   └── settings/               # Settings page, data import template
└── static/
    ├── css/custom.css          # Custom styles + dark mode overrides
    └── js/
        ├── main.js             # Delete modal, quick functions, toasts, pagination
        ├── panel.js            # Slide-over form panel
        ├── kanban.js           # Drag-and-drop board
        ├── reassign.js         # Client reassignment logic
        └── settings.js         # Theme switcher + settings handlers
```

---

## Acknowledgements

> Thank you to **Miłosz Ławrynowicz** for my first copy of *The 7 Habits of Highly Effective People* by Stephen Covey. The Eisenhower Matrix feature in this project exists because of you!

---

## Version History

| Version | Description |
|---------|-------------|
| v0.26.0-beta | Companies + Contacts restructure, Cash module, confirm-action modals, HTTPS support |
| v0.25.1-beta | UI polish, expanded seed data, and project state documentation |
| v0.25.0-beta | Data import/export, attachment taxonomy, and full test suite |
| v0.24.0-beta | Google Workspace integration — Calendar, Meet, Docs, and Drive |
| v0.23.0-beta | 3-role user management with authentication and authorisation |
| v0.16.0-beta | Attachment categories, tags, document preview, pagination, and UI preferences |
| v0.15.0-beta | File attachments on clients, contacts, and follow-ups |
| v0.14.0-beta | Custom client fields with Settings CRUD |
| v0.13.0-beta | Configurable interaction types with Settings CRUD |
| v0.12.0-beta | Clickable `tel:` and `mailto:` links |
| v0.11.0-beta | Colour scheme with dark mode (Light / Dark / System) |
| v0.10.0-beta | Settings page + DB-backed configurable quick functions |
| v0.9.0-beta | Eisenhower Matrix for follow-up prioritisation |
| v0.8.0-beta | Quarterly Overview with Q1–Q4 strategic calendar |
| v0.7.0-beta | Quick Functions for one-click interaction logging |
| v0.6.0-beta | Slide-over form panels with AJAX submit |
| v0.5.0-beta | Completion-to-outcome flow with modal |
| v0.4.0-beta | Kanban pipeline board with drag-and-drop |
| v0.3.0-beta | 360-degree client profile with two-column layout |
| v0.2.0-beta | Calendar time context for timed events |
| v0.1.0-beta | Rebrand to NextStep CRM with version system |

---

## Licence

MIT
