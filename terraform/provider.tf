terraform {
    required_providers {
        google = {
            source = "hashicorp/google"
            version = "~>5.2"
        }    
    }
}

provider "google" {
  project = var.google.project
  region = var.google.region
}

# Merely uses as a reference for where the project name or id are needed
data "google_project" "project" {

}