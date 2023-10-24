# Data Mesh Manager - GCP Integration

This repository contains an example how to integrate the [Data Mesh Manager](https://www.datamesh-manager.com/) into a Google Cloud Platform (GCP) account and automate the permission granting in BigQuery based on agreed data useage agreements.

It reads the Data Mesh Manager [events API](https://docs.datamesh-manager.com/events) and uses serverless GCP functionality like Cloud Functions, Firestore, Google Storace, Secretmanager, PubSub and Cloud Scheduler.

The infrastructure is set up by using Terraform.

## Limitations
- We do not handle deleted data usage agreements. So make sure to deactivate data usage agreements before deleting them. Otherwise, permissions will be kept existent.
- Not all kinds of output ports are supported at this point. Currently, we support only BigQuery tables with views.

## Architecture
For a better understanding of how the integration works, see this simple architecture diagram. Arrows show access direction.

```
                                       ┌─────────────────┐
                                       │                 │
                                       │Data Mesh Manager│
                                       │                 │
                                       └─────────────────┘
                                          ▲           ▲
                                          │           │
                                          │           │
                                          │           │
┌─────────────────────────────────────────┼───────────┼─────────────────────────────────────────────┐
│                                         │           │                                             │
│                                         │           │ 4. read usage agreement information         │
│                     1. pull events      │           │                                             │
│              ┌──────────────────────────┘           └───────────────────────────────┐             │
│              │                                                                      │             │
│              │                                                                      │             │
│              │                                                                      │             │
│     ┌────────┴────────┐                ──────────────── ──                ┌─────────┴─────────┐   │
│     │    poll_feed    │   2. write    │ dmm_events     │  │  3. trigger   │ manage_permissions│   │
│     │                 ├──────────────►│                │  ├──────────────►│                   │   │
│     │[Cloud  Function]│               │ [PubSub Topic] │  │               │ [Cloud  Function] │   │
│     └─────────────────┘                ──────────────── ──                └─────────┬─────────┘   │
│                                                                                     │             │
│                                                                                     │5. manage    │
│                                                                                     │             │
│                                                                                     ▼             │
│                                                                             ┌────────────────┐    │
│                                                                             │    BigQuery    │    │
│                                                                             │   Authorized   │    │
│                                                                             │      View      │    │
│                                                                             └────────────────┘    │
│                                                                                                   │
│                                                                                                   │
│                                                                                  [GCP Integration]│
└───────────────────────────────────────────────────────────────────────────────────────────────────┘
```

## Lambdas
### [Poll Feed](src%2Fpoll_feed%2Fmain.py)
- **Execution:** The function runs every minute, scheduled using a Cloud Scheduler Job putting a message in a PubSub topic which triggers the function.
- **Reading Events from Data Mesh Manager:** It reads all unprocessed [events from the Data Mesh Manager API](https://docs.datamesh-manager.com/events).
- **Sending Events to PubSub:** These events are then sent to a PubSub topic for further processing.
- **Tracking Last Event ID:** To ensure proper resumption of processing, the function remembers the last event ID by storing it in a Firestore document. This allows subsequent executions of the function to start processing from the correct feed position.

### [Manage Permissions](src%2Fmanage_permissions%2Fmain.py)
- **Execution:** The function is triggered by new messages in the PubSub topic.
- **Filtering Relevant Events:** The function selectively processes events based on their type. It focuses on events of the type `DataUsageAgreementActivatedEvent` and `DataUsageAgreementDeactivatedEvent`.
- **DataUsageAgreementActivatedEvent:** When a `DataUsageAgreementActivatedEvent` occurs, the function authorizes the BigQuery view against the source BigQuery dataset. These policies allow access from a producing data product's output port to a consuming data product. This will skip events if a policy already exists. The data usage agreement in Data Mesh Manager is tagged with `gcp-integration` and `gcp-integration-active`.
- **DataUsageAgreementDeactivatedEvent:** When a `DataUsageAgreementDeactivatedEvent` occurs, the function removes the permissions from the consuming data product to access the output port of the producing data product. This will skip events, if no corresponding policy ist found. The data usage agreement in Data Mesh Manager is tagged with `gcp-integration` and `gcp-integration-inactive`.
- **Extra Information:** To effectively process the events, the function may retrieve additional information from the Data Mesh Manager API. This information includes details about the data usage agreement, data products involved, and the teams associated with them.

## Usage
### Prerequisites
- [Terraform](https://developer.hashicorp.com/terraform/tutorials/gcp-get-started/install-cli)
- [Python3.11](https://www.python.org/downloads/release/python-3110/)

### Prepare your data products
To allow the integration to work, your data products in Data Mesh manager must contain some metadata in their [custom fields](https://docs.datamesh-manager.com/dataproducts).

#### Consumer Data Product
A consuming data product requires information about its BigQuery table id. We use the notation of the [data product specification](https://github.com/datamesh-architecture/dataproduct-specification) here.
```yaml
dataProductSpecification: 0.0.1
info:
  id: example_consumer_id
  name: Example Consumer Data Product
owner:
  teamId: example_team_id
custom:
  gcp-table-id: <project-name>.<dataset-name>.<table-name>
```

#### Provider Data Product
A providing data product also requires information about the BigQuery table id. We use the notation of the [data product specification](https://github.com/datamesh-architecture/dataproduct-specification) here.

```yaml
dataProductSpecification: 0.0.1
info:
  id: example_provider_id
  name: Example Provider Data Product
owner:
  teamId: example_team_id
custom:
  gcp-table-id: <project-name>.<dataset-name>.<table-name>
outputPorts:
  - id: example_output_port_id
```

### Deployment
- **Setup Terraform Variables:** An example of a minimum configuration can be found [here](terraform%2Fterraform.tfvars.template). Copy this file and name the copy `terraform.tfvars`. Set your credentials.
- **Login Into GCP:** There are multiple options to authenticate detailed in the [terraform provider documentation](https://registry.terraform.io/providers/hashicorp/google/latest/docs/guides/provider_reference#authentication).
- **Deployment:** Nothing more than `terraform apply` is needed to deploy everything to your gcp project.

## Licenses

This project is distributed under the MIT License. It includes various open-source dependencies, each governed by its respective license.

For more details, please refer to the [LICENSES](LICENSES) file.
