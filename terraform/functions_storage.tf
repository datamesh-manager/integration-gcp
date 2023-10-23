data "archive_file" "poll_feed" {
    type = "zip"
    output_path = "${path.module}/poll_feed.zip"

    # excludes = ["venv", "__pycache__", ".fleet", ".idea"]

    source_dir = "../src/poll_feed/"
}

data "archive_file" "manage_permissions" {
    type = "zip"
    output_path = "${path.module}/manage_permissions.zip"

    # excludes = ["venv", "__pycache__", ".fleet", ".idea", "*.json" ]

    source_dir = "../src/manage_permissions/"
}

resource "google_storage_bucket" "functions_bucket" {
    name = var.functions.source_bucket
    location = "EU"
    uniform_bucket_level_access = true
}

resource "google_storage_bucket_object" "poll_feed" {
    name = "poll_feed.${data.archive_file.poll_feed.output_base64sha256}.zip"
    source = data.archive_file.poll_feed.output_path
    bucket = google_storage_bucket.functions_bucket.name
}

resource "google_storage_bucket_object" "manage_permissions" {
    name = "manage_permissions.${data.archive_file.manage_permissions.output_base64sha256}.zip"
    source = data.archive_file.manage_permissions.output_path
    bucket = google_storage_bucket.functions_bucket.name
}