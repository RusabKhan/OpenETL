import { ApiAuthParams, DatabaseAuthParams } from "@/types/auth_params";

export function capitalizeFirstLetter(str: string) {
  if (!str) return ""; // Handle empty or null strings
  return str.charAt(0).toUpperCase() + str.slice(1).toLowerCase();
}

export function isValidAuthParams(
  params: unknown,
): params is DatabaseAuthParams | ApiAuthParams {
  // Implement your validation logic
  return (
    typeof params === "object" &&
    params !== null &&
    ("username" in params || "token" in params)
  );
}

export const getCurrentTime = () => {
  const now = new Date();
  const hours = String(now.getHours()).padStart(2, "0");
  const minutes = String(now.getMinutes()).padStart(2, "0");
  const seconds = String(now.getSeconds()).padStart(2, "0");

  return `${hours}:${minutes}:${seconds}`;
};

export const getCurrentDate = () => {
  const now = new Date();

  // Format date as YYYY-MM-DD
  const year = now.getFullYear();
  const month = String(now.getMonth() + 1).padStart(2, "0"); // Months are 0-indexed
  const day = String(now.getDate()).padStart(2, "0");

  return `${year}-${month}-${day}`;
};
