import { Configuration, LogLevel, PublicClientApplication } from "@azure/msal-browser";

const TENANT_ID = import.meta.env.VITE_AZURE_AD_TENANT_ID || "";
const CLIENT_ID = import.meta.env.VITE_AZURE_AD_CLIENT_ID || "";

export const msalConfig: Configuration = {
  auth: {
    clientId: CLIENT_ID,
    authority: `https://login.microsoftonline.com/${TENANT_ID}`,
    redirectUri: window.location.origin,
    postLogoutRedirectUri: window.location.origin,
  },
  cache: {
    cacheLocation: "sessionStorage",
    storeAuthStateInCookie: false,
  },
  system: {
    loggerOptions: {
      logLevel: LogLevel.Warning,
    },
  },
};

export const loginRequest = {
  scopes: [`api://${CLIENT_ID}/access_as_user`],
};

// 単一インスタンス（AuthProvider と api.ts で共有）
export const msalInstance = new PublicClientApplication(msalConfig);
