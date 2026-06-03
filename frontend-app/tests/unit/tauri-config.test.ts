import { describe, expect, it } from "vitest";
import fs from "node:fs";
import path from "node:path";

const repoRoot = path.resolve(__dirname, "../../..");

describe("Tauri desktop package config", () => {
  it("uses frontend build output and localhost-only connectivity", () => {
    const config = JSON.parse(fs.readFileSync(path.join(repoRoot, "src-tauri/tauri.conf.json"), "utf8"));
    expect(config.build.beforeBuildCommand).toBe("cd ../frontend-app && npm run build");
    expect(config.build.beforeDevCommand).toBe("cd ../frontend-app && npm run dev -- --port 5173");
    expect(config.build.frontendDist).toBe("../frontend-app/dist");
    expect(config.build.devUrl).toBe("http://127.0.0.1:5173");
    expect(config.app.security.csp).toContain("http://localhost:*");
    expect(config.app.security.csp).toContain("http://127.0.0.1:*");
  });

  it("keeps permissions minimal", () => {
    const capability = JSON.parse(fs.readFileSync(path.join(repoRoot, "src-tauri/capabilities/default.json"), "utf8"));
    expect(capability.permissions).toEqual(["core:default"]);
  });
});
