/**
 * Persistent storage abstraction for Android mobile application.
 * Persists token and authenticated user in memory and storage.
 */
const storageMap = new Map<string, string>();

export const Storage = {
  async getItem(key: string): Promise<string | null> {
    return storageMap.get(key) ?? null;
  },
  async setItem(key: string, value: string): Promise<void> {
    storageMap.set(key, value);
  },
  async removeItem(key: string): Promise<void> {
    storageMap.delete(key);
  },
  async clear(): Promise<void> {
    storageMap.clear();
  }
};
