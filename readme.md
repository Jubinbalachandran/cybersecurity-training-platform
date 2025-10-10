# Cybersecurity Training Platform

A self-hosted, KnowBe4-inspired cybersecurity training platform. Manage training modules, track user progress, generate reports, and control feature access via super admin and admin roles. Each installation uses a separate database and includes licensing and demo modes.

## Features

- Modular training management (CRUD)
- User progress tracking and reporting
- Role-based access (Super Admin, Admin)
- Super admin controls: license (user limit), feature enable/disable, demo mode
- Demo mode: restricts features for evaluation
- Local SQLite database (one per installation)
- Web-based UI (Flask)
- Easy installer for any server

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/Jubinbalachandran/cybersecurity-training-platform.git
   cd cybersecurity-training-platform
   ```

2. Install dependencies:
   ```bash
   pip install .
   ```

3. Run the application:
   ```bash
   python run.py
   ```

4. On first run, register a Super Admin account.

## Configuration

- Edit `app/config.py` to adjust database or secret key.

## Licensing

- Super Admin sets the maximum number of users (license).
- When demo mode is enabled, only selected features are available.

## Project Structure

```
cybersecurity-training-platform/
│
├── app/
│   ├── __init__.py
│   ├── config.py
│   ├── models.py
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── admin.py
│   │   ├── superadmin.py
│   │   └── training.py
│   ├── templates/
│   └── static/
├── install/
│   └── setup.py
├── requirements.txt
├── run.py
└── README.md
```

## Contributing

Pull requests are welcome! For major changes, open an issue first.

## License

MIT