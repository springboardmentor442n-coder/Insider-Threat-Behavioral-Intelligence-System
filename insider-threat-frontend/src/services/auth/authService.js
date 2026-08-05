import api from "../../lib/axios";
import tokenService from "./tokenService";

export const authService = {
  async login(username, password) {
    const body = new URLSearchParams();

    body.append("username", username);
    body.append("password", password);

    const response = await api.post(
      "/auth/login",
      body,
      {
        headers: {
          "Content-Type":
            "application/x-www-form-urlencoded",
        },
      }
    );

    tokenService.setAccessToken(
      response.data.access_token
    );

    return response.data;
  },

  async me() {
    const response = await api.get("/auth/me");
    return response.data;
  },

  logout() {
    tokenService.clearTokens();
  },
};

export default authService;
