import { format, formatDistanceToNow, parseISO } from "date-fns";

export const formatDate = (date: string | Date): string => {
  const d = typeof date === "string" ? parseISO(date) : date;
  return format(d, "MMM dd, yyyy HH:mm");
};

export const formatRelative = (date: string | Date): string => {
  const d = typeof date === "string" ? parseISO(date) : date;
  return formatDistanceToNow(d, { addSuffix: true });
};

export const formatTimestamp = (date: string | Date): string => {
  const d = typeof date === "string" ? parseISO(date) : date;
  return format(d, "yyyy-MM-dd'T'HH:mm:ss'Z'");
};
