# Use official PostgreSQL image
FROM postgres:16

# Set environment variables
ENV POSTGRES_USER=postgres
ENV POSTGRES_PASSWORD=admin
ENV POSTGRES_DB=fccpd

# Expose PostgreSQL default port
EXPOSE 5432

# Copy initialization scripts
COPY init.sql /docker-entrypoint-initdb.d/

# Create volume for persistent data
VOLUME ["/var/lib/postgresql/data"]

# The default CMD from the postgres image will be used
# which runs postgres server