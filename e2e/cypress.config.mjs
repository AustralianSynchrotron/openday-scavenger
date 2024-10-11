import { defineConfig } from "cypress";

export default defineConfig({
  e2e: {
    baseUrl: "http://localhost:8000",
  },
  env: {
    admin_username: "admin",
    admin_password: "admin",
  },
});
