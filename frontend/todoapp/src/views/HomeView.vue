<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useRouter } from 'vue-router';

const cartItems = ref<any[]>([]);
const loading = ref(false);
const error = ref<string | null>(null);
const totalAmount = ref(0);
const tg = (window as any).Telegram?.WebApp;
const router = useRouter();

// Получение ID пользователя из Telegram
const userId = computed(() => {
  return tg?.initDataUnsafe?.user?.id;
});

const fetchCart = async () => {
  if (!userId.value) {
    error.value = 'Необходимо авторизоваться в Telegram';
    return;
  }

  loading.value = true;
  error.value = null;
  
  try {
    console.log('Запрашиваем корзину для пользователя:', userId.value);
    const response = await fetch(`http://localhost:8000/api/cart/${userId.value}/`);
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => null);
      throw new Error(errorData?.detail || `Ошибка сервера: ${response.status} ${response.statusText}`);
    }
    
    const data = await response.json();
    console.log('Данные корзины:', data);
    
    // Проверяем структуру ответа
    if (data.items && Array.isArray(data.items)) {
      cartItems.value = data.items.map((item: any) => ({
        id: item.id,
        product: item.product,
        quantity: item.quantity,
        price: item.product.price,
        name: item.product.name
      }));
    } else if (Array.isArray(data)) {
      // Альтернативный формат ответа
      cartItems.value = data.map((item: any) => ({
        id: item.id,
        product: item.product || { name: 'Товар без названия', price: 0 },
        quantity: item.quantity || 1,
        price: item.product?.price || item.price || 0,
        name: item.product?.name || item.name || 'Товар без названия'
      }));
    } else {
      cartItems.value = [];
    }
    
    calculateTotal();
  } catch (err) {
    const errorMessage = err instanceof Error ? err.message : 'Неизвестная ошибка при загрузке корзины';
    error.value = errorMessage;
    console.error('Ошибка загрузки корзины:', err);
    
    // Показываем тестовые данные только в режиме разработки
    if (import.meta.env.DEV) {
      cartItems.value = [
        {
          id: 1,
          name: 'Умные часы',
          price: 2990,
          quantity: 1
        },
        {
          id: 2,
          name: 'Беспроводные наушники',
          price: 4500,
          quantity: 2
        }
      ];
      calculateTotal();
    }
  } finally {
    loading.value = false;
  }
};

const calculateTotal = () => {
  totalAmount.value = cartItems.value.reduce((sum, item) => {
    return sum + (item.price * item.quantity);
  }, 0);
};

const updateQuantity = async (itemId: number, newQuantity: number) => {
  if (newQuantity < 1 || !userId.value) return;
  
  loading.value = true;
  error.value = null;
  
  try {
    const response = await fetch(`http://localhost:8000/api/cart/${userId.value}/${itemId}/`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ quantity: newQuantity }),
    });
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => null);
      throw new Error(errorData?.detail || `Ошибка обновления: ${response.status}`);
    }
    
    // Обновляем локальные данные
    const item = cartItems.value.find(i => i.id === itemId);
    if (item) {
      item.quantity = newQuantity;
      calculateTotal();
    }
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Ошибка при обновлении количества';
    console.error('Ошибка обновления количества:', err);
  } finally {
    loading.value = false;
  }
};

const removeFromCart = async (itemId: number) => {
  if (!userId.value) return;
  
  loading.value = true;
  error.value = null;
  
  try {
    const response = await fetch(`http://localhost:8000/api/cart/${userId.value}/${itemId}/`, {
      method: 'DELETE',
    });
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => null);
      throw new Error(errorData?.detail || `Ошибка удаления: ${response.status}`);
    }
    
    // Обновляем локальные данные
    cartItems.value = cartItems.value.filter(item => item.id !== itemId);
    calculateTotal();
    
    tg?.showAlert('Товар удален из корзины!');
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Ошибка при удалении товара';
    console.error('Ошибка удаления товара:', err);
  } finally {
    loading.value = false;
  }
};

const checkout = async () => {
  if (cartItems.value.length === 0) {
    tg?.showAlert('Ваша корзина пуста!');
    return;
  }
  
  if (!userId.value) {
    tg?.showAlert('Пожалуйста, авторизуйтесь в Telegram для оформления заказа!');
    return;
  }
  
  try {
    const confirm = await new Promise<boolean>((resolve) => {
      if (tg?.showConfirm) {
        tg.showConfirm(
          `Ваш заказ на сумму ${totalAmount.value.toLocaleString('ru-RU')} ₽`,
          (confirmed: boolean) => resolve(confirmed)
        );
      } else {
        resolve(confirm(`Ваш заказ на сумму ${totalAmount.value.toLocaleString('ru-RU')} ₽`));
      }
    });
    
    if (!confirm) {
      tg?.showAlert('Оформление заказа отменено');
      return;
    }
    
    loading.value = true;
    
    // Подготавливаем данные для заказа
    const orderData = {
      items: cartItems.value.map(item => ({
        id: item.product.id || item.id,
        quantity: item.quantity,
        price: item.price
      })),
      total: totalAmount.value
    };
    
    console.log('Данные заказа:', orderData);
    
    const response = await fetch(`http://localhost:8000/api/cart/${userId.value}/checkout/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(orderData),
    });
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => null);
      throw new Error(errorData?.detail || `Ошибка оформления заказа: ${response.status}`);
    }
    
    const result = await response.json();
    console.log('Результат заказа:', result);
    
    tg?.showAlert(`Заказ успешно оформлен! Номер: ${result.id || 'без номера'}`);
    
    // Очищаем корзину
    cartItems.value = [];
    calculateTotal();
    
    // Возвращаемся в каталог
    setTimeout(() => {
      router.push('/');
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
  tg.MainButton.textColor = '#FFFFFF';
  
  tg.MainButton.onClick(checkout);
  
  // Обновляем состояние кнопки при загрузке данных
  const updateMainButton = () => {
    if (cartItems.value.length > 0) {
      tg.MainButton.show();
      tg.MainButton.enable();
    } else {
      tg.MainButton.hide();
    }
  };
  
  updateMainButton();
}

onMounted(fetchCart);
</script>

<template>
  <div class="cart-container">
    <h2 class="page-title">🛒 Ваша корзина</h2>
    
    <div v-if="error" class="error-message">
      {{ error }}
    </div>
    
    <div v-if="loading" class="loading">
      <div class="loading-spinner"></div>
      <p>Загрузка корзины...</p>
    </div>
    
    <div v-else-if="cartItems.length === 0" class="empty-cart">
      <div class="empty-icon">🛒</div>
      <h3>Ваша корзина пуста</h3>
      <p>Добавьте товары для оформления заказа</p>
      <RouterLink to="/" class="browse-button tg-button">
        К каталогу товаров
      </RouterLink>
    </div>
    
    <div v-else class="cart-items">
      <div 
        v-for="item in cartItems" 
        :key="item.id" 
        class="cart-item"
      >
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
        :disabled="loading || cartItems.length === 0"
      >
        {{ loading ? 'Оформление...' : `Оформить заказ за ${totalAmount.toLocaleString('ru-RU')} ₽` }}
      </button>
    </div>
    
    <div v-if="userId" class="user-info">
      <p>Пользователь ID: {{ userId }}</p>
      <p>Товаров в корзине: {{ cartItems.length }}</p>
    </div>
  </div>
</template>

<style scoped>
.cart-container {
  padding: 16px 0;
}

.page-title {
  font-size: 1.8rem;
  font-weight: 700;
  margin-bottom: 24px;
  text-align: center;
  color: var(--tg-theme-text-color);
}

.empty-cart {
  text-align: center;
  padding: 40px 20px;
  color: var(--tg-theme-hint-color);
}

.empty-icon {
  font-size: 4rem;
  margin-bottom: 16px;
  color: var(--tg-theme-button-color);
}

.empty-cart h3 {
  font-size: 1.5rem;
  margin-bottom: 8px;
  color: var(--tg-theme-text-color);
}

.empty-cart p {
  margin-bottom: 24px;
  font-size: 1.1rem;
}

.browse-button {
  margin-top: 16px;
  width: auto;
  padding: 12px 32px;
}

.cart-items {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.cart-item {
  display: flex;
  background-color: var(--tg-section-bg-color);
  border-radius: var(--border-radius);
  padding: 16px;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.05);
  transition: var(--transition);
}

.cart-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.item-details {
  flex: 1;
}

.item-name {
  font-size: 1.1rem;
  font-weight: 600;
  color: var(--tg-theme-text-color);
  margin-bottom: 4px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.item-price {
  font-size: 1.2rem;
  font-weight: 700;
  color: var(--tg-theme-button-color);
  margin-bottom: 8px;
}

.quantity-control {
  display: flex;
  align-items: center;
  gap: 8px;
}

.quantity-btn {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background-color: var(--tg-theme-button-color);
  color: white;
  border: none;
  font-weight: bold;
  cursor: pointer;
  transition: var(--transition);
}

.quantity-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.quantity-btn:hover:not(:disabled) {
  transform: scale(1.1);
}

.quantity-input {
  width: 48px;
  padding: 8px;
  text-align: center;
  border: 1px solid rgba(0, 0, 0, 0.1);
  border-radius: 8px;
  color: var(--tg-theme-text-color);
  background-color: var(--tg-theme-bg-color);
}

.item-actions {
  display: flex;
  align-items: flex-start;
  margin-left: 16px;
}

.remove-btn {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background-color: #ff4444;
  color: white;
  border: none;
  font-weight: bold;
  cursor: pointer;
  transition: var(--transition);
}

.remove-btn:hover {
  transform: scale(1.1);
}

.remove-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.cart-summary {
  background-color: var(--tg-section-bg-color);
  border-radius: var(--border-radius);
  padding: 16px;
  margin: 24px 0;
  border: 1px solid rgba(0, 0, 0, 0.05);
}

.summary-row {
  display: flex;
  justify-content: space-between;
  padding: 8px 0;
  border-bottom: 1px solid rgba(0, 0, 0, 0.05);
}

.summary-row:last-child {
  border-bottom: none;
}

.total-row {
  font-weight: 700;
  font-size: 1.2rem;
  border-bottom: none;
  padding-top: 12px;
}

.total-amount {
  color: #4CAF50;
}

.checkout-button {
  width: 100%;
  padding: 16px;
  font-size: 1.1rem;
  margin-bottom: 24px;
  background-color: #4CAF50;
}

.user-info {
  margin-top: 30px;
  padding: 12px 16px;
  background-color: rgba(0, 0, 0, 0.03);
  border-radius: var(--border-radius);
  font-size: 0.9rem;
  color: var(--tg-theme-hint-color);
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
  border: 3px solid rgba(76, 175, 80, 0.3);
  border-radius: 50%;
  border-top-color: #4CAF50;
  animation: spin 1s linear infinite;
  margin-bottom: 8px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Адаптивность для мобильных устройств */
@media (max-width: 768px) {
  .cart-item {
    flex-direction: column;
  }
  
  .item-actions {
    margin-left: 0;
    margin-top: 16px;
  }
}
</style>