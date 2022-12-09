from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("search", views.search, name="search"),
    path("categories", views.categories, name="categories"),
    path("categories/<int:category_pk>", views.goto_category, name="goto_category"),
    path("add_listing", views.add_listing, name="add_listing"),
    path("listing/<int:listing_pk>", views.goto_listing, name="goto_listing"),
    path("comment/<int:listing_pk>", views.comment, name="comment"),
    path("bid/<int:listing_pk>", views.bid, name="bid"),
    path("mylistings", views.my_listings, name="my_listings"),
    path("mylistingsclose/<int:listing_pk>", views.close_listing, name="close_listing"),
    path("watchlist", views.goto_watchlist, name="goto_watchlist"),
    path("watchlistadd/<int:listing_pk>", views.addto_watchlist, name="addto_watchlist"), 
    path("watchlistremove/<int:listing_pk>", views.removefrom_watchlist, name="removefrom_watchlist"),
    path("closedlistings", views.inactive_listings, name="inactive_listings"),
    path("winner/<int:listing_pk>", views.winner, name="winner"),
]
