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

data "google_project" "project" {

}