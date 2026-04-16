import { clsx, type ClassValue } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export const toHex = (n: bigint): string => {
  return "0x" + n.toString(16);
};

export const toBigInt = (s: string): bigint => {
  try {
    if (!s) return 0n;
    return BigInt(s);
  } catch (e) {
    return 0n;
  }
};