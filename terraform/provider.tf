terraform {
    required_providers {
        google = {
            source = "hashicorp/google"
            version = "~>5.2"
        }    
    }
}

provider "google" {
  project = var.project
  region = var.region
}

data "google_project" "project" {

}