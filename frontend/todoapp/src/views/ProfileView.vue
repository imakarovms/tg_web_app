<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';

// Реактивные данные
const user = ref({
  id: '',
  name: '',
  completedTasks: 0,
  createdAt: ''
});
const loading = ref(true);
const error = ref<string | null>(null);
const tg = window.Telegram?.WebApp;

// Получение ID пользователя из Telegram
const tgUser = computed(() => tg?.initDataUnsafe?.user);

// Получение профиля
const fetchProfile = async () => {
  if (!tgUser.value?.id) return;
  
  loading.value = true;
  error.value = null;
  
  try {
    const response = await fetch(`http://localhost:8000/api/orders/${tgUser.value.id}`);
    
    if (!response.ok) {
      throw new Error(`Ошибка сервера: ${response.status}`);
    }
    
    const data = await response.json();
    
    // Обновление данных пользователя
    user.value = {
      id: tgUser.value.id.toString(),
      name: `${tgUser.value.first_name}${tgUser.value.last_name ? ` ${tgUser.value.last_name}` : ''}`,
      completedTasks: data.completedTasks || 0,
      createdAt: data.createdAt || new Date().toISOString()
    };
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Неизвестная ошибка при загрузке профиля';
    console.error('Ошибка загрузки профиля:', err);
  } finally {
    loading.value = false;
  }
};

// Настройка Main Button для Telegram
if (tg?.MainButton) {
  tg.MainButton.hide(); // Скрыть кнопку на странице профиля
}

onMounted(fetchProfile);
</script>

<template>
  <div class="profile-container">
    <h2 class="page-title">Мой профиль</h2>
    
    <!-- Отображение ошибок -->
    <div v-if="error" class="error-message">
      {{ error }}
    </div>
    
    <!-- Индикатор загрузки -->
    <div v-if="loading" class="loading">
      <div class="loading-spinner"></div>
      <p>Загрузка профиля...</p>
    </div>
    
    <!-- Профиль пользователя -->
    <div v-else class="profile-card">
      <div class="profile-header">
        <div class="avatar">
          <span v-if="tgUser?.photo_url">
            <img :src="tgUser.photo_url" alt="Аватар" class="avatar-img" />
          </span>
          <span v-else class="avatar-placeholder">
            {{ tgUser?.first_name?.charAt(0) || 'U' }}
          </span>
        </div>
        <div class="user-info">
          <h3 class="user-name">{{ user.name }}</h3>
          <p class="user-id">ID: {{ user.id }}</p>
        </div>
      </div>
      
      <div class="stats-container">
        <div class="stat-item">
          <div class="stat-value">{{ user.completedTasks }}</div>
          <div class="stat-label">Выполнено задач</div>
        </div>
        <div class="stat-item">
          <div class="stat-value">🎯</div>
          <div class="stat-label">Цель: 10 задач</div>
        </div>
      </div>
      
      <div class="profile-details">
        <div class="detail-item">
          <span class="detail-label">Дата регистрации:</span>
          <span class="detail-value">{{ new Date(user.createdAt).toLocaleDateString('ru-RU') }}</span>
        </div>
        <div class="detail-item">
          <span class="detail-label">Telegram:</span>
          <span class="detail-value">@{{ tgUser?.username || 'не указан' }}</span>
        </div>
        <div class="detail-item">
          <span class="detail-label">Язык:</span>
          <span class="detail-value">{{ tgUser?.language_code || 'ru' }}</span>
        </div>
      </div>
      
      <button class="refresh-button tg-button" @click="fetchProfile" :disabled="loading">
        {{ loading ? 'Обновление...' : 'Обновить данные' }}
      </button>
    </div>
    
    <div class="telegram-info">
      <p>Версия Telegram WebApp: {{ tg?.version }}</p>
      <p>Платформа: {{ tg?.platform }}</p>
    </div>
  </div>
</template>

