import { ApiAuthParams, DatabaseAuthParams } from "../types/auth_params";

export function capitalizeFirstLetter(str: string) {
  if (!str) return ""; // Handle empty or null strings
  return str.charAt(0).toUpperCase() + str.slice(1).toLowerCase();
}

export function isValidAuthParams(
  params: unknown
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

export function formatNumber(num: number) {
  if (num >= 1000000000) {
    // For billions (e.g., 1.32B)
    return (num / 1000000000).toFixed(1).replace(/\.0$/, "") + "B";
  } else if (num >= 1000000) {
    // For millions (e.g., 1.32M)
    return (num / 1000000).toFixed(1).replace(/\.0$/, "") + "M";
  } else if (num >= 1000) {
    // For thousands (e.g., 13.2k)
    return (num / 1000).toFixed(1).replace(/\.0$/, "") + "k";
  } else {
    // For numbers below 1000
    return num.toString();
  }
}

export function formatDateTime(dateTimeString: string): string {
  const date = new Date(dateTimeString); // Convert the string into a Date object

  // Format the date and time
  const options: Intl.DateTimeFormatOptions = {
    year: "numeric",
    month: "long",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
    hour12: true,
  };

  return date.toLocaleString("en-US", options); // Convert to a human-readable format
}

export function extractInitials(input: string): string {
  const words = input.trim().split(" ");
  if (words.length === 1) {
    return words[0].charAt(0).toUpperCase(); // Return the first letter of the single word
  }
  return (
    words[0].charAt(0).toUpperCase() + words[1].charAt(0).toUpperCase() // Return the first letters of the first two words
  );
}
