package role.assign.keycloak;

import java.util.List;
import org.keycloak.authentication.Authenticator;
import org.keycloak.authentication.AuthenticatorFactory;
import org.keycloak.models.AuthenticationExecutionModel.Requirement;
import org.keycloak.models.KeycloakSession;
import org.keycloak.models.KeycloakSessionFactory;
import org.keycloak.provider.ProviderConfigProperty;

public class RoleAutoAssignerAuthenticatorFactory implements AuthenticatorFactory {
    public static final String ID = "role-auto-assigner";

    private static final List<ProviderConfigProperty> CONFIG = List.of(
        new ProviderConfigProperty("roles", "Roles to Assign", "Comma-separated list of roles to automatically assign to the user (e.g., 'role1, client1:role2').", ProviderConfigProperty.STRING_TYPE, "")
    );

    @Override public String getId() { return ID; }
    @Override public String getDisplayType() { return "Role Auto-Assigner"; }
    @Override public String getReferenceCategory() { return "role"; }
    @Override public boolean isConfigurable() { return true; }
    @Override public List<ProviderConfigProperty> getConfigProperties() { return CONFIG; }
    @Override public Requirement[] getRequirementChoices() { return new Requirement[]{Requirement.REQUIRED, Requirement.ALTERNATIVE, Requirement.DISABLED}; }
    @Override public Authenticator create(KeycloakSession session) { return new RoleAutoAssignerAuthenticator(); }
    @Override public void init(org.keycloak.Config.Scope scope) {}
    @Override public void postInit(KeycloakSessionFactory factory) {}
    @Override public boolean isUserSetupAllowed() { return false; }
    @Override public void close() {}
    @Override public String getHelpText() { return "Automatically assigns specified roles to the user during the authentication flow."; }
}
