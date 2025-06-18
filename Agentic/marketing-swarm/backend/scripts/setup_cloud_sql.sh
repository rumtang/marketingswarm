#!/bin/bash
# Setup Cloud SQL instance for Marketing Swarm

# Configuration - update these values
PROJECT_ID="${GCP_PROJECT_ID:-your-project-id}"
INSTANCE_NAME="${CLOUD_SQL_INSTANCE:-marketing-swarm-db}"
REGION="${GCP_REGION:-us-central1}"
TIER="${DB_TIER:-db-f1-micro}"  # Smallest tier for testing
DB_NAME="marketing_swarm"
DB_USER="app_user"

echo "=== Marketing Swarm Cloud SQL Setup ==="
echo "Project: $PROJECT_ID"
echo "Instance: $INSTANCE_NAME"
echo "Region: $REGION"
echo "Tier: $TIER"
echo ""

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo "❌ gcloud CLI not found. Please install Google Cloud SDK first."
    exit 1
fi

# Set project
echo "Setting project..."
gcloud config set project $PROJECT_ID

# Create Cloud SQL instance
echo "Creating Cloud SQL instance..."
gcloud sql instances create $INSTANCE_NAME \
    --database-version=POSTGRES_15 \
    --tier=$TIER \
    --region=$REGION \
    --network=default \
    --no-backup \
    --database-flags=max_connections=50

if [ $? -ne 0 ]; then
    echo "❌ Failed to create Cloud SQL instance"
    exit 1
fi

# Wait for instance to be ready
echo "Waiting for instance to be ready..."
gcloud sql operations wait --timeout=300

# Create database
echo "Creating database..."
gcloud sql databases create $DB_NAME \
    --instance=$INSTANCE_NAME

# Create user
echo "Creating database user..."
# Generate secure password
DB_PASS=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-25)

gcloud sql users create $DB_USER \
    --instance=$INSTANCE_NAME \
    --password=$DB_PASS

# Create secret for password
echo "Creating secret for database password..."
echo -n "$DB_PASS" | gcloud secrets create db-pass --data-file=-

# Output connection details
echo ""
echo "✅ Cloud SQL instance created successfully!"
echo ""
echo "=== Connection Details ==="
echo "Instance Connection Name: $PROJECT_ID:$REGION:$INSTANCE_NAME"
echo "Database: $DB_NAME"
echo "User: $DB_USER"
echo "Password: Stored in Secret Manager as 'db-pass'"
echo ""
echo "=== Environment Variables for Cloud Run ==="
echo "INSTANCE_CONNECTION_NAME=$PROJECT_ID:$REGION:$INSTANCE_NAME"
echo "DB_USER=$DB_USER"
echo "DB_NAME=$DB_NAME"
echo "# DB_PASS should be loaded from Secret Manager"
echo ""
echo "=== Next Steps ==="
echo "1. Grant Cloud Run service account access to the secret:"
echo "   gcloud secrets add-iam-policy-binding db-pass \\"
echo "     --member=\"serviceAccount:SERVICE_ACCOUNT_EMAIL\" \\"
echo "     --role=\"roles/secretmanager.secretAccessor\""
echo ""
echo "2. Deploy to Cloud Run with Cloud SQL connection:"
echo "   gcloud run deploy marketing-swarm-backend \\"
echo "     --add-cloudsql-instances=$PROJECT_ID:$REGION:$INSTANCE_NAME \\"
echo "     --set-env-vars=INSTANCE_CONNECTION_NAME=$PROJECT_ID:$REGION:$INSTANCE_NAME"