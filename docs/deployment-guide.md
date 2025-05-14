# Deployment Guide

This guide covers how to deploy GastroAssist to various environments for production use.

## Prerequisites

Before deploying GastroAssist, ensure you have:

1. A fully tested version of the application
2. Required API keys (OpenAI, Tavily)
3. A production database (PostgreSQL recommended)
4. Domain name (optional, but recommended)
5. SSL certificate for HTTPS (highly recommended for medical applications)

## General Deployment Steps

Regardless of the hosting platform, these steps apply:

1. **Environment Configuration**
   - Set up production environment variables (see [Environment Variables Guide](./environment-variables.md))
   - Disable debug mode (`DEBUG=False`)
   - Configure a production database
   - Set appropriate logging levels

2. **Security Considerations**
   - Use HTTPS for all traffic
   - Implement proper authentication
   - Apply rate limiting to prevent abuse
   - Consider implementing a Web Application Firewall (WAF)

3. **Performance Optimization**
   - Enable caching where appropriate
   - Configure appropriate worker counts for your server
   - Set up a CDN for static assets
   - Implement database connection pooling

## Docker Deployment

Docker is the recommended deployment method for GastroAssist as it ensures consistent environments.

### Docker Compose Setup

1. Create a `docker-compose.yml` file:

```yaml
version: '3'

services:
  backend:
    build:
      context: .
      dockerfile: Dockerfile.backend
    ports:
      - "8000:8000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - TAVILY_API_KEY=${TAVILY_API_KEY}
      - DATABASE_URL=${DATABASE_URL}
      - DEBUG=False
      - HOST=0.0.0.0
      - PORT=8000
    depends_on:
      - db
    restart: always

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile.frontend
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=https://api.yourdomain.com
    restart: always

  db:
    image: postgres:14
    volumes:
      - postgres_data:/var/lib/postgresql/data
    environment:
      - POSTGRES_PASSWORD=${DB_PASSWORD}
      - POSTGRES_USER=${DB_USER}
      - POSTGRES_DB=${DB_NAME}
    restart: always

volumes:
  postgres_data:
```

2. Create Dockerfiles:

**Dockerfile.backend**:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Dockerfile.frontend**:
```dockerfile
FROM node:18-alpine

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

CMD ["npm", "start"]
```

3. Deploy with Docker Compose:

```bash
docker-compose up -d
```

## Cloud Platform Deployments

### AWS Deployment

#### Using Elastic Beanstalk

1. Install the EB CLI:
   ```bash
   pip install awsebcli
   ```

2. Initialize EB application:
   ```bash
   eb init -p python-3.11 gastroassist
   ```

3. Create a `.ebextensions/01_packages.config` file:
   ```yaml
   packages:
     yum:
       git: []
       postgresql-devel: []
   ```

4. Create a `.ebextensions/02_python.config` file:
   ```yaml
   option_settings:
     aws:elasticbeanstalk:application:environment:
       PYTHONPATH: "/var/app/current:"
     aws:elasticbeanstalk:container:python:
       WSGIPath: app.main:app
   ```

5. Create a `.ebextensions/03_environment.config` file:
   ```yaml
   option_settings:
     aws:elasticbeanstalk:application:environment:
       OPENAI_API_KEY: your_openai_api_key
       TAVILY_API_KEY: your_tavily_api_key
       DATABASE_URL: postgresql://user:password@yourrds.amazonaws.com:5432/gastroassist
       DEBUG: False
   ```

6. Create a `Procfile`:
   ```
   web: gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app
   ```

7. Deploy to Elastic Beanstalk:
   ```bash
   eb create gastroassist-prod
   ```

### Google Cloud Platform (GCP)

#### Using Cloud Run

1. Build the Docker image:
   ```bash
   gcloud builds submit --tag gcr.io/your-project/gastroassist
   ```

2. Deploy to Cloud Run:
   ```bash
   gcloud run deploy gastroassist \
     --image gcr.io/your-project/gastroassist \
     --platform managed \
     --set-env-vars="OPENAI_API_KEY=your_openai_api_key,TAVILY_API_KEY=your_tavily_api_key,DATABASE_URL=postgresql://user:password@your-db-ip:5432/gastroassist,DEBUG=False"
   ```

### Microsoft Azure

#### Using Azure App Service

1. Create a `requirements.txt` file with all dependencies
2. Create an App Service in the Azure Portal
3. Set up CI/CD through Azure DevOps or GitHub Actions
4. Configure environment variables in the Azure Portal

### Heroku Deployment

1. Install the Heroku CLI and log in:
   ```bash
   heroku login
   ```

2. Create a new Heroku app:
   ```bash
   heroku create gastroassist
   ```

3. Add a `Procfile`:
   ```
   web: gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app
   ```

4. Set environment variables:
   ```bash
   heroku config:set OPENAI_API_KEY=your_openai_api_key
   heroku config:set TAVILY_API_KEY=your_tavily_api_key
   heroku config:set DEBUG=False
   ```

5. Add a PostgreSQL database:
   ```bash
   heroku addons:create heroku-postgresql:hobby-dev
   ```

6. Deploy to Heroku:
   ```bash
   git push heroku main
   ```

## Production Database Setup

### PostgreSQL Setup

1. Create a database and user:
   ```sql
   CREATE DATABASE gastroassist;
   CREATE USER gastroassist_user WITH PASSWORD 'secure_password';
   GRANT ALL PRIVILEGES ON DATABASE gastroassist TO gastroassist_user;
   ```

2. Update the `DATABASE_URL` environment variable:
   ```
   DATABASE_URL=postgresql://gastroassist_user:secure_password@localhost:5432/gastroassist
   ```

3. Run migrations:
   ```bash
   python -m app.db.init_db
   ```

## Reverse Proxy Configuration

### Nginx Configuration

For production deployments, it's recommended to use Nginx as a reverse proxy:

```nginx
server {
    listen 80;
    server_name yourdomain.com;
    
    # Redirect HTTP to HTTPS
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl;
    server_name yourdomain.com;
    
    ssl_certificate /path/to/fullchain.pem;
    ssl_certificate_key /path/to/privkey.pem;
    
    # Frontend
    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    # API
    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        
        # For WebSockets (if used)
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

## Monitoring and Maintenance

### Health Checks

Implement a health check endpoint in your API:

```python
@app.get("/health")
async def health_check():
    """
    Health check endpoint for monitoring
    """
    return {
        "status": "healthy",
        "version": "0.1.0",
        "timestamp": datetime.now().isoformat()
    }
```

### Logging

Configure comprehensive logging:

```python
import logging
from logging.handlers import RotatingFileHandler

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        RotatingFileHandler('logs/gastroassist.log', maxBytes=10485760, backupCount=5),
        logging.StreamHandler()
    ]
)
```

### Backup Procedures

1. Database backups:
   ```bash
   pg_dump -U gastroassist_user gastroassist > backup_$(date +%Y%m%d).sql
   ```

2. Automate backups with a cron job:
   ```
   0 2 * * * pg_dump -U gastroassist_user gastroassist > /backups/gastroassist_$(date +\%Y\%m\%d).sql
   ```

## Scaling Strategies

### Horizontal Scaling

1. Use a load balancer to distribute traffic across multiple instances
2. Implement stateless design for the backend to facilitate scaling
3. Use Redis or another distributed cache for session management

### Vertical Scaling

1. Increase resources (CPU, RAM) for existing instances
2. Optimize database queries and indexing
3. Implement query caching for frequently accessed data

## Troubleshooting Production Issues

### Common Problems and Solutions

1. **High Server Load**
   - Check for inefficient queries
   - Implement caching
   - Consider scaling resources

2. **Memory Leaks**
   - Set up memory monitoring
   - Implement proper resource cleanup
   - Consider container restarts on a schedule

3. **Slow Response Times**
   - Optimize database queries
   - Implement caching
   - Check API rate limits

4. **Database Connection Issues**
   - Verify connection string
   - Check for connection leaks
   - Set up connection pooling

## Conclusion

This deployment guide covers the basics of deploying GastroAssist to various environments. For specific questions or issues, consult the documentation for your chosen deployment platform or reach out to our support channels.

Remember that as a medical application, reliability, security, and data privacy should be your top priorities when deploying GastroAssist.
