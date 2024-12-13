import { ApiAuthParams, DatabaseAuthParams } from "@/types/auth_params";

export function capitalizeFirstLetter(str: string) {
  if (!str) return ""; // Handle empty or null strings
  return str.charAt(0).toUpperCase() + str.slice(1).toLowerCase();
}

export function isValidAuthParams(params: unknown): params is DatabaseAuthParams | ApiAuthParams {
  // Implement your validation logic
  return typeof params === 'object' && params !== null &&
         ('username' in params || 'token' in params);
}