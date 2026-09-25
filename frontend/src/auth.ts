import {
  InMemoryWebStorage,
  UserManager,
  WebStorageStateStore,
} from "oidc-client-ts";
export interface PublicConfig {
  api: string;
  authority: string;
  clientId: string;
  authMode: "oidc" | "cognito";
}
export function manager(config: PublicConfig) {
  return new UserManager({
    authority: config.authority,
    client_id: config.clientId,
    redirect_uri: location.origin + "/",
    post_logout_redirect_uri: location.origin + "/",
    response_type: "code",
    scope: "openid profile",
    automaticSilentRenew: false,
    userStore: new WebStorageStateStore({ store: new InMemoryWebStorage() }),
    stateStore: new WebStorageStateStore({ store: sessionStorage }),
    loadUserInfo: false,
  });
}
