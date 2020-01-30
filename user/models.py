from django.db import models


class Country(models.Model):
    country_code = models.CharField(max_length=100)
    country_name = models.CharField(max_length=100)

    class Meta:
        db_table = "country"


class Profile(models.Model):
    user_id = models.IntegerField()
    dob = models.CharField(max_length=100)
    mobile_no = models.CharField(max_length=20)
    address = models.CharField(max_length=1000)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=100)
    country = models.CharField(max_length=100)

    class Meta:
        db_table = "profile"


class Balance(models.Model):
    user_id = models.IntegerField()
    bal = models.FloatField()
    status = models.CharField(max_length=100)

    class Meta:
        db_table = "balance"


class Transactions(models.Model):
    s_id = models.IntegerField()
    r_id = models.IntegerField()
    sender_name = models.CharField(max_length=1000)
    receiver_name = models.CharField(max_length=1000)
    desc = models.CharField(max_length=1000)
    txn_amt = models.CharField(max_length=100)
    txn_id = models.CharField(max_length=50)
    txn_date = models.CharField(max_length=100)
    currency = models.CharField(max_length=100)

    class Meta:
        db_table = "transactions"


class RequestMoney(models.Model):
    s_id = models.IntegerField()
    r_id = models.IntegerField()
    r_name = models.CharField(max_length=1000)
    sender = models.CharField(max_length=1000)
    r_email = models.EmailField()
    r_amount = models.FloatField()
    currency = models.CharField(max_length=10)
    country = models.CharField(max_length=100)
    desc = models.CharField(max_length=1000)
    due_date = models.CharField(max_length=1000)
    status = models.CharField(max_length=100)
    r_date = models.CharField(max_length=100)

    class Meta:
        db_table = "request_money"


class Card(models.Model):
    owner_id = models.IntegerField()
    card_type = models.CharField(max_length=100)
    card_issuer = models.CharField(max_length=100)
    card_num = models.CharField(max_length=100)
    exp_date = models.CharField(max_length=10)
    cvv_no = models.CharField(max_length=10)
    card_name = models.CharField(max_length=1000)

    class Meta:
        db_table = 'card'


