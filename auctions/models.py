from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator 
from django.db import models


class User(AbstractUser):
    pass
    

class Category(models.Model):
    name = models.CharField(unique=True, max_length=100)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ["name"]

    def __str__(self):
        return self.name

    
class Listing(models.Model):
    active = models.BooleanField(default=True)
    title = models.CharField(max_length=50)
    description = models.TextField(max_length=500)
    start_price = models.DecimalField(max_digits=10, decimal_places=2, 
        validators=[MinValueValidator(0.05, message="Invalid starting price")])
    current_price = models.DecimalField(max_digits=10, decimal_places=2)
    datetime_listed = models.DateTimeField(auto_now_add=True)
    image_link = models.URLField(null=True, blank=True)
    image_file = models.ImageField(null=True, blank=True, upload_to="", default="default_listing_image.png")
    category = models.ForeignKey(Category, null=True, blank=True, on_delete=models.SET_NULL)
    seller = models.ForeignKey(User, on_delete=models.CASCADE)
    highest_bidder = models.ForeignKey(User, related_name="highest_bidder", null=True, blank=True, on_delete=models.CASCADE)
    watchlist = models.ManyToManyField(User, related_name="user_watching", null=True, blank=True)

    class Meta:
        ordering = ["-datetime_listed"]

    def __str__(self):
        return f"{self.id}: {self.title}"

    
class Bid(models.Model):
    bid_price = models.DecimalField(max_digits=10, decimal_places=2)
    bidder = models.ForeignKey(User, on_delete=models.CASCADE)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)

    class Meta:
        ordering = ["listing", "-bid_price"]
        unique_together = ["bid_price", "listing"]

    def __str__(self):
        return f"{self.bid_price} on {self.listing}"
    

class Comment(models.Model):
    message = models.TextField(max_length=500)
    timestamp = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)

    class Meta:
        ordering = ["-timestamp"]

    def __str__(self):
        return self.message
