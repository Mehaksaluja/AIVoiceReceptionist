import * as VapiModule from "@vapi-ai/web/dist/vapi.js";

export type VapiConstructor = new (
  apiToken: string,
  apiBaseUrl?: string,
  dailyCallConfig?: Record<string, unknown>,
  dailyCallObject?: Record<string, unknown>,
) => VapiClient;

export type VapiClient = InstanceType<VapiConstructor>;

function unwrapModuleExport(mod: unknown): unknown {
  let current: unknown = mod;

  for (let depth = 0; depth < 5; depth += 1) {
    if (typeof current === "function") {
      return current;
    }

    if (!current || typeof current !== "object") {
      break;
    }

    const record = current as Record<string, unknown>;

    if (typeof record.Vapi === "function") {
      return record.Vapi;
    }

    if ("default" in record) {
      current = record.default;
      continue;
    }

    break;
  }

  return current;
}

export function resolveVapiConstructor(): VapiConstructor {
  const resolved = unwrapModuleExport(VapiModule);

  if (typeof resolved !== "function") {
    const shape =
      VapiModule && typeof VapiModule === "object"
        ? Object.keys(VapiModule).join(", ")
        : typeof VapiModule;

    throw new Error(
      `Voice SDK loaded but constructor was not found (saw: ${shape}). Stop and restart: npm run dev`,
    );
  }

  return resolved as VapiConstructor;
}

export async function loadVapiClient(): Promise<VapiConstructor> {
  return resolveVapiConstructor();
}
