package github.guard.keycloak;

import java.util.List;
import org.keycloak.authentication.Authenticator;
import org.keycloak.authentication.AuthenticatorFactory;
import org.keycloak.models.AuthenticationExecutionModel.Requirement;
import org.keycloak.models.KeycloakSession;
import org.keycloak.models.KeycloakSessionFactory;
import org.keycloak.provider.ProviderConfigProperty;

public class GithubOrgAuthenticatorFactory implements AuthenticatorFactory {
    public static final String ID = "github-org-guard";

    private static final List<ProviderConfigProperty> CONFIG = List.of(
        new ProviderConfigProperty("githubOrg", "GitHub Organization", "Org slug to enforce (default nidus-lab).", ProviderConfigProperty.STRING_TYPE, "nidus-lab"),
        new ProviderConfigProperty("githubServiceToken", "GitHub Service Token", "Optional PAT/App token with org membership read permission.", ProviderConfigProperty.PASSWORD, null)
    );

    @Override public String getId() { return ID; }
    @Override public String getDisplayType() { return "GitHub Organization Gate"; }
    @Override public String getReferenceCategory() { return "github"; }
    @Override public boolean isConfigurable() { return true; }
    @Override public List<ProviderConfigProperty> getConfigProperties() { return CONFIG; }
    @Override public Requirement[] getRequirementChoices() { return new Requirement[]{Requirement.REQUIRED}; }
    @Override public Authenticator create(KeycloakSession session) { return new GithubOrgAuthenticator(); }
    @Override public void init(org.keycloak.Config.Scope scope) {}
    @Override public void postInit(KeycloakSessionFactory factory) {}
    @Override public boolean isUserSetupAllowed() { return false; }
    @Override public void close() {}
    @Override public String getHelpText() { return "Restricts GitHub identity brokering to members of a specific organization."; }
}
