Here is your **clean `info.md` (Day 1 setup) with NO code**, ready to copy directly:

---

# INFO.MD — DAY 1 PROJECT SETUP

## PROJECT: TRADING BOT SYSTEM

This document outlines the first day of development for the trading bot system. The focus is on setting up the project foundation, database connection, and basic application interface for external access.

---

# 1. PROJECT STRUCTURE

The initial project will be organized into a clear and scalable folder structure to support backend, frontend, database handling, and future trading modules.

The system will include separate directories for backend logic, frontend interface, database configuration, data storage, and reports.

This structure is designed to ensure modular development, making it easier to expand the system into backtesting, forward testing, and live trading features.

---

# 2. DATABASE SETUP (POSTGRESQL)

A PostgreSQL database will be created to store all trading-related data.

The database will act as the central storage system for:

* Trading strategies
* Market data
* Trade logs
* Backtesting results
* Forward testing results

A dedicated database user will be created with full permissions to manage the system data securely.

---

# 3. DATABASE CONNECTION (BACKEND)

The backend system will be connected to the PostgreSQL database using Python.

This connection will allow the application to:

* Read and write trading data
* Store strategy configurations
* Save trade execution history
* Manage backtesting results

The database connection layer will be isolated to ensure reusability across all services.

---

# 4. API SETUP (FASTAPI BACKEND)

A lightweight backend API will be created using a Python-based web framework.

This API will serve as the main communication layer between:

* Frontend dashboard
* External users
* Trading engines
* Database system

The API will initially provide basic endpoints to confirm system status and health checks.

This ensures that the backend is properly running and accessible before adding trading functionality.

---

# 5. PUBLIC API ACCESS DESIGN

The system will be designed to allow external access through REST API endpoints.

This means:

* External systems can interact with the trading bot
* Future integration with dashboards or mobile apps is possible
* Trading operations can be controlled programmatically

At this stage, only basic connectivity endpoints are active.

---

# 6. DAY 1 OBJECTIVES

By the end of Day 1, the following should be completed:

* Full project folder structure is created
* PostgreSQL database is installed and configured
* Database connection is successfully established in backend
* API server is running successfully
* External requests can reach the backend system
