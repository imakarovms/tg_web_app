<script setup lang="ts">
import { onMounted, ref, onUnmounted, computed } from 'vue';
import { RouterLink, RouterView } from 'vue-router';

// Проверка режима разработки через process.env
const isDevMode = import.meta.env.DEV;

// Инициализация Telegram WebApp
onMounted(() => {
  // Безопасное получение Telegram WebApp
  const tg = (window as any).Telegram?.WebApp;
  if (tg) {
    try {
      // Говорим Telegram, что приложение готово
      tg.ready?.();
      
      // Расширяем приложение на полный экран
      tg.expand?.();
      
      // Включаем подтверждение при закрытии (если метод поддерживается)
      if (tg.enableClosingConfirmation) {
        tg.enableClosingConfirmation();
      }
      
      // Обработка изменения темы
      const themeChangeHandler = (newTheme: any) => updateTheme(newTheme);
      tg.onThemeChange?.(themeChangeHandler);
      
      // Применяем текущую тему
      updateTheme(tg.themeParams || {});
      
      // Очистка обработчиков при размонтировании компонента
      onUnmounted(() => {
        tg.offThemeChange?.(themeChangeHandler);
      });
    } catch (error) {
      console.error('Ошибка инициализации Telegram WebApp:', error);
    }
  } else {
    console.warn('Telegram WebApp не обнаружен. Используется мок-объект для разработки.');
    // Применяем тему по умолчанию для разработки
    updateTheme({
      bg_color: '#ffffff',
      text_color: '#222222',
      hint_color: '#aaaaaa',
      link_color: '#2678b6',
      button_color: '#3390ec',
      button_text_color: '#ffffff'
    });
  }
});

// Обновление темы приложения
const updateTheme = (theme: Record<string, any>) => {
  document.documentElement.style.setProperty('--tg-theme-bg-color', theme.bg_color || '#ffffff');
  document.documentElement.style.setProperty('--tg-theme-text-color', theme.text_color || '#222222');
  document.documentElement.style.setProperty('--tg-theme-hint-color', theme.hint_color || '#aaaaaa');
  document.documentElement.style.setProperty('--tg-theme-link-color', theme.link_color || '#2678b6');
  document.documentElement.style.setProperty('--tg-theme-button-color', theme.button_color || '#3390ec');
  document.documentElement.style.setProperty('--tg-theme-button-text-color', theme.button_text_color || '#ffffff');
  
  // Установка цветовой схемы
  const tg = (window as any).Telegram?.WebApp;
  const colorScheme = tg?.colorScheme || 'light';
  document.documentElement.setAttribute('data-theme', colorScheme);
  document.documentElement.style.backgroundColor = theme.bg_color || '#ffffff';
  document.documentElement.style.color = theme.text_color || '#222222';
};

// Безопасное получение глобального объекта window
const getWindow = () => {
  if (typeof window !== 'undefined') {
    return window;
  }
  // Для SSR возвращаем мок-объект
  return {
    innerHeight: 768,
    addEventListener: () => {},
    removeEventListener: () => {},
    matchMedia: () => ({ matches: false, addEventListener: () => {}, removeEventListener: () => {} })
  } as any;
};

// Для отладки в браузере (без Telegram)
if (isDevMode && !(getWindow() as any).Telegram) {
  // Создаем мок-объект Telegram WebApp
  const mockMainButton = {
    text: 'Готово',
    color: '#3390ec',
    backgroundColor: '#3390ec',
    textColor: '#ffffff',
    isVisible: false,
    isActive: true,
    isProgressVisible: false,
    
    setText: function(text: string) { 
      this.text = text; 
      console.log('MainButton text set:', text);
      return this;
    },
    setColor: function(color: string) { 
      this.color = color; 
      this.backgroundColor = color;
      console.log('MainButton color set:', color);
      return this;
    },
    setTextColor: function(color: string) { 
      this.textColor = color;
      console.log('MainButton text color set:', color);
      return this;
    },
    show: function() { 
      this.isVisible = true; 
      console.log('MainButton shown');
      return this;
    },
    hide: function() { 
      this.isVisible = false; 
      console.log('MainButton hidden');
      return this;
    },
    enable: function() { 
      this.isActive = true; 
      console.log('MainButton enabled');
      return this;
    },
    disable: function() { 
      this.isActive = false; 
      console.log('MainButton disabled');
      return this;
    },
    showProgress: function(loading = true) { 
      this.isProgressVisible = loading; 
      console.log('MainButton progress shown');
      return this;
    },
    hideProgress: function() { 
      this.isProgressVisible = false; 
      console.log('MainButton progress hidden');
      return this;
    },
    onClick: function(callback: () => void) { 
      console.log('MainButton click handler added');
      // Эмулируем клик для разработки
      getWindow().document.addEventListener('keydown', (e: KeyboardEvent) => {
        if (e.key === 'Enter' && this.isVisible && this.isActive) {
          callback();
        }
      });
      return this;
    },
    offClick: function(callback: () => void) { 
      console.log('MainButton click handler removed');
      return this;
    }
  };

  (getWindow() as any).Telegram = {
    WebApp: {
      initData: '',
      initDataUnsafe: {
        user: {
          id: 123456789,
          first_name: 'Тест',
          last_name: 'Пользователь',
          username: 'test_user',
          language_code: 'ru',
          is_premium: false
        },
        auth_date: Math.floor(Date.now() / 1000),
        hash: 'mock_hash_for_development'
      },
      version: '7.8',
      platform: getWindow().navigator?.platform?.includes('iPhone') ? 'ios' : 'tdesktop',
      colorScheme: getWindow().matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light',
      themeParams: {
        bg_color: '#ffffff',
        text_color: '#222222',
        hint_color: '#aaaaaa',
        link_color: '#2678b6',
        button_color: '#3390ec',
        button_text_color: '#ffffff'
      },
      isExpanded: true,
      viewportHeight: getWindow().innerHeight,
      viewportStableHeight: getWindow().innerHeight,
      viewportWidth: getWindow().innerWidth,
      isClosingConfirmationEnabled: false,
      
      ready: () => console.log('Telegram WebApp mock: ready'),
      expand: () => {
        console.log('Telegram WebApp mock: expanded');
        (getWindow() as any).Telegram.WebApp.isExpanded = true;
      },
      close: () => {
        console.log('Telegram WebApp mock: closed');
        if (confirm('Закрыть приложение?')) {
          // Эмуляция закрытия
        }
      },
      sendData: (data: string) => console.log('Telegram WebApp mock: send data to bot:', data),
      enableClosingConfirmation: () => {
        console.log('Telegram WebApp mock: closing confirmation enabled');
        (getWindow() as any).Telegram.WebApp.isClosingConfirmationEnabled = true;
      },
      disableClosingConfirmation: () => {
        console.log('Telegram WebApp mock: closing confirmation disabled');
        (getWindow() as any).Telegram.WebApp.isClosingConfirmationEnabled = false;
      },
      
      // Методы для работы с кнопками
      BackButton: {
        isVisible: false,
        show: function() { this.isVisible = true; console.log('BackButton shown'); return this; },
        hide: function() { this.isVisible = false; console.log('BackButton hidden'); return this; },
        onClick: function(callback: () => void) { console.log('BackButton click handler added'); return this; },
        offClick: function(callback: () => void) { console.log('BackButton click handler removed'); return this; }
      },
      
      // Добавляем недостающий метод showAlert
      showAlert: (message: string, callback?: () => void) => {
        alert(`[DEV MODE] ${message}`);
        callback?.();
        console.log('Telegram WebApp mock: showAlert:', message);
      },
      
      // Дополнительные методы для полной эмуляции
      openLink: (url: string) => {
        console.log('Telegram WebApp mock: open link', url);
        getWindow().open(url, '_blank');
      },
      openInvoice: (url: string) => {
        console.log('Telegram WebApp mock: open invoice', url);
        alert(`[DEV MODE] Invoice would open: ${url}`);
      },
      shareToStory: (mediaUrl: string, text?: string) => {
        console.log('Telegram WebApp mock: share to story', { mediaUrl, text });
        alert(`[DEV MODE] Would share to story: ${mediaUrl}`);
      },
      
      onEvent: (eventType: string, eventHandler: (event: any) => void) => {
        console.log('Telegram WebApp mock: Event listener added:', eventType);
        return (getWindow() as any).Telegram.WebApp;
      },
      offEvent: (eventType: string, eventHandler: (event: any) => void) => {
        console.log('Telegram WebApp mock: Event listener removed:', eventType);
        return (getWindow() as any).Telegram.WebApp;
      },
      
      onThemeChange: (callback: (theme: any) => void) => {
        console.log('Telegram WebApp mock: Theme change listener added');
        // Эмулируем изменение темы при переключении системы
        const mediaQuery = getWindow().matchMedia('(prefers-color-scheme: dark)');
        const themeChangeHandler = () => {
          (getWindow() as any).Telegram.WebApp.colorScheme = mediaQuery.matches ? 'dark' : 'light';
          (getWindow() as any).Telegram.WebApp.themeParams = mediaQuery.matches ? {
            bg_color: '#1a1a1a',
            text_color: '#f5f5f5',
            hint_color: '#888888',
            link_color: '#4da6ff',
            button_color: '#2a7ae8',
            button_text_color: '#ffffff'
          } : {
            bg_color: '#ffffff',
            text_color: '#222222',
            hint_color: '#aaaaaa',
            link_color: '#2678b6',
            button_color: '#3390ec',
            button_text_color: '#ffffff'
          };
          callback((getWindow() as any).Telegram.WebApp.themeParams);
        };
        
        mediaQuery.addEventListener('change', themeChangeHandler);
        callback((getWindow() as any).Telegram.WebApp.themeParams);
        
        // Сохраняем обработчик для удаления позже
        (getWindow() as any).Telegram.WebApp._themeChangeHandler = themeChangeHandler;
        return (getWindow() as any).Telegram.WebApp;
      },
      offThemeChange: (callback: (theme: any) => void) => {
        console.log('Telegram WebApp mock: Theme change listener removed');
        const mediaQuery = getWindow().matchMedia('(prefers-color-scheme: dark)');
        mediaQuery.removeEventListener('change', (getWindow() as any).Telegram.WebApp._themeChangeHandler);
        return (getWindow() as any).Telegram.WebApp;
      },
      
      onViewportChanged: (callback: () => void) => {
        console.log('Telegram WebApp mock: Viewport change listener added');
        // Эмулируем изменение viewport при изменении размера окна
        const resizeHandler = () => {
          (getWindow() as any).Telegram.WebApp.viewportHeight = getWindow().innerHeight;
          (getWindow() as any).Telegram.WebApp.viewportWidth = getWindow().innerWidth;
          callback();
        };
        
        getWindow().addEventListener('resize', resizeHandler);
        callback();
        
        // Сохраняем обработчик для удаления позже
        (getWindow() as any).Telegram.WebApp._viewportChangeHandler = resizeHandler;
        return (getWindow() as any).Telegram.WebApp;
      },
      offViewportChanged: (callback: () => void) => {
        console.log('Telegram WebApp mock: Viewport change listener removed');
        getWindow().removeEventListener('resize', (getWindow() as any).Telegram.WebApp._viewportChangeHandler);
        return (getWindow() as any).Telegram.WebApp;
      },
      
      // MainButton с поддержкой цепочки вызовов
      MainButton: mockMainButton
    }
  };
  
  console.log('✅ Telegram WebApp mock initialized for development');
}

// Создаем вычисляемые свойства для доступа к Telegram WebApp
const telegramWebApp = computed(() => {
  return (window as any).Telegram?.WebApp;
});

const isTelegramExpanded = computed(() => {
  return !!telegramWebApp.value?.isExpanded;
});

const telegramVersion = computed(() => {
  return telegramWebApp.value?.version || '';
});

const telegramPlatform = computed(() => {
  return telegramWebApp.value?.platform || '';
});
</script>

<template>
  <div class="app-container" :data-expanded="isTelegramExpanded">
    <header class="app-header">
      <div class="header-content">
        <h1>📝 Todo App</h1>
          <nav class="nav-tabs">
            <RouterLink to="/" class="nav-link" active-class="active">Каталог</RouterLink>
            <RouterLink to="/cart" class="nav-link" active-class="active">Корзина</RouterLink>
            <RouterLink to="/profile" class="nav-link" active-class="active">Профиль</RouterLink>
          </nav>
      </div>
    </header>

    <main class="app-content">
      <RouterView />
    </main>

    <footer class="app-footer">
      <div class="footer-content">
        <p>Telegram Mini App • Todo List</p>
        <p v-if="telegramWebApp" class="version-info">
          Версия: {{ telegramVersion }} • Платформа: {{ telegramPlatform }}
        </p>
      </div>
    </footer>
  </div>
</template>

<style scoped>
:root {
  --tg-theme-bg-color: #ffffff;
  --tg-theme-text-color: #222222;
  --tg-theme-hint-color: #aaaaaa;
  --tg-theme-link-color: #2678b6;
  --tg-theme-button-color: #3390ec;
  --tg-theme-button-text-color: #ffffff;
  --tg-section-bg-color: rgba(0, 0, 0, 0.03);
  
  --border-radius: 12px;
  --shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  --transition: all 0.3s ease;
  --header-height: 70px;
}

[data-theme="dark"] {
  --tg-theme-bg-color: #1a1a1a;
  --tg-theme-text-color: #f5f5f5;
  --tg-theme-hint-color: #888888;
  --tg-section-bg-color: rgba(255, 255, 255, 0.05);
}

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
  background-color: var(--tg-theme-bg-color);
  color: var(--tg-theme-text-color);
  line-height: 1.6;
  min-height: 100vh;
  padding: env(safe-area-inset-top) env(safe-area-inset-right) env(safe-area-inset-bottom) env(safe-area-inset-left);
  transition: background-color 0.3s, color 0.3s;
}

.app-container {
  max-width: 100%;
  margin: 0 auto;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background-color: var(--tg-theme-bg-color);
  color: var(--tg-theme-text-color);
}

.app-header {
  background-color: var(--tg-theme-bg-color);
  border-bottom: 1px solid rgba(0, 0, 0, 0.1);
  padding: 16px;
  position: sticky;
  top: env(safe-area-inset-top);
  z-index: 100;
  box-shadow: var(--shadow);
}

.header-content {
  max-width: 600px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 100%;
}

.app-header h1 {
  font-size: 1.8rem;
  font-weight: 700;
  margin-bottom: 12px;
  color: var(--tg-theme-text-color);
  text-align: center;
}

.nav-tabs {
  display: flex;
  width: 100%;
  justify-content: center;
  gap: 12px;
  flex-wrap: wrap;
}

.nav-link {
  padding: 8px 16px;
  border-radius: var(--border-radius);
  text-decoration: none;
  color: var(--tg-theme-text-color);
  font-weight: 500;
  transition: var(--transition);
  text-align: center;
  flex: 1;
  max-width: 150px;
}

.nav-link.active,
.nav-link:hover {
  background-color: rgba(51, 144, 236, 0.15);
  color: var(--tg-theme-button-color);
  box-shadow: 0 2px 4px rgba(51, 144, 236, 0.2);
}

.app-content {
  flex: 1;
  padding: 20px;
  max-width: 600px;
  margin: 0 auto;
  width: 100%;
}

.app-footer {
  background-color: var(--tg-theme-bg-color);
  border-top: 1px solid rgba(0, 0, 0, 0.1);
  padding: 16px;
  text-align: center;
  margin-top: auto;
}

.footer-content {
  max-width: 600px;
  margin: 0 auto;
  color: var(--tg-theme-hint-color);
  font-size: 0.85rem;
}

.version-info {
  font-size: 0.75rem;
  margin-top: 4px;
  opacity: 0.8;
}

/* Стили для кнопок Telegram */
.tg-button {
  background-color: var(--tg-theme-button-color);
  color: var(--tg-theme-button-text-color);
  border: none;
  border-radius: var(--border-radius);
  padding: 12px 24px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: var(--transition);
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.15);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  max-width: 300px;
  margin: 8px auto;
}

.tg-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

.tg-button:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
}

.tg-button:active:not(:disabled) {
  transform: translateY(0);
}

/* Кнопка с прозрачным фоном */
.tg-button-outline {
  background-color: transparent;
  border: 2px solid var(--tg-theme-button-color);
  color: var(--tg-theme-button-color);
}

.tg-button-outline:hover:not(:disabled) {
  background-color: rgba(51, 144, 236, 0.1);
}

/* Адаптивность */
@media (max-width: 768px) {
  .app-header {
    padding: 12px;
  }
  
  .app-header h1 {
    font-size: 1.5rem;
    margin-bottom: 8px;
  }
  
  .nav-tabs {
    gap: 6px;
  }
  
  .nav-link {
    padding: 6px 10px;
    font-size: 0.85rem;
    max-width: 120px;
  }
  
  .app-content {
    padding: 16px;
  }
  
  .tg-button {
    padding: 10px;
    font-size: 0.95rem;
  }
}

@media (max-width: 480px) {
  .nav-tabs {
    flex-direction: column;
    gap: 8px;
  }
  
  .nav-link {
    max-width: 100%;
  }
}

/* Стили для загрузки */
.loading {
  text-align: center;
  padding: 20px;
  color: var(--tg-theme-hint-color);
}

.loading-spinner {
  display: inline-block;
  width: 24px;
  height: 24px;
  border: 3px solid rgba(51, 144, 236, 0.3);
  border-radius: 50%;
  border-top-color: var(--tg-theme-button-color);
  animation: spin 1s linear infinite;
  margin-bottom: 8px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Стили для ошибок */
.error-message {
  background-color: rgba(239, 68, 68, 0.1);
  color: #ef4444;
  border: 1px solid #ef4444;
  padding: 12px;
  border-radius: var(--border-radius);
  margin-bottom: 16px;
  position: relative;
  padding-left: 32px;
}

.error-message:before {
  content: "⚠️";
  position: absolute;
  left: 10px;
  top: 50%;
  transform: translateY(-50%);
}

/* Стили для разделов */
.section-card {
  background-color: var(--tg-section-bg-color);
  border-radius: var(--border-radius);
  padding: 20px;
  margin-bottom: 16px;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.05);
}

/* Вспомогательные классы */
.text-center {
  text-align: center;
}

.mb-16 {
  margin-bottom: 16px;
}

.mt-8 {
  margin-top: 8px;
}

/* Главная кнопка Telegram */
.telegrams-main-button {
  position: fixed;
  bottom: 16px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 1000;
  width: 90%;
  max-width: 500px;
  transition: var(--transition);
}

[data-expanded="false"] .telegrams-main-button {
  opacity: 0.8;
  transform: translateX(-50%) scale(0.95);
}

/* Поддержка safe area для iOS */
@media (max-width: 768px) {
  body {
    padding-bottom: calc(env(safe-area-inset-bottom) + 16px);
  }
  
  .telegrams-main-button {
    bottom: calc(env(safe-area-inset-bottom) + 16px);
  }
}
</style>