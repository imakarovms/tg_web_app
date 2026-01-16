<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';

// Реактивные данные
const cartItems = ref<any[]>([]);
const loading = ref(false);
const error = ref<string | null>(null);
const totalAmount = ref(0);
const tg = (window as any).Telegram?.WebApp;

// Получение ID пользователя из Telegram
const userId = computed(() => {
  return tg?.initDataUnsafe?.user?.id;
});

// Получение товаров корзины
const fetchCart = async () => {
  if (!userId.value) {
    console.warn('User ID not found, using mock data for development');
    // Мок-данные для разработки
    calculateTotal();
    return;
  }

  loading.value = true;
  error.value = null;
  
  try {
    const response = await fetch(`http://localhost:8000/api/cart/${userId.value}`);
    
    if (!response.ok) {
      throw new Error(`Ошибка сервера: ${response.status}`);
    }
    
    const data = await response.json();
    cartItems.value = Array.isArray(data) ? data : [];
    calculateTotal();
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Неизвестная ошибка при загрузке корзины';
    console.error('Ошибка загрузки корзины:', err);
    calculateTotal();
  } finally {
    loading.value = false;
  }
};

// Расчет общей суммы
const calculateTotal = () => {
  totalAmount.value = cartItems.value.reduce((sum, item) => {
    return sum + (item.price * item.quantity);
  }, 0);
};

// Изменение количества товара
const updateQuantity = async (itemId: number, newQuantity: number) => {
  if (newQuantity < 1) return;
  
  loading.value = true;
  error.value = null;
  
  try {
    // Найти товар в корзине
    const item = cartItems.value.find(i => i.id === itemId);
    if (!item) return;
    
    // Обновить локальное состояние
    item.quantity = newQuantity;
    calculateTotal();
    
    // Если пользователь авторизован, отправить на сервер
    if (userId.value) {
      await fetch(`http://localhost:8000/api/cart/${userId.value}/${itemId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ quantity: newQuantity }),
      });
    }
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Ошибка при обновлении количества';
    console.error('Ошибка обновления количества:', err);
  } finally {
    loading.value = false;
  }
};

// Удаление товара из корзины
const removeFromCart = async (itemId: number) => {
  loading.value = true;
  error.value = null;
  
  try {
    // Обновить локальное состояние
    cartItems.value = cartItems.value.filter(item => item.id !== itemId);
    calculateTotal();
    
    // Если пользователь авторизован, отправить на сервер
    if (userId.value) {
      await fetch(`http://localhost:8000/api/cart/${userId.value}/${itemId}`, {
        method: 'DELETE',
      });
      
      tg?.showAlert('Товар удален из корзины!');
    }
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Ошибка при удалении товара';
    console.error('Ошибка удаления товара:', err);
  } finally {
    loading.value = false;
  }
};

// Оформление заказа
const checkout = async () => {
  if (cartItems.value.length === 0) {
    tg?.showAlert('Ваша корзина пуста!');
    return;
  }
  
  if (!userId.value) {
    tg?.showAlert('Пожалуйста, авторизуйтесь в Telegram для оформления заказа!');
    return;
  }
  
  loading.value = true;
  error.value = null;
  
  try {
    // Показать подтверждение заказа
    const confirm = await new Promise<boolean>((resolve) => {
      tg?.showConfirm(
        `Ваш заказ на сумму ${totalAmount.value.toLocaleString('ru-RU')} ₽`,
        (confirmed: boolean) => resolve(confirmed) // <-- ИСПРАВЛЕНО: добавлен тип boolean
      );
    });
    
    if (!confirm) {
      tg?.showAlert('Оформление заказа отменено');
      return;
    }
    
    // Отправка заказа на сервер
    const response = await fetch(`http://localhost:8000/api/cart/${userId.value}/checkout`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        items: cartItems.value.map(item => ({
          id: item.id,
          quantity: item.quantity,
          price: item.price
        })),
        total: totalAmount.value
      }),
    });
    
    if (!response.ok) {
      throw new Error(`Ошибка оформления заказа: ${response.status}`);
    }
    
    const result = await response.json();
    
    // Очистка корзины
    cartItems.value = [];
    calculateTotal();
    
    // Отображение результата
    tg?.showAlert(`Заказ успешно оформлен! Номер заказа: ${result.orderId}`);
    
    // Закрытие приложения или переход к подтверждению
    setTimeout(() => {
      tg?.close();
    }, 2000);
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Ошибка при оформлении заказа';
    console.error('Ошибка оформления заказа:', err);
    tg?.showAlert('Произошла ошибка при оформлении заказа. Попробуйте еще раз.');
  } finally {
    loading.value = false;
  }
};

// Настройка Main Button для Telegram
if (tg?.MainButton) {
  tg.MainButton.setText('Оформить заказ');
  tg.MainButton.setColor('#4CAF50');
  
  if (cartItems.value.length > 0) {
    tg.MainButton.show();
    tg.MainButton.enable();
  } else {
    tg.MainButton.hide();
  }
  
  tg.MainButton.onClick(checkout);
}

// Загрузка данных при монтировании
onMounted(fetchCart);
</script>

<template>
  <div class="cart-container">
    <h2 class="page-title">🛒 Ваша корзина</h2>
    
    <!-- Отображение ошибок -->
    <div v-if="error" class="error-message">
      {{ error }}
    </div>
    
    <!-- Индикатор загрузки -->
    <div v-if="loading" class="loading">
      <div class="loading-spinner"></div>
      <p>Загрузка корзины...</p>
    </div>
    
    <!-- Корзина пуста -->
    <div v-else-if="cartItems.length === 0" class="empty-cart">
      <div class="empty-icon">🛒</div>
      <h3>Ваша корзина пуста</h3>
      <p>Добавьте товары для оформления заказа</p>
      <RouterLink to="/" class="browse-button tg-button">
        К каталогу товаров
      </RouterLink>
    </div>
    
    <!-- Список товаров -->
    <div v-else class="cart-items">
      <div 
        v-for="item in cartItems" 
        :key="item.id" 
        class="cart-item"
      >
        <div class="item-image">
          <img :src="item.image" :alt="item.name" />
        </div>
        <div class="item-details">
          <h3 class="item-name">{{ item.name }}</h3>
          <div class="item-price">
            {{ item.price.toLocaleString('ru-RU') }} ₽
          </div>
          <div class="quantity-control">
            <button 
              class="quantity-btn" 
              @click="updateQuantity(item.id, item.quantity - 1)"
              :disabled="item.quantity <= 1 || loading"
            >
              -
            </button>
            <input
              type="number"
              v-model.number="item.quantity"
              min="1"
              class="quantity-input"
              @change="updateQuantity(item.id, item.quantity)"
              :disabled="loading"
            />
            <button 
              class="quantity-btn" 
              @click="updateQuantity(item.id, item.quantity + 1)"
              :disabled="loading"
            >
              +
            </button>
          </div>
        </div>
        <div class="item-actions">
          <button 
            class="remove-btn" 
            @click="removeFromCart(item.id)"
            :disabled="loading"
          >
            ✕
          </button>
        </div>
      </div>
      
      <!-- Итоговая сумма -->
      <div class="cart-summary">
        <div class="summary-row">
          <span>Товаров:</span>
          <span>{{ cartItems.length }}</span>
        </div>
        <div class="summary-row total-row">
          <span>Итого:</span>
          <span class="total-amount">
            {{ totalAmount.toLocaleString('ru-RU') }} ₽
          </span>
        </div>
      </div>
      
      <!-- Кнопка оформления заказа -->
      <button 
        class="checkout-button tg-button"
        @click="checkout"
        :disabled="loading"
      >
        {{ loading ? 'Оформление...' : `Оформить заказ за ${totalAmount.toLocaleString('ru-RU')} ₽` }}
      </button>
      
      <!-- Информация о доставке -->
      <div class="delivery-info">
        <h4>🚚 Доставка</h4>
        <p>Бесплатная доставка при заказе от 5000 ₽</p>
        <p>Самовывоз из пунктов выдачи</p>
      </div>
    </div>
    
    <!-- Информация пользователя -->
    <div class="user-info" v-if="userId">
      <p>Пользователь ID: {{ userId }}</p>
      <p>Товаров в корзине: {{ cartItems.length }}</p>
    </div>
  </div>
</template>

