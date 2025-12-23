package github.guard.keycloak;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import jakarta.ws.rs.core.Response;
import org.jboss.logging.Logger;
import org.keycloak.authentication.AuthenticationFlowContext;
import org.keycloak.authentication.AuthenticationFlowError;
import org.keycloak.authentication.Authenticator;
import org.keycloak.broker.provider.util.SimpleHttp;
import org.keycloak.models.KeycloakSession;
import org.keycloak.models.RealmModel;
import org.keycloak.models.UserModel;

public class GithubOrgAuthenticator implements Authenticator {
    private static final Logger logger = Logger.getLogger(GithubOrgAuthenticator.class);
    private static final ObjectMapper MAPPER = new ObjectMapper();

    @Override
    public void authenticate(AuthenticationFlowContext context) {
        var configModel = context.getAuthenticatorConfig();
        var config = (configModel != null) ? configModel.getConfig() : java.util.Collections.<String, String>emptyMap();
        var org = config.getOrDefault("githubOrg", "nidus-lab");
        var serviceToken = config.get("githubServiceToken");

        var authSession = context.getAuthenticationSession();
        var serializedCtx = authSession.getAuthNote("BROKERED_CONTEXT");
        if (serializedCtx == null) {
            logger.warn("Missing BROKERED_CONTEXT in auth session");
            fail(context, "Missing broker context");
            return;
        }

        try {
            var brokerCtx = MAPPER.readTree(serializedCtx);

            // Extract username - based on logs, modelUsername is at the root
            String userProfile = brokerCtx.path("modelUsername").asText(null);
            if (userProfile == null || userProfile.isBlank()) {
                userProfile = brokerCtx.path("brokerUsername").asText(null);
            }

            // Extract access token - based on logs, FEDERATED_ACCESS_TOKEN.data contains the clean token
            String accessToken = brokerCtx.path("contextData").path("FEDERATED_ACCESS_TOKEN").path("data").asText(null);

            // Fallback to parsing the 'token' field if FEDERATED_ACCESS_TOKEN is missing
            if (accessToken == null || accessToken.isBlank()) {
                String rawToken = brokerCtx.path("token").asText("");
                if (rawToken.contains("access_token=")) {
                    for (String part : rawToken.split("&")) {
                        if (part.startsWith("access_token=")) {
                            accessToken = part.substring("access_token=".length());
                            break;
                        }
                    }
                } else if (!rawToken.isBlank() && !rawToken.startsWith("{")) {
                    accessToken = rawToken;
                }
            }

            if (userProfile == null || userProfile.isBlank()) {
                logger.warnf("GitHub username is null in brokered context. Full context: %s", serializedCtx);
                fail(context, "No GitHub username provided.");
                return;
            }

            if (accessToken != null && !accessToken.isBlank()) {
                String maskedToken = accessToken.length() > 8
                    ? accessToken.substring(0, 4) + "..." + accessToken.substring(accessToken.length() - 4)
                    : "***";
                logger.infof("Verifying GitHub membership for user: %s in org: %s (token: %s)", userProfile, org, maskedToken);
            } else {
                logger.warnf("No GitHub token available for user: %s. Context: %s", userProfile, serializedCtx);
                fail(context, "No GitHub token available.");
                return;
            }

            SimpleHttp request = SimpleHttp.doGet(
                "https://api.github.com/orgs/" + org + "/memberships/" + userProfile,
                context.getSession()
            ).header("Accept", "application/vnd.github+json")
             .header("User-Agent", "Keycloak-Github-Org-Guard");

            if (serviceToken != null && !serviceToken.isBlank()) {
                logger.debug("Using service token for GitHub API request");
                request.header("Authorization", "Bearer " + serviceToken);
            } else if (accessToken != null && !accessToken.isBlank()) {
                logger.debug("Using user access token for GitHub API request");
                request.header("Authorization", "Bearer " + accessToken);
            } else {
                logger.warnf("No GitHub token available (neither service token nor user token). Context: %s", serializedCtx);
                fail(context, "No GitHub token available.");
                return;
            }

            var response = request.asResponse();
            logger.infof("GitHub API response status: %d", response.getStatus());

            if (response.getStatus() == 401) {
                String maskedToken = accessToken.length() > 8
                    ? accessToken.substring(0, 4) + "..." + accessToken.substring(accessToken.length() - 4)
                    : "***";
                logger.warnf("GitHub API 401 Unauthorized. Token used: %s. Full context: %s", maskedToken, serializedCtx);
            }

            if (response.getStatus() == 200) {
                JsonNode body = MAPPER.readTree(response.asString());
                String state = body.path("state").asText();
                logger.infof("GitHub membership state: %s", state);
                if ("active".equalsIgnoreCase(state)) {
                    context.success();
                    return;
                }
            }

            logger.warnf("GitHub membership verification failed for %s in %s. Status: %d", userProfile, org, response.getStatus());
            fail(context, "GitHub account is not an active member of " + org + ".");
        } catch (Exception e) {
            logger.error("Error verifying GitHub membership", e);
            fail(context, "Error verifying GitHub membership: " + e.getMessage());
        }
    }

    private void fail(AuthenticationFlowContext context, String message) {
        context.failure(AuthenticationFlowError.INVALID_USER,
            context.form().setError(message).createErrorPage(Response.Status.FORBIDDEN));
    }

    @Override public void action(AuthenticationFlowContext context) {}
    @Override public boolean requiresUser() { return false; }
    @Override public boolean configuredFor(KeycloakSession session, org.keycloak.models.RealmModel realmModel, UserModel userModel) { return false; }
    @Override public void setRequiredActions(KeycloakSession session, org.keycloak.models.RealmModel realmModel, UserModel userModel) {}
    @Override public void close() {}
}
