import createClient from "openapi-fetch";
import type { paths } from "~/types/api";

let _api: ReturnType<typeof createClient<paths>> | null = null;

export function useApi() {
  if (!_api) {
    _api = createClient<paths>({
      baseUrl: useRuntimeConfig().public.apiBase,
      fetch: globalThis.fetch,
      credentials: "include",
    });
  }
  return _api;
}
