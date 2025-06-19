document.addEventListener('DOMContentLoaded', function() {
    // Обновление счетчика корзины
    function updateCartCount() {
        // В реальном приложении здесь был бы запрос к API
        const count = localStorage.getItem('cartCount') || 0;
        document.querySelectorAll('.cart-count').forEach(el => {
            el.textContent = count;
        });
    }
    
    // Инициализация
    updateCartCount();
    
    // Обработчики для кнопок "Купить" в каталоге
    document.querySelectorAll('.btn-outline-primary').forEach(button => {
        button.addEventListener('click', function() {
            const currentCount = parseInt(localStorage.getItem('cartCount') || 0);
            localStorage.setItem('cartCount', currentCount + 1);
            updateCartCount();
            
            // Показываем уведомление
            const toast = document.createElement('div');
            toast.className = 'position-fixed bottom-0 end-0 p-3';
            toast.style.zIndex = '11';
            toast.innerHTML = `
                <div class="toast show" role="alert" aria-live="assertive" aria-atomic="true">
                    <div class="toast-header bg-primary text-white">
                        <strong class="me-auto">CurrencyExchange</strong>
                        <button type="button" class="btn-close btn-close-white" data-bs-dismiss="toast" aria-label="Close"></button>
                    </div>
                    <div class="toast-body">
                        Товар добавлен в корзину!
                    </div>
                </div>
            `;
            document.body.appendChild(toast);
            
            // Удаляем уведомление через 3 секунды
            setTimeout(() => {
                toast.remove();
            }, 3000);
        });
    });
    
    // Обработчики для удаления из корзины
    document.querySelectorAll('.btn-outline-danger').forEach(button => {
        button.addEventListener('click', function() {
            const row = this.closest('tr');
            row.style.opacity = '0';
            setTimeout(() => {
                row.remove();
                const currentCount = parseInt(localStorage.getItem('cartCount') || 0);
                localStorage.setItem('cartCount', Math.max(0, currentCount - 1));
                updateCartCount();
                
                // Если корзина пуста, показываем сообщение
                if (document.querySelectorAll('tbody tr').length === 0) {
                    location.reload(); // Перезагружаем страницу для показа сообщения о пустой корзине
                }
            }, 300);
        });
    });
    
    // Валидация только для форм с классом .js-validate (например, для корзины)
    document.querySelectorAll('form.js-validate').forEach(form => {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            // Простая валидация
            let isValid = true;
            this.querySelectorAll('[required]').forEach(input => {
                if (!input.value.trim()) {
                    input.classList.add('is-invalid');
                    isValid = false;
                } else {
                    input.classList.remove('is-invalid');
                }
            });
            if (isValid) {
                alert('Форма успешно отправлена!');
                this.reset();
            }
        });
    });
});