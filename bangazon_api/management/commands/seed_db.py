import random
import faker_commerce
from faker import Faker
from datetime import datetime
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from rest_framework.authtoken.models import Token
from bangazon_api.models import (
    Store, Product, Category, PaymentType, Order, Favorite, Rating)
from bangazon_api.helpers import STATE_NAMES


class Command(BaseCommand):
    faker = Faker()
    faker.add_provider(faker_commerce.Provider)

    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument(
            '--user_count',
            help='Count of users to seed',
        )

    def handle(self, *args, **options):
        if options['user_count']:
            self.create_users(int(options['user_count']))
        else:
            self.create_users()

    def create_users(self, user_count=8):
        """Create random users"""
        for _ in range(user_count):
            first_name = self.faker.first_name()
            last_name = self.faker.last_name()
            username = f'{first_name}_{last_name}@example.com'
            user = User.objects.create_user(
                first_name=first_name,
                last_name=last_name,
                password="PassWord1",
                username=username,
            )

            PaymentType.objects.create(
                customer=user,
                merchant_name=self.faker.credit_card_provider(),
                acct_number=self.faker.credit_card_number()
            )

            Token.objects.create(
                user=user
            )

            if user.id % 2 == 0:
                store = self.create_store(user)
                self.create_products(store, user_count)
        users = User.objects.all()

        for user in users:
            self.create_closed_orders(user)
            self.create_open_orders(user)
            self.create_favorite(user)
            if user.id % 2 != 0:
                self.create_ratings(user)

    def create_store(self, user):
        """Create random stores in the database"""
        return Store.objects.create(
            seller=user,
            name=self.faker.company(),
            description="Lorem ipsum dolor sit amet, consectetur adipiscing elit. Maecenas pellentesque.",
            is_active=True
        )

    def create_products(self, store, count):
        """Create Random Products in the database"""
        for _ in range(count):
            Product.objects.create(
                name=self.faker.ecommerce_name(),
                store=store,
                price=random.randint(50, 1000),
                description="Lorem ipsum dolor sit amet, consectetur adipiscing elit. Etiam elit.",
                quantity=random.randint(2, 20),
                location=random.choice(STATE_NAMES),
                image_path="",
                category=Category.objects.get_or_create(
                    name=self.faker.ecommerce_category())[0]
            )

    def create_closed_orders(self, user):
        order = Order.objects.create(
            user=user,
            payment_type=user.payment_types.first(),
            completed_on=datetime.now()
        )
        category = random.randint(1, Category.objects.count())
        products = [product.id for product in Product.objects.filter(
            category_id=category)]
        order.products.set(products)

    def create_open_orders(self, user):
        order = Order.objects.create(
            user=user
        )
        category = random.randint(1, Category.objects.count())
        products = [product.id for product in Product.objects.filter(
            category_id=category)]
        order.products.set(products)

    def create_favorite(self, user):
        store = Store.objects.get(pk=random.randint(1, Store.objects.count()))

        Favorite.objects.create(
            customer=user,
            store=store
        )

    def create_ratings(self, user):
        for product in Product.objects.all():
            Rating.objects.create(
                customer=user,
                product=product,
                score=random.randint(1, 5),
                review=self.faker.paragraph()
            )
