FROM python:3.8-slim

# Generate requirements.txt file
RUN pip install pipenv
COPY Pipfile* /
RUN pipenv lock --requirements > requirements.txt

# Install project packages
RUN pip install -r requirements.txt
# Keeps docker lightweight removing temporary installation files
#RUN apk del .tmp

RUN mkdir /app
# Copy project's files
COPY . /app
# Change directory to roles_ms
WORKDIR /app
# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
# Copy scripts dir
COPY ./scripts /scripts
# Updates execution permissions
RUN chmod +x /scripts/*.sh

# Creates directory to holds static files (*.js, *.html, *.css)
RUN mkdir -p /web/static

# Creates a new user (best practices)
RUN adduser app-user
RUN chown -R app-user:app-user /web
RUN chmod -R 755 /web
RUN chown -R app-user:app-user /app
RUN chmod -R 755 /app

# Switch to created user
USER app-user

# Execute BD
ENTRYPOINT ["/scripts/entrypoint.sh"]