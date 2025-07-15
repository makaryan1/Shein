$(document).ready(function() {
    // Добавление в корзину
    $('.add-to-cart').click(function() {
        const productId = $(this).data('product-id');

        $.ajax({
            url: '/api/add_to_cart',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({ product_id: productId }),
            success: function(response) {
                $('.cart-count').text(response.cart_count);
                showToast('Товар добавлен в корзину!');
            }
        });
    });

    // Показать уведомление
    function showToast(message) {
        const toast = $(`
            <div class="position-fixed bottom-0 end-0 p-3" style="z-index: 11">
                <div class="toast show align-items-center text-white bg-success" role="alert">
                    <div class="d-flex">
                        <div class="toast-body">
                            ${message}
                        </div>
                        <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
                    </div>
                </div>
            </div>
        `);

        $('body').append(toast);
        setTimeout(() => toast.remove(), 3000);
    }
});