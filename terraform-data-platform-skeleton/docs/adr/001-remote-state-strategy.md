# ADR 001: Remote State Management Strategy

**Status:** Proposed  
**Date:** 2026-02-26  
**Author:** André Wehr

## Context

A small data platform team (3–6 engineers) needs a Terraform state strategy 
that prevents conflicts, enables collaboration, and keeps secrets safe.

Local state files (default Terraform behavior) are not suitable for team 
environments – they cause race conditions and cannot be shared safely via Git 
(state files may contain sensitive values).

## Decision

We use **S3 + DynamoDB** (AWS) or **Azure Blob Storage** (Azure) for remote 
state, depending on the primary cloud provider. Key principles:

- One state file per environment (dev/prod)
- State locking via DynamoDB (AWS) or native blob leasing (Azure)
- State bucket has versioning enabled → rollback capability
- State bucket is managed separately from the platform itself (bootstrap separation)

## Consequences

### Positive
- No "last write wins" conflicts in team environments
- Full audit trail via versioning
- Separation of concerns: state infrastructure ≠ platform infrastructure

### Negative / Trade-offs
- Bootstrap problem: state bucket must exist before `terraform init` can run
- Credentials for state backend must be managed separately (never in repo)
- DynamoDB incurs minor cost (~$0 at low usage volume)

## Alternatives Considered

| Option | Pro | Con |
|--------|-----|-----|
| Terraform Cloud | Free tier, built-in locking | Vendor lock-in, SaaS dependency |
| Git-committed state | Simple setup | Race conditions, secrets in Git |
| Local state | Zero setup | No team collaboration possible |

## Relevance for Small Teams (like tractionwise)

Even with 2–3 engineers touching infrastructure, remote state pays off 
immediately. The locking mechanism alone prevents the most common IaC 
incident: two engineers running `terraform apply` simultaneously.
