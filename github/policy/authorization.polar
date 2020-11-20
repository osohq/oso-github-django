
# RBAC BASE POLICY

allow(user: github::User, action: String, resource) if
    rbac_allow(user, action, resource);

# rbac allow for resource-scoped roles to apply to the same resource
rbac_allow(user: github::User, action: String, resource) if
    user_in_role(user, role, resource) and
    role_allow(role, action, resource);

# rbac allow to let Repository roles have permissions on their child Issues
# TODO: improve, maybe this looks like a mixin for nested resources, with abstract `parent` fields
rbac_allow(user: github::User, action: String, issue: github::Issue) if
    user_in_role(user, role, issue.repository) and
    role_allow(role, action, issue);

# rbac allow to let Organization roles have permissions on their child Repositories
# TODO: improve
rbac_allow(user: github::User, action: String, repo: github::Repository) if
    user_in_role(user, role, repo.organization) and
    role_allow(role, action, repo);

# USER-ROLE RELATIONSHIPS

## Organization Roles

### User role source: direct mapping between users and organization roles
user_in_role(user: github::User, role, org: github::Organization) if
    # role is an OrganizationRole object
    role in github::OrganizationRole.objects.filter(users: user, organization: org);

### TODO: maybe another role source is being the creator of an organization -> owner role?


## Organization Helpers

### User in organization
user_in_org(user: github::User, org: github::Organization) if
    user_in_role(user, role, org) and
    # check that role came back bound, so the user has at least one role on the org
    role matches github::OrganizationRole;


## Team Roles

### User role source: direct mapping between users and team roles
user_in_role(user: github::User, role, team: github::Team) if
    role in github::TeamRole.objects.filter(users: user, team: team);

## Team Helpers

### Get user's teams
get_user_teams(user: github::User, team) if
    team in github::Team.objects.filter(teamrole__users__in=user);

## Repository Roles

### User role source: direct mapping between users and repository roles
user_in_role(user: github::User, role, repo: github::Repository) if
    # role is a RepositoryRole object
    role in github::RepositoryRole.objects.filter(users: user, repository: repo);

### Team role source: direct mapping between teams and repository roles
team_in_role(team: github::Team, role, repo: github::Repository) if
    role in github::RepositoryRole.objects.filter(teams: team, repository: repo);

### User role source: organization base role
user_in_role(user: github::User, role, repo: github::Repository) if
    user_in_org(user, repo.organization) and
    role = new RepositoryRole(name: org.base_role, repository: repo);

### User role source: team role
user_in_role(user: github::User, role, repo: github::Repository) if
    get_user_teams(user, team) and
    team_in_role(team, role, repo);


# ROLE-PERMISSION RELATIONSHIPS

## Repository Permissions

### TODO: map these to HTTP requests?
### Read role can read repositories
role_allow(role: RepositoryRole{name: "Read", repository: repo}, "read", repo: github::Repository);


# ROLE-ROLE RELATIONSHIPS

## Role Hierarchies

### Grant a role permissions that it inherits from a more junior role
role_allow(role, action, resource) if
    inherits_role(role, inherited_role) and
    role_allow(inherited_role, action, resource);

### Role inheritance for repository roles
inherits_role(role: github::RepositoryRole, inherited_role) if
    inherits_repository_role(role.name, inherited_role_name) and
    inherited_role = new github::RepositoryRole(name: inherited_role_name, repository: role.repository);

# TODO: this doesn't feel like the ideal way to express this hierarchy, quite redundant
inherits_repository_role("Admin", "Maintain");
inherits_repository_role("Maintain", "Write");
inherits_repository_role("Write", "Triage");
inherits_repository_role("Triage", "Read");


### Role inheritance for organization roles
inherits_role(role: github::OrganizationRole, inherited_role) if
    inherits_org_role(role.name, inherited_role_name) and
    inherited_role = new github::OrganizationRole(name: inherited_role_name, organization: role.organization);

inherits_org_role("Owner", "Member");
inherits_org_role("Owner", "Billing");

### Role inheritance for team roles
inherits_role(role: github::TeamRole, inherited_role) if
    inherits_team_role(role.name, inherited_role_name) and
    inherited_role = new github::TeamRole(name: inherited_role_name, team: role.team);

inherits_team_role("Maintainer", "Member");




######## NOTES ###########
# Actor types:
# - users
# - user groups
#
# Role scope types:
# - resources (e.g. repositories)
# - resource groups OR tenants (e.g. organizations)
#   - are tenants only relevant as resource groups? E.g. an organization groups repositories?
#   - are resource groups just resources with nested resources inside them?
#
# - `user_in_role` is only being used to get roles, and won't work properly to check roles, since
#    roles are django models, not Strings. Should we explicitly name them `get_user_role`?
#   - related: would be helpfult to mark an unbound variable with a specializer
