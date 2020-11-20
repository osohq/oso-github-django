
# enable rbac
allow(user: github::User, action: String, resource) if
    rbac_allow(user, action, resource);

# rbac allow for resource-scoped roles to apply to the same resource
rbac_allow(user: github::User, action: String, resource) if
    user_in_role(user, role, resource) and
    role_allow(role, action, resource);

# rbac allow to let Repository roles have permissions on their child Issues
# TODO: improve
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

### OrganizationRole source: direct mapping between users and organization roles
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

### TeamRole source: direct mapping between users and team roles
user_in_role(user: github::User, role, team: github::Team) if
    role in github::TeamRole.objects.filter(users: user, team: team);

## Team Helpers

### Get user's teams
get_user_teams(user: github::User, team) if
    team in github::Team.objects.filter(teamrole__users=user);

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
    user_in_team
    team_in_role(team, role, repo);





# it seems weird that the association between the role and the repository is happening
# in the `user_in_role` rule, rather than here. Feels like there should be some connection
# between the role and the resource in this rule.
role_allow(RepositoryRole{name: "R", repository: repo}, "read", repo: github::Repository);

# this is more clear, as an alternative to the `role_allow` structure.
# eliding `role_allow` might make more sense for resource-specific roles.
allow(user: github::User, "read", repo: github::Repository) if
    user_in_role(user, "R", repo);

allow(user: github::User, "view", repo: github::Repo) if
    user.permission


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