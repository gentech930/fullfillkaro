var updateBtns = document.getElementsByClassName('update-cart');

for (let i = 0; i < updateBtns.length; i++) {
    updateBtns[i].addEventListener('click', function() {
        var productId = this.dataset.product;
        var action = this.dataset.action;
        console.log('productId:', productId, 'Action:', action);
        console.log('USER:', user);

        if (user == 'AnonymousUser') {
            console.log('User is not authenticated');
            // Optionally redirect to login page
        } else {
            updateUserOrder(productId, action);
        }
    });
}

function updateUserOrder(productId, action) {
    console.log('User is authenticated, sending data...');
    
    var url = '/update_item/'; // Update this URL if needed

    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken,
        }, 
        body: JSON.stringify({'productId': productId, 'action': action})
    })
    .then((response) => response.json())
    .then((data) => {
        // Redirect to cart page after adding the item
        window.location.href = '/cart/'; // Ensure this matches your URL configuration
    });
}
