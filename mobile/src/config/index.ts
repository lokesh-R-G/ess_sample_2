import { Platform } from 'react-native';

// For Android emulator, the host machine is 10.0.2.2.
// For physical Android devices connected to LAN or ADB reverse, adjust accordingly.
export const Config = {
  API_BASE_URL: Platform.select({
    android: 'http://10.0.2.2:8000/api',
    ios: 'http://localhost:8000/api',
    default: 'http://localhost:8000/api',
  }),
  TIMEOUT_MS: 15000,
  APP_NAME: 'ESS / HRMS Portal',
  VERSION: '1.0.0',
};
