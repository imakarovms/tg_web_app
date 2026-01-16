// src/telegram.d.ts
interface WebAppUser {
  id: number;
  first_name: string;
  last_name?: string;
  username?: string;
  language_code?: string;
  is_premium?: boolean;
  allows_write_to_pm?: boolean;
  photo_url?: string;
}

interface WebAppChat {
  id: number;
  type: string;
  title?: string;
  username?: string;
  photo_url?: string;
}

interface WebAppInitDataUnsafe {
  query_id?: string;
  user?: WebAppUser;
  chat?: WebAppChat;
  chat_type?: string;
  chat_instance?: string;
  start_param?: string;
  auth_date: number;
  hash: string;
}

interface MainButton {
  text: string;
  color: string;
  textColor: string;
  isVisible: boolean;
  isActive: boolean;
  isProgressVisible: boolean;
  
  setText(text: string): void;
  setColor(color: string): void;
  setTextColor(color: string): void;
  show(): void;
  hide(): void;
  enable(): void;
  disable(): void;
  showProgress(loading?: boolean): void;
  hideProgress(): void;
  onClick(callback: () => void): void;
  offClick(callback: () => void): void;
}

interface BackButton {
  isVisible: boolean;
  
  show(): void;
  hide(): void;
  onClick(callback: () => void): void;
  offClick(callback: () => void): void;
}

interface WebApp {
  initData: string;
  initDataUnsafe: WebAppInitDataUnsafe;
  version: string;
  platform: string;
  colorScheme: 'light' | 'dark';
  themeParams: {
    bg_color?: string;
    text_color?: string;
    hint_color?: string;
    link_color?: string;
    button_color?: string;
    button_text_color?: string;
  };
  isExpanded: boolean;
  viewportHeight: number;
  viewportStableHeight: number;
  viewportWidth: number;
  isClosingConfirmationEnabled: boolean;
  
  // Методы
  ready(): void;
  expand(): void;
  close(): void;
  sendData(data: string): void;
  enableClosingConfirmation(): void;
  disableClosingConfirmation(): void;
  showAlert(message: string, callback?: () => void): void;
  showConfirm(message: string, callback: (confirmed: boolean) => void): void; // <-- ДОБАВЛЕН ТИП ДЛЯ CALLBACK
  
  onEvent(eventType: string, eventHandler: (event: any) => void): void;
  offEvent(eventType: string, eventHandler: (event: any) => void): void;
  
  // Theme
  onThemeChange(callback: (theme: any) => void): void;
  offThemeChange(callback: (theme: any) => void): void;
  
  // Viewport
  onViewportChanged(callback: () => void): void;
  offViewportChanged(callback: () => void): void;
  
  // Buttons
  MainButton: MainButton;
  BackButton: BackButton;
}

declare global {
  interface Window {
    Telegram?: {
      WebApp?: WebApp;
    };
  }
}

export {};