# SFU Food Pantry Management System

**Course:** CMPT 354 - Database Systems  
**Institution:** Simon Fraser University  
**Term:** Spring 2026

## Project Overview

The SFU Food Pantry Management System is a comprehensive web-based application designed to streamline food pantry operations at Simon Fraser University. The system manages donations, tracks inventory, processes visitor check-ins, and distributes food items efficiently.

### Group Members
- Aliriza Hazarat
- Damin Mutti
- Karanveer Singh
- Prabhjot Singh

---

## Features

### Core Functionality
- **Donation Management** - Track incoming donations from individual donors and organizations
- **Inventory Tracking** - Maintain real-time inventory with batch tracking and expiry dates
- **Visitor Check-in** - Log visitor information and categorize by type (Student, Staff, Community)
- **Food Distribution** - Process food distribution with automatic inventory updates
- **Reports & Analytics** - Generate insights on donations, inventory, visitors, and distribution patterns

### Technical Highlights
- **Responsive Design** - Fully responsive web interface for desktop and mobile devices
- **Database Normalization** - BCNF normalized schema with 10 normalized tables
- **Referential Integrity** - Complete foreign key constraints and data validation
- **Advanced Queries** - Complex SQL queries including joins, aggregations, and grouping
- **User Authentication** - Role-based access (Admin, Manager, Volunteer, Staff)

---

## Database Schema

The system uses a normalized relational database with 10 tables:

| Table | Purpose |
|-------|---------|
| DONOR | Track donation sources (individuals and organizations) |
| CATEGORY | Food item categorization |
| USER_ACCOUNT | Staff and volunteer accounts with role-based access |
| VISITOR | Track pantry visitors |
| FOOD_ITEM | Catalog of food items with reorder thresholds |
| DONATION | Log incoming donations |
| PANTRY_VISIT | Record visitor check-ins |
| DONATION_ITEM | Line items within each donation |
| INVENTORY_BATCH | Track inventory batches with expiry dates and locations |
| DISTRIBUTES | Record food distribution to visitors |

**Database Status:** ✓ Normalized to BCNF with proper referential integrity

---

## Technology Stack

- **Backend:** Python Flask
- **Frontend:** HTML5, CSS3, JavaScript
- **Database:** SQL Server (CSIL)
- **Server:** Deployed on cypress.csil.sfu.ca (database: psa167354)

---

## Installation & Setup

### Prerequisites
- Python 3.8+
- Flask and dependencies
- SQL Server connection (CSIL credentials)
- pyodbc driver

### Steps to Deploy

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd SFU-Pantry-Database-System
   ```

2. **Set up the database**
   - Open SQL Server Management Studio (SSMS)
   - Connect to cypress.csil.sfu.ca
   - Run `setup_script.sql` to create all tables and load sample data

3. **Configure database connection**
   - Update credentials in `app.py`:
   ```python
   DB_CONFIG = {
       'driver': '{ODBC Driver 17 for SQL Server}',
       'server': 'cypress.csil.sfu.ca',
       'database': 'psa167354',
       'uid': 's_psa167',
       'pwd': 'your_password_here'
   }
   ```

4. **Install Python dependencies**
   ```bash
   pip install flask pyodbc
   ```

5. **Run the application**
   ```bash
   python app.py
   ```
   - Access at http://localhost:5000

---

## Project Files

```
.
├── README.md                 # Project documentation
├── DEMO_SCRIPT.md           # 5-minute demo script
├── app.py                   # Flask application (941 lines)
├── config.py                # Configuration settings
├── normalization.md         # Database normalization documentation
├── schema.sql               # Database schema definition
├── setup_database.sql       # Complete setup script with sample data
├── seed.sql                 # Legacy seed data (SQLite format)
├── static/
│   ├── css/
│   │   └── style.css        # Stylesheet
│   └── js/
│       └── main.js          # Frontend scripts
└── templates/
    ├── base.html            # Base template
    ├── index.html           # Dashboard
    ├── inventory.html       # Inventory management
    ├── donations.html       # Donations page
    ├── visits.html          # Visitor check-ins
    ├── distribution.html    # Food distribution
    ├── reports.html         # Analytics & reports
    ├── 404.html             # Error pages
    └── 500.html
```

---

## Query Implementations

All required query types are implemented in the application:

### 1. Join Queries (60 marks)
- **Inventory Page** ([app.py#L142](app.py#L142)): Multi-table joins for inventory display
- **Distribution Page** ([app.py#L649](app.py#L649)): Complex joins across 4 tables
- **Reports Page** ([app.py#L862](app.py#L862)): Multiple joins for analytics

### 2. Aggregation Queries (20 marks)
- **Donations by Type** - GROUP BY with COUNT and SUM
- **Visitor Statistics** - Time-based aggregation
- **Top Items Distributed** - Ranking by total distributed quantity

### 3. Division Query (10 marks)
- **Low Stock Items** - Using HAVING clause for threshold comparison ([app.py#L160](app.py#L160))

### 4. Update Operations (10 marks)
- **Distribution Updates** ([app.py#L750](app.py#L750)) - Automatic inventory reduction
- **Donation Processing** - Updates inventory on receipt

### 5. Delete with CASCADE (10 marks)
- Foreign key constraints configured throughout schema.sql with cascade rules

---

## Key Features Demonstrated

### Responsive Web Design (20 marks)
- CSS Grid and Flexbox layouts
- Adaptive navigation and forms
- Touch-friendly interface elements

### SQL Assertions/Triggers (20 marks)
- CHECK constraints on quantities (must be > 0 or >= 0)
- UNIQUE constraints on Email and Username
- Referential integrity through foreign keys

### User Experience
- Intuitive dashboard with quick access to all functions
- Real-time inventory updates
- Expiry date tracking and alerts
- Low stock notifications
- Comprehensive reporting dashboard

---

## Running Demos

### Application Demo


### Query Demo

---


---

- Project Lead: Prabhjot Singh 
- Course Instructor: Mohammad Tayebi

---

