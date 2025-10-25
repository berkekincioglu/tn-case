# Airline Management System API

## 🛠 Technology Stack

| Technology            | Version | Purpose                   |
| --------------------- | ------- | ------------------------- |
| Python                | 3.x     | Programming language      |
| Django                | 5.2.7   | Web framework             |
| Django REST Framework | 3.16.1  | REST API toolkit          |
| PostgreSQL            | 18      | Database                  |
| Docker                | -       | Database containerization |
| drf-spectacular       | 0.28.0  | API documentation         |

---

## 📁 Project Structure

```
technarts-case/
│
├── airline_project/          # Main Django project
│   ├── settings.py          # Project settings and configuration
│   ├── urls.py              # Main URL routing
│   └── wsgi.py              # WSGI configuration
│
├── airplanes/               # Airplane app
│   ├── models.py            # Airplane data model
│   ├── serializers.py       # Data serialization/validation
│   ├── views.py             # API endpoints logic
│   ├── urls.py              # URL routing
│   └── admin.py             # Admin interface configuration
│
├── flights/                 # Flights app
│   ├── models.py            # Flight data model
│   ├── serializers.py       # Data serialization/validation
│   ├── views.py             # API endpoints logic
│   ├── urls.py              # URL routing
│   └── admin.py             # Admin interface configuration
│
├── reservations/            # Reservations app
│   ├── models.py            # Reservation data model
│   ├── serializers.py       # Data serialization/validation
│   ├── views.py             # API endpoints logic
│   ├── urls.py              # URL routing
│   └── admin.py             # Admin interface configuration
│
├── manage.py                # Django CLI management tool
├── requirements.txt         # Python dependencies
├── docker-compose.yml       # Docker configuration for PostgreSQL
├── .env                     # Environment variables (not in git)
└── .env.example             # Example environment variables
```

---

## 🚀 Installation & Setup

### Prerequisites

- Python 3.x installed
- Docker installed and running
- Git installed

### Step 1: Clone the Repository

```bash
git clone https://github.com/berkekincioglu/tn-case.git
```

```bash
cd tn-case
```

### Step 2: Set Up Environment Variables

Copy the example environment file and configure it:

```bash
cp .env.example .env
```

Edit the `.env` file with your settings:

```
SECRET_KEY=your-secret-key-here
DEBUG=True
DB_NAME=airline_db
DB_USER=airline_user
DB_PASSWORD=airline_password
DB_HOST=localhost
DB_PORT=5432
```

### Step 3: Start the PostgreSQL Database

```bash
# Using Docker Compose
docker compose up -d

# Verify database is running
docker compose ps
```

You should see the database container `airline_db` running with status "healthy".

### Step 4: Set Up Python Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate
```

### Step 5: Install Python Dependencies

```bash
pip install -r requirements.txt
```

### Step 6: Run Database Migrations

```bash
# Create migration files (already done, but included for reference)
python manage.py makemigrations

# Apply migrations to create database tables
python manage.py migrate
```

### Step 7: Create a Superuser (Optional but Recommended)

This creates an admin account for accessing the Django admin interface:

```bash
python manage.py createsuperuser
```

Follow the prompts to set:

- Username (e.g., `admin`)
- Email address
- Password

### Step 8: Start the Development Server

```bash
python manage.py runserver
```

The API will be available at: **http://127.0.0.1:8000/**

---

## 📡 API Endpoints

### Base URL

```
http://127.0.0.1:8000/api/
```

## 🧪 Testing with Postman

### Import Airline_Api.postman_collection.json

### 🔹 Airplane Endpoints

| Method | Endpoint                       | Description                             |
| ------ | ------------------------------ | --------------------------------------- |
| GET    | `/api/airplanes/`              | List all airplanes                      |
| POST   | `/api/airplanes/`              | Create a new airplane                   |
| GET    | `/api/airplanes/{id}/`         | Get details of a specific airplane      |
| PATCH  | `/api/airplanes/{id}/`         | Update airplane information             |
| DELETE | `/api/airplanes/{id}/`         | Delete an airplane                      |
| GET    | `/api/airplanes/{id}/flights/` | Get all flights for a specific airplane |

**Query Parameters for List:**

- `status`: Filter by operational status (`true` or `false`)

### 🔹 Flight Endpoints

| Method | Endpoint                          | Description                           |
| ------ | --------------------------------- | ------------------------------------- |
| GET    | `/api/flights/`                   | List all flights (supports filtering) |
| POST   | `/api/flights/`                   | Create a new flight                   |
| GET    | `/api/flights/{id}/`              | Get details of a specific flight      |
| PATCH  | `/api/flights/{id}/`              | Update flight information             |
| DELETE | `/api/flights/{id}/`              | Delete a flight                       |
| GET    | `/api/flights/{id}/reservations/` | Get all reservations for a flight     |

**Query Parameters for List:**

- `departure`: Filter by departure location (e.g., `Istanbul`)
- `destination`: Filter by destination location (e.g., `London`)
- `departure_date`: Filter by departure date (format: `YYYY-MM-DD`)
- `arrival_date`: Filter by arrival date (format: `YYYY-MM-DD`)

**Example Filtered Request:**

```
GET /api/flights/?departure=Istanbul&destination=London&departure_date=2024-01-15
```

### 🔹 Reservation Endpoints

| Method | Endpoint                         | Description                           |
| ------ | -------------------------------- | ------------------------------------- |
| GET    | `/api/reservations/`             | List all reservations                 |
| POST   | `/api/reservations/`             | Create a new reservation              |
| GET    | `/api/reservations/{id}/`        | Get details of a specific reservation |
| PATCH  | `/api/reservations/{id}/`        | Update reservation information        |
| POST   | `/api/reservations/{id}/cancel/` | Cancel a reservation                  |

**Query Parameters for List:**

- `status`: Filter by status (`true` for active, `false` for cancelled)
- `flight`: Filter by flight ID
- `passenger_email`: Filter by passenger email

**Note:** There is no DELETE operation for reservations. Use the cancel endpoint instead to maintain booking history.

### 🔹 Documentation Endpoints

| URL            | Description                                   |
| -------------- | --------------------------------------------- |
| `/api/docs/`   | Swagger UI (interactive API testing)          |
| `/api/redoc/`  | ReDoc (alternative documentation UI)          |
| `/api/schema/` | OpenAPI schema (JSON) for import into Postman |
| `/admin/`      | Django admin interface                        |

---

## 🧠 Business Logic

### 1. Flight Conflict Detection

**Rule:** An airplane cannot have overlapping flights. There must be at least a 1-hour gap between flights.

**How it works:**

- When creating/updating a flight, the system checks for time conflicts
- Calculates a conflict window: 1 hour before departure to 1 hour after arrival
- Searches for existing flights of the same airplane in that window
- Rejects the operation if a conflict is found

**Example:**

```
Flight A: 10:00 - 12:00
Minimum gap: 1 hour
Next flight can start: 13:00 or later
```

**Location:** `flights/models.py` - `_check_flight_conflicts()` method

### 2. Capacity Management (Preventing Overbooking)

**Rule:** The number of active reservations cannot exceed the airplane's capacity.

**How it works:**

- When creating a reservation, counts existing active reservations for that flight
- Compares with the airplane's capacity
- Rejects the reservation if the flight is full

**Location:** `reservations/models.py:150` - `clean()` method validation

### 3. Automatic Reservation Code Generation

**Rule:** Each reservation gets a unique 8-character alphanumeric code.

**How it works:**

- Uses Python's `secrets` module for cryptographic randomness
- Generates code from uppercase letters and digits (36 possible characters)
- Checks database for uniqueness
- Regenerates if collision detected (extremely rare with 36^8 = 2.8 trillion possibilities)

**Example codes:** `A1B2C3D4`, `9XYZ1234`, `ABCD5678`

**Location:** `reservations/models.py:108` - `_generate_reservation_code()` method

### When Emails are Sent (Logged to Console SMTP is not configured)

1. **Reservation Confirmation** - When a new reservation is created
2. **Cancellation Confirmation** - When a reservation is cancelled

```bash
# Start the server
python manage.py runserver

# Create a reservation via API
# Check the terminal - the email will be printed there!
```

### Email Content

**Confirmation Email includes:**

- Reservation code (e.g., `ABC12345`)
- Passenger name
- Flight details (number, departure, destination, times)
- Aircraft information
- Check-in instructions

**Cancellation Email includes:**

- Cancelled reservation code
- Flight details
- Cancellation confirmation

### API Response with Email Status

When creating or cancelling a reservation, the API response includes email status:

```json
{
  "reservation_code": "ABC12345",
  "email_sent": true,
  "email_message": "Confirmation email sent to passenger@example.com",
  "message": "Reservation created successfully!"
}
```
