# Puts all files of the poll function into a zip archive to later be uploaded
# into the storage bucket. Note: Use excludes in case there are excess files or folders
data "archive_file" "poll_feed" {
    type = "zip"
    output_path = "${path.module}/poll_feed.zip"

    excludes = ["venv", "__pycache__"]

    source_dir = "../src/poll_feed/"
}

# Puts all files of the manage permissions function into a zip archive to later be uploaded
# into the storage bucket. Note: Use excludes in case there are excess files or folders
data "archive_file" "manage_permissions" {
    type = "zip"
    output_path = "${path.module}/manage_permissions.zip"

    excludes = ["venv", "__pycache__" ]

    source_dir = "../src/manage_permissions/"
}

# Creates the bucket where the function code will be stored
resource "google_storage_bucket" "functions_bucket" {
    name = var.functions.source_bucket
    location = "EU"
    uniform_bucket_level_access = true
}

# Stores the poll function's code as a new object in the storage
# A hash in the object's name is used to trigger a new deployment
resource "google_storage_bucket_object" "poll_feed" {
    name = "poll_feed.${data.archive_file.poll_feed.output_base64sha256}.zip"
    source = data.archive_file.poll_feed.output_path
    bucket = google_storage_bucket.functions_bucket.name
}

# Stores the manage permissions function's code as a new object in the storage
# A hash in the object's name is used to trigger a new deployment
resource "google_storage_bucket_object" "manage_permissions" {
    name = "manage_permissions.${data.archive_file.manage_permissions.output_base64sha256}.zip"
    source = data.archive_file.manage_permissions.output_path
    bucket = google_storage_bucket.functions_bucket.name
}