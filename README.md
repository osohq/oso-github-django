# Modeling GitHub permissions with oso

This application is a sample application based on GitHub, meant to model the basics of GitHub's permissions system.
The app uses the `django-oso` authorization library to model and enforce this system. For more information on oso, check out our docs.

The data model is based on the B2B features of GitHub (it does not cover the B2C features).
It includes the following models.

### Resource Models

The app has the following models:

- `Organization`
  - Organizations are the top-level grouping of users and resources in the app. As with the real GitHub, users can be in multiple Organizations, and may have different permission levels in each.
- `User`
- `Team`
- `Repository`
- `Issue`
- `OrganizationRole`
- `TeamRole`
- `RepositoryRole`

Model hierarchy:

```
       Organizations ------------> OrganizationRoles: - Owner
             |                                        - Member
    +---+----+--------+                               - Billing Manager
    |   |             |
    | Teams ---------------------> TeamRoles: - Maintainer
    |   |             |                       - Member
    |   |             |
    +---+---+    Repositories ---> RepositoryRoles: - Admin
    |       |         |                             - Maintain
  Users   Teams     Issues                          - Write
                                                    - Triage
                                                    - Read
```

## Authorization Patterns
