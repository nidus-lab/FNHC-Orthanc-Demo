package role.assign.keycloak;

import org.jboss.logging.Logger;
import org.keycloak.authentication.AuthenticationFlowContext;
import org.keycloak.authentication.Authenticator;
import org.keycloak.models.KeycloakSession;
import org.keycloak.models.RealmModel;
import org.keycloak.models.RoleModel;
import org.keycloak.models.UserModel;
import org.keycloak.models.utils.KeycloakModelUtils;

import java.util.Arrays;
import java.util.Set;
import java.util.stream.Collectors;

public class RoleAutoAssignerAuthenticator implements Authenticator {
    private static final Logger logger = Logger.getLogger(RoleAutoAssignerAuthenticator.class);

    @Override
    public void authenticate(AuthenticationFlowContext context) {
        UserModel user = context.getUser();
        if (user == null) {
            logger.warn("No user found in authentication flow context");
            context.success();
            return;
        }

        var configModel = context.getAuthenticatorConfig();
        var config = (configModel != null) ? configModel.getConfig() : java.util.Collections.<String, String>emptyMap();
        String rolesString = config.getOrDefault("roles", "");

        if (rolesString.isBlank()) {
            logger.debug("No roles configured for auto-assignment");
            context.success();
            return;
        }

        Set<String> rolesToAssign = Arrays.stream(rolesString.split(","))
                .map(String::trim)
                .filter(s -> !s.isEmpty())
                .collect(Collectors.toSet());

        RealmModel realm = context.getRealm();
        for (String roleName : rolesToAssign) {
            RoleModel role = realm.getRole(roleName);
            if (role == null) {
                // Try client role if it's in format client:role
                if (roleName.contains(":")) {
                    String[] parts = roleName.split(":", 2);
                    var client = realm.getClientByClientId(parts[0]);
                    if (client != null) {
                        role = client.getRole(parts[1]);
                    }
                }
            }

            if (role != null) {
                if (!user.hasRole(role)) {
                    logger.infof("Assigning role %s to user %s", roleName, user.getUsername());
                    user.grantRole(role);
                } else {
                    logger.debugf("User %s already has role %s", user.getUsername(), roleName);
                }
            } else {
                logger.warnf("Role %s not found in realm %s", roleName, realm.getName());
            }
        }

        context.success();
    }

    @Override public void action(AuthenticationFlowContext context) {}
    @Override public boolean requiresUser() { return true; }
    @Override public boolean configuredFor(KeycloakSession session, RealmModel realm, UserModel user) { return true; }
    @Override public void setRequiredActions(KeycloakSession session, RealmModel realm, UserModel user) {}
    @Override public void close() {}
}
