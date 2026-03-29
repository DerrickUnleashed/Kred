# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 3.0.x   | :white_check_mark: |
| < 3.0   | :x:                |

## Security Features

### Authentication
- Supabase Auth for user authentication
- JWT-based session management
- Password hashing with bcrypt
- Protected routes for authenticated users

### API Security
- CORS middleware configured for frontend origin
- Input validation using Pydantic models
- Rate limiting considerations for API endpoints
- Environment variables for sensitive credentials

### Database Security
- Row Level Security (RLS) enabled on all tables
- Users can only access their own data
- Prepared statements to prevent SQL injection

### Environment Variables
Never commit these files containing secrets:
- `.env` files
- `backend/.env`
- `frontend/.env`

Required environment variables:
```
# Backend
GROQ_API_KEY=your_groq_api_key
HF_TOKEN=your_huggingface_token
SUPABASE_URL=your_supabase_url
SUPABASE_ANON_KEY=your_supabase_anon_key

# Frontend
VITE_SUPABASE_URL=your_supabase_url
VITE_SUPABASE_ANON_KEY=your_supabase_anon_key
VITE_STOCKS_API_URL=http://localhost:8000
```

## Reporting a Vulnerability

If you discover a security vulnerability within KRED, please report it responsibly:

1. **Do not** create a public GitHub issue
2. Contact the development team directly
3. Include a detailed description of the vulnerability
4. Provide steps to reproduce the issue
5. Wait for acknowledgment before disclosure

We aim to respond to vulnerability reports within 48 hours and will work to address critical issues promptly.

## Security Best Practices

### For Users
- Use strong, unique passwords
- Enable two-factor authentication (if available)
- Never share your login credentials
- Log out after using shared devices

### For Developers
- Validate all user inputs
- Sanitize data before database operations
- Use parameterized queries
- Keep dependencies updated
- Run security audits: `npm audit` for frontend, `pip audit` for backend

## Compliance

KRED handles personal and financial data. Ensure compliance with:
- Data privacy regulations
- Secure data transmission (HTTPS)
- Proper data encryption at rest
