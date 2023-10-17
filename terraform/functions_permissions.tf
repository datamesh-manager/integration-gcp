data "google_iam_policy" "service_account_policy" {
#     binding {
#         role = "roles/bigquery.dataOwner"
#         members = ["serviceAccount:${google_service_account.function_service_account.email}"]
#     }
#     binding {
#         role = "roles/secretmanager.secretAccessor"
#         members = ["serviceAccount:${google_service_account.function_service_account.email}"]
#     }
    binding {
        role = "roles/editor"
        members = ["serviceAccount:${google_service_account.function_service_account.email}"]
    }
}

resource "google_service_account" "function_service_account" {
    account_id = "dmm-permission-manager"
    display_name = "dmm permission manager"
}


resource "google_project_iam_member" "big_query" {
    project = data.google_project.project.project_id
    role = "roles/bigquery.dataOwner"
    member = "serviceAccount:${google_service_account.function_service_account.email}"
}

resource "google_project_iam_member" "secret" {
    project = data.google_project.project.project_id
    role = "roles/secretmanager.secretAccessor"
    member = "serviceAccount:${google_service_account.function_service_account.email}"
}

resource "google_service_account_iam_policy" "service_account_policy" {
    service_account_id = google_service_account.function_service_account.id
    policy_data = data.google_iam_policy.service_account_policy.policy_data
}