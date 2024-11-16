from django.db import models
from django.contrib.auth.models import User
from decimal import Decimal
from django import forms

class Product(models.Model):
    COLOR_CHOICES = [
        ('black', 'Black'),
        ('blue', 'Blue'),
        ('red', 'Red'),
    ]

    SIZE_CHOICES = [
        ('S', 'Small'),
        ('L', 'Large'),
        ('XL', 'Extra Large'),
    ]

    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    old_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    image1 = models.ImageField(upload_to='products/')
    image2 = models.ImageField(upload_to='products/', blank=True, null=True)
    category = models.CharField(max_length=100)
    is_hot = models.BooleanField(default=False)
    discount_percentage = models.IntegerField(default=0)
    
    # New fields
    color = models.CharField(max_length=5, choices=COLOR_CHOICES, null=True, blank=True)
    size = models.CharField(max_length=2, choices=SIZE_CHOICES, null=True, blank=True)

    def __str__(self):
        return self.name
    # Add a method to get price options based on quantity
    def get_price_options(self):
       return {
            1: self.price,
            2: self.price * Decimal(2) * Decimal(0.9),  # 10% discount for 2
            3: self.price * Decimal(3) * Decimal(0.8)   # 20% discount for 3
        }

    
class Bundle(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='bundles')
    name = models.CharField(max_length=255, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    
    def __str__(self):
        return self.name

class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="cart")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Cart for {self.user.username}"

    def total_price(self):
        return sum(item.total_price for item in self.cart_items.all())

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name="cart_items", on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    bundle = models.ForeignKey(Bundle, null=True, blank=True, on_delete=models.SET_NULL)
    quantity = models.PositiveIntegerField(default=1)
    color = models.CharField(max_length=5, null=True, blank=True)
    size = models.CharField(max_length=2, null=True, blank=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, editable=False)

    def save(self, *args, **kwargs):
        if self.bundle:
            self.total_price = self.bundle.price * self.quantity
        else:
            discounted_price = self.product.price * (1 - self.product.discount_percentage / 100)
            self.total_price = discounted_price * self.quantity
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.product.name} ({self.quantity})"




class ProductOption(models.Model):
    product = models.ForeignKey(Product, related_name="options", on_delete=models.CASCADE)
    option_name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.option_name} - Rs:{self.price}"
    
class Category(models.Model):
    name = models.CharField(max_length=200)
    image = models.ImageField(upload_to='category_images/', blank=True, null=True)  # Image for category

 

    def __str__(self):
        return self.name
    


class Customer(models.Model):
	user = models.OneToOneField(User, null=True, blank=True, on_delete=models.CASCADE)
	name = models.CharField(max_length=200, null=True)
	email = models.CharField(max_length=200)

	def __str__(self):
		return self.name

class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True)
    date_ordered = models.DateTimeField(auto_now_add=True)
    complete = models.BooleanField(default=False)
    transaction_id = models.CharField(max_length=100, null=True)

    def __str__(self):
        return str(self.id)

    @property
    def get_cart_items(self):
        # This calculates the total quantity of all items in the cart
        order_items = self.orderitem_set.all()
        total = sum([item.quantity for item in order_items])
        return total

    @property
    def get_cart_total(self):
        # This calculates the total price of all items in the cart
        order_items = self.orderitem_set.all()
        total = sum([item.get_total for item in order_items])
        print("total price: ",total)
        return total

	
class OrderItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True)
    quantity = models.IntegerField(default=0, null=True, blank=True)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.product)

    @property
    def get_total(self):
        total = self.product.price * self.quantity
        print(self.product.price)
        print("total price: ",total)
        return total

class OrderForm(forms.Form):
    name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Name'}))
    phone = forms.CharField(max_length=15, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone'}))
    address = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Address'}))
    city = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'City'}))


class ShippingAddress(models.Model):
	customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True)
	order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True)
	address = models.CharField(max_length=200, null=False)
	city = models.CharField(max_length=200, null=False)
	state = models.CharField(max_length=200, null=False)
	zipcode = models.CharField(max_length=200, null=False)
	date_added = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return self.address
@property
def shipping(self):
	shipping = False
	orderitems = self.orderitem_set.all()
	for i in orderitems:
		if i.product.digital == False:
			shipping = True
	return shipping
