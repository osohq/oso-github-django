# DEPRECATED

We deprecated the legacy Oso open source library in December 2023. We have plans for the next open source release and we’re looking forward to getting feedback from the community leading up to that point. In the meantime, if you’re happy using the Oso open source library now, nothing needs to change – i.e., we are not end-of-lifing (EOL) the library and we’ll continue to provide support and critical bug fixes.

[This post](https://www.osohq.com/docs/oss/getting-started/deprecation.html) describes how we got here, what this change means for existing users, and what you can expect from Oso in the future. If you have questions, you can always reach out to us in our [community Slack](https://join-slack.osohq.com).

If you’re building authorization for more than one service or want to share a policy across multiple applications, read how to get started with [Oso Cloud](https://www.osohq.com/docs).

# Modeling GitHub permissions with Oso

This application is a sample application based on GitHub, meant to model the basics of GitHub's permissions system.
The app uses the `django-oso` [authorization library](https://docs.osohq.com/using/frameworks/django.html) to model and enforce this system. For more information on oso, check out our docs.

The data model is based on the B2B features of GitHub (it does not cover the B2C features).

## Application Data Model

The app has the following models:

- `Organization`
  - Organizations are the top-level grouping of users and resources in the app. As with the real GitHub, users can be in multiple Organizations, and may have different permission levels in each.
- `User`
  - GitHub users, built with Django's `AbstractUser` model. Users can have roles within Organizations, Teams, and Repositories.
- `Team`
  - Groups of users within an organizaiton. They can be nested. Teams can have roles within Repositories.
- `Repository`
  - GitHub repositories, each is associated with a single organization.
- `Issue`
  - GitHub issues; each is associated with a single repository.
- `OrganizationRole`
  - Roles scoped to organizations; each is associated with a single organizaiton.
  - Assigned to users through a many-to-many relationship.
  - The role levels are: Owner, Member, and Billing Manager.
- `TeamRole`
  - Roles scoped to teams; each is associated with a single team.
  - Assigned to users through a many-to-many relationship.
  - The role levels are: Maintainer, Member.
- `RepositoryRole`
  - Roles scoped to repositories; each is associated with a single repository.
  - The role levels are: Admin, Maintain, Write, Triage, Read.
  - Assigned to users through a many-to-many relationship.
  - Assigned to teams through a many-to-many relationship.

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

## Running the App

To run the application, complete the following steps:

1. Set up a virtual environment and install required packages

   ```
   $ python -m venv venv/

   $ pip install -r requirements.txt
   ```

2. Create the database

   ```
   $ python manage.py migrate
   ```

3. [OPTIONAL] Load the fixture data. This will create some seed data, as well as a superuser with the following credentials:
   username: admin
   password: ilikecats

   ```
   $ bash ./github/fixtures/load.sh
   ```

   If you don't load the fixture data, you will need to create your own superuser with

   ```
   $ python manage.py createsuperuser
   ```

4. Run the server

   ```
   $ python manage.py runserver
   ```

   Once the server is running, you can login to the admin dashboard (localhost:8000/admin) to view or create more sample data (and see the passwords for test users).

## Authorization Patterns

The permissions model for this app is based on [GitHub's real permissions system](https://docs.github.com/en/free-pro-team@latest/github/setting-up-and-managing-organizations-and-teams) for their B2B product.

In our [guide to role-based access control](https://docs.osohq.com/getting-started/rbac.html), we have laid out
common authorization patterns involving roles, and how to implement them using oso.
This application exemplifies several of the patterns from that guide, which we'll go over here.

### Resource-specific roles

All of the roles in this app are [resource-specific roles](https://docs.osohq.com/getting-started/rbac.html#resource-specific-roles). Resource-specific roles are roles that apply to one type of resource.
In this app, we have represented these roles as Django models that correspond to tables in the database.

Each role model has the following characteristics:

- Role name, one of a pre-defined set of roles (e.g., "Admin", "Read", "Write", etc.)
- Many-to-many relationship with users (`User`)
- Many-to-one (FK) relationship with the resource record the role applies to

The three types of resource-specific roles in the app are:

- `OrganizationRole`: roles scoped to `Organization` resources:
  - Owner, Member, Billing Manager
  - Users are related to organizations by having one of these roles.
  - Based on GitHub's [organization roles](https://docs.github.com/en/free-pro-team@latest/github/setting-up-and-managing-organizations-and-teams/managing-peoples-access-to-your-organization-with-roles)
- `TeamRole`: roles scoped to `Team` resources:
  - Maintainer, Member
  - Users are related to teams by having one of these roles.
  - Based on GitHub's [teams](https://docs.github.com/en/free-pro-team@latest/github/setting-up-and-managing-organizations-and-teams/organizing-members-into-teams)
- `RepositoryRole`: roles scoped to `Repository` resources:
  - Admin, Maintain, Write, Triage, Read
  - Users and teams are related to repositories by having one of these roles.
  - Based on GitHub's [repository permission levels](https://docs.github.com/en/free-pro-team@latest/github/setting-up-and-managing-organizations-and-teams/repository-permission-levels-for-an-organization)

> NOTE: in the roles guide, we distinguish between "Resource-specific roles" and "tenant-specific roles." However, in this app organizations are basically tenants and we refer to their roles as resource-specific. This is because in our data model, organizations are represented as Django models and have many-to-many relationships with users, just like teams and repositories. In this case, tenant-specific roles can be implemeneted as resource-specific roles. If tenancy is modeled differently, for example with a per-session tenant ID, then the tenant-specific roles section in the guide may be useful.

### Hierarchical roles

All of the roles in the app have some hierarchical element to them. [Hierarchical roles](https://docs.osohq.com/getting-started/rbac.html#role-hierarchies) inherit permissions from one another based on their position in the hierarchy. In the GitHub example, the following hierarchies apply:

Organization roles:

- **Owner** inherits from:
  - **Member**
  - **Billing Manager**

Team roles:

- **Maintainer** inherits from:
  - **Member**

Repository roles:

- **Admin** inherits from:
  - **Maintain** inherits from:
    - **Write** inherits from:
      - **Triage** inherits from:
        - **Read**

These hierarchies are implemented with the `inherits_role` rule in `github/policy/authorization.polar`.

### Using roles with user groups

Assigning roles to groups of users, rather than individual users, is a [common roles use case](https://docs.osohq.com/getting-started/rbac.html#group-roles). In this app, `RepositoryRole`s can be assigned to both users (`User`) and teams (`Team`) as the model has a many-to-many relationship with both models. This is an easy way to assign roles to users and groups. In the oso policy (`github/policy/authorization.polar`), we show how to cascade the permissions of a team's role to all the users in the team.

### Nested resources

We have three resource-specific roles in the application, but each of those resources has more resource types nested inside it. GitHub, like many apps, applies the roles associated with a top-level resource to the resources nested within that resource as well. For example, someone with the "Read" role in a repository should also be able to read all the repository's issues, even though the `Issue` model doesn't have an explict role associated with it.

This is implemented in the oso policy(`github/policy/authorization.polar`) with the `rbac_allow` and `resource_role_applies_to` rules.

The implementation in this policy is different from that shown in the roles guide, which demonstrates two other alternative implementations [here](https://docs.osohq.com/getting-started/rbac.html#resource-hierarchies-nested-resources).

## Demo Users

The users configured from the fixture data are:

```
username: admin
password: ilikecats

username: john
password: strawberryfields

username: paul
password: strawberryfields

username: ringo
password: beatles123

username: mike
password: monsters123

username: sully
password: monsters123
```

where `admin` is the django superuser.
