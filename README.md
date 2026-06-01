# The Wise Carpenter — Telegram Bots

A two-bot system built for the Wise Carpenter movement to streamline 
communication between the team and users.

## Bots

**User Bot** (`@wisecarpenter_bot`)
- Browse information about the Wise Carpenter movement
- View FAQ and workshops
- Submit requests to open a workshop or invite a mobile workshop

**Admin Bot** (`@wisecarpenter_admin_bot`)
- Manage content shown in the user bot
- Process user requests and support questions
- Manage admin accounts and view statistics

## Tech Stack

- Python 3.12, aiogram 3
- PostgreSQL + SQLAlchemy (async) + Alembic
- Redis (FSM state storage)
- Pydantic Settings

## Setup

1. Clone the repository
2. Create a virtual environment and install dependencies:
```bash
   pip install -r requirements.txt
```
3. Copy `env.example` to `.env` and fill in the values
4. Run migrations:
```bash
   alembic upgrade head
```
5. Start both bots:
```bash
   python3 -m run
```

## Learn More

To learn more about the Wise Carpenter movement:

- 🌐 Website: [m-teslya.org.ua](https://m-teslya.org.ua/)
- 📢 Telegram channel: [@wisecarpenter](https://t.me/wisecarpenter)

## Feedback & Support

If you'd like to support this project or share feedback, feel free to reach out:

- 📧 Email: [kucheruk.yevhenii@gmail.com](mailto:kucheruk.yevhenii@gmail.com)
- 💬 Telegram: [@zhenyakr515](https://t.me/zhenyakr515)

## License

MIT
