# Creates a service account used by both cloud functions to manage the necessary permissions
resource "google_service_account" "function_service_account" {
    account_id = "dmm-permission-manager"
    display_name = "dmm permission manager"
}

# This adds the service account as a member to the default editor role
# to be able to use firestore and pubsubs
resource "google_project_iam_member" "editor" {
    project = data.google_project.project.project_id
    role = "roles/editor"
    member = "serviceAccount:${google_service_account.function_service_account.email}"
}

# This adds the service account as a member to the bigquery.dataOwner role
# to be able to authorize views from within the manage permissions function
resource "google_project_iam_member" "big_query" {
    project = data.google_project.project.project_id
    role = "roles/bigquery.dataOwner"
    member = "serviceAccount:${google_service_account.function_service_account.email}"
}

# This adds the service account as a member to the secretmanager.secretAccessor role
# to be able to access the api key from the secretmanager
resource "google_project_iam_member" "secret" {
    project = data.google_project.project.project_id
    role = "roles/secretmanager.secretAccessor"
    member = "serviceAccount:${google_service_account.function_service_account.email}"
}
