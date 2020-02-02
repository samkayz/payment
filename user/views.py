from django.shortcuts import render, redirect
from django.contrib.auth.models import auth, User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from . models import Country, Profile, Balance, Transactions, RequestMoney, Card
from django.db.models import Q
from django.core.paginator import Paginator
import random
import string
import uuid
import datetime
from datetime import datetime


def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = auth.authenticate(username=username, password=password)
        if user is not None:
            auth.login(request, user)
            return redirect('home')
        else:
            messages.error(request, "Invalid Credentials")
            return redirect('login')
    else:
        return render(request, 'user/login.html')


def signup(request):
    if request.method == 'POST':
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        username = request.POST['username']
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']

        if password1 == password2:
            if User.objects.filter(username=username).exists():
                messages.error(request, "Username Taken")
                return redirect('signup')
            elif User.objects.filter(email=email).exists():
                messages.error(request, "Email Taken")
                return redirect('signup')
            else:
                user = User.objects.create_user(first_name=first_name,
                                                last_name=last_name,
                                                username=username,
                                                email=email,
                                                password=password1)
                user.save()
                messages.success(request, "SignUp Successful!!")
                return redirect('signup')
        else:
            messages.error(request, "Password not Match")
            return redirect('signup')
    else:
        return render(request, 'user/signup.html')


def logout(request):
    auth.logout(request)
    return redirect('/')


@login_required(login_url='login')
def home(request):
    c_user = request.user.id
    users = Balance.objects.filter(user_id=c_user).exists()
    if Balance.objects.filter(user_id=c_user).exists():
        bal = Balance.objects.all().get(user_id=c_user)
        show = Transactions.objects.filter(Q(r_id=c_user) | Q(s_id=c_user)).order_by('-id')[:6]
        return render(request, 'user/home.html', {'users': users, 'bal': bal, 'show': show})
    else:
        return render(request, 'user/home.html')


@login_required(login_url='login')
def profile(request):
    c_user = request.user.id
    if request.method == 'POST':
        dob = request.POST['dob']
        mobile_no = request.POST['mobile_no']
        address = request.POST['address']
        city = request.POST['city']
        state = request.POST['state']
        zip_code = request.POST['zip_code']
        country = request.POST['country']

        if Profile.objects.filter(user_id=c_user).exists():
            Profile.objects.filter(user_id=c_user).update(user_id=c_user,
                                                          dob=dob,
                                                          mobile_no=mobile_no,
                                                          address=address,
                                                          city=city,
                                                          state=state,
                                                          zip_code=zip_code,
                                                          country=country)
            messages.success(request, "Profile Updated Successful")
            return redirect('profile')
        else:
            data = Profile(user_id=c_user,
                           dob=dob,
                           mobile_no=mobile_no,
                           address=address,
                           city=city,
                           state=state,
                           zip_code=zip_code,
                           country=country)

            Balance.objects.update_or_create(user_id=c_user,
                                             bal='0',
                                             status='inactive')
            data.save()
            messages.success(request, 'Profile Created')
            return redirect('profile')
    else:
        if Profile.objects.filter(user_id=c_user).exists():
            country = Country.objects.filter()
            all_profile = Profile.objects.all().get(user_id=c_user)
            user = Balance.objects.filter(user_id=c_user).exists()
            bal = Balance.objects.values('bal').get(user_id=c_user)['bal']
            status = Balance.objects.values('status').get(user_id=c_user)['status']
            return render(request, 'user/profile.html', {'all_profile': all_profile,
                                                         'users': user, 'bal': bal,
                                                         'country': country,
                                                         'status': status})
        else:
            country = Country.objects.filter()
            return render(request, 'user/profile.html', {'country': country})


@login_required(login_url='login')
def send_money(request):
    ref_no = uuid.uuid4().hex[:10].lower()
    base_date_time = datetime.now()
    now = (datetime.strftime(base_date_time, "%Y-%m-%d %H:%M %p"))
    c_user_email = request.user.email
    if request.method == 'POST':
        email = request.POST['email']
        amount = request.POST['amount']
        currency = request.POST['currency']
        if c_user_email == email:
            messages.error(request, "Sorry you can't Send Money to Yourself")
            return redirect('send-money')
        elif amount == '':
            messages.error(request, "Invalid Amount")
            return redirect('send-money')
        elif float(amount) < 100.0:
            messages.error(request, 'You can only send money from $100 and Above')
            return redirect('send-money')
        else:
            if User.objects.filter(email=email).exists():
                name = User.objects.all().get(email=email)
                return render(request, 'user/send-money-confirm.html', {'email': email,
                                                                        'amount': amount,
                                                                        'currency': currency,
                                                                        'name': name})
            else:
                messages.error(request, "User not Found in the System")
                return redirect('send-money')
    else:
        return render(request, 'user/send-money.html')


@login_required(login_url='login')
def send_money_confirm(request):
    ref_no = uuid.uuid4().hex[:10].lower()
    base_date_time = datetime.now()
    now = (datetime.strftime(base_date_time, "%Y-%m-%d %H:%M %p"))
    c_user_id = request.user.id
    if request.method == "POST":
        r_email = request.POST['email']
        amount = request.POST['amount']
        currency = request.POST['currency']
        desc = request.POST['desc']

        am = float(amount)
        # Sender balance
        sender = User.objects.all().get(id=c_user_id)
        rec_name = User.objects.all().get(email=r_email)
        s_bal = Balance.objects.values('bal').get(user_id=c_user_id)['bal']

        # Receiver's Balance
        r_bal_id = User.objects.all().get(email=r_email)
        r_bal = Balance.objects.values('bal').get(user_id=r_bal_id.id)['bal']

        # Check if Sender have low Acct Balance
        if s_bal < am:
            messages.error(request, "Insufficient Balance")
            return redirect('send-money')
        else:
            # Add Money to receiver's Account
            new = am + r_bal
            Balance.objects.filter(user_id=r_bal_id.id).update(bal=new)

            # Minus Money from the Sender
            s_new = s_bal - am
            Balance.objects.filter(user_id=c_user_id).update(bal=s_new)

            # Updating Transactions Table
            txn = Transactions(s_id=c_user_id, r_id=r_bal_id.id, sender_name=sender.first_name,
                               desc=desc, txn_amt=am, txn_id="tx"+ref_no, txn_date=now, currency=currency,
                               receiver_name=rec_name.first_name)
            txn.save()
            return render(request, 'user/send-money-success.html', {'email': r_email, 'amount': am})
    return render(request, 'user/send-money-confirm.html')


@login_required(login_url='login')
def send_money_success(request):
    return render(request, 'user/send-money-success.html')


@login_required(login_url='login')
def transactions(request):
    c_user = request.user.id
    users = Balance.objects.filter(user_id=c_user).exists()
    if Balance.objects.filter(user_id=c_user).exists():
        bal = Balance.objects.all().get(user_id=c_user)
        show = Transactions.objects.filter(Q(r_id=c_user) | Q(s_id=c_user)).order_by('-id')
        paginator = Paginator(show, 8)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        return render(request, 'user/transactions.html', {'users': users, 'bal': bal, 'show': page_obj})
    else:
        return render(request, 'user/transactions.html')


@login_required(login_url='login')
def request_money(request):
    c_user_email = request.user.email
    if request.method == "POST":
        name = request.POST['name']
        email = request.POST['email']
        count = request.POST['country']
        amount = request.POST['amount']
        currency = request.POST['currency']
        due = request.POST['due']
        desc = request.POST['desc']
        if c_user_email == email:
            messages.error(request, "Sorry You can't request money from Yourself")
            return redirect('request-money')
        else:
            return render(request, 'user/request-money-confirm.html', {'name': name, 'email': email,
                                                                       'count': count, 'amount': amount,
                                                                       'due': due, 'desc': desc, 'currency': currency})
    country = Country.objects.filter()
    return render(request, 'user/request-money.html', {'country': country})


def request_money_confirm(request):
    c_user = request.user.id
    sender = request.user.first_name + ' ' + request.user.last_name
    base_date_time = datetime.now()
    now = (datetime.strftime(base_date_time, "%Y-%m-%d %H:%M %p"))
    if request.method == "POST":
        name = request.POST['name']
        email = request.POST['email']
        country = request.POST['country']
        due_date = request.POST['due']
        desc = request.POST['desc']
        currency = request.POST['currency']
        amount = request.POST['amount']
        if User.objects.filter(email=email).exists():
            r_id = User.objects.all().get(email=email)

            req = RequestMoney(s_id=c_user, r_id=r_id.id, r_name=name, r_email=email,
                               r_amount=amount, currency=currency, country=country,
                               desc=desc, due_date=due_date, status='pending',
                               r_date=now, sender=sender)
            req.save()
            return render(request, 'user/request-money-success.html', {'currency': currency, 'amount': amount,
                                                                       'email': email})
        else:
            req = RequestMoney(s_id=c_user, r_id='0', r_name=name, r_email=email,
                               r_amount=amount, currency=currency, country=country,
                               desc=desc, due_date=due_date, status='pending',
                               r_date=now, sender=sender)
            req.save()
            return render(request, 'user/request-money-success.html', {'currency': currency, 'amount': amount,
                                                                       'email': email})
    return render(request, 'user/request-money-confirm.html')


def request_detail(request):
    c_user = request.user.id
    users = Balance.objects.filter(user_id=c_user).exists()
    if Balance.objects.filter(user_id=c_user).exists():
        bal = Balance.objects.all().get(user_id=c_user)
        show = RequestMoney.objects.filter(Q(r_id=c_user) | Q(s_id=c_user)).order_by('-id')
        paginator = Paginator(show, 8)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        return render(request, 'user/request.html', {'users': users, 'bal': bal, 'show': page_obj})
    else:
        return render(request, 'user/request.html')


def card_and_account(request):
    c_user = request.user.id
    if request.method == 'POST':
        options = request.POST['options']
        card_type = request.POST['card_type']
        card_no = request.POST['card_no']
        exp_date = request.POST['exp_date']
        cvv_no = request.POST['cvv_no']
        card_owner = request.POST['card_owner']
        if Card.objects.count() == 2:
            messages.error(request, 'You can only have 2 Card link to your Account')
            return redirect('cards-and-accounts')
        else:
            card = Card(owner_id=c_user, card_type=card_type, card_issuer=options,
                        card_num=card_no, exp_date=exp_date, cvv_no=cvv_no, card_name=card_owner)
            card.save()
            messages.success(request, "Card Added Successfully")
            return redirect('cards-and-accounts')

    show = Card.objects.filter(owner_id=c_user)
    bal = Balance.objects.values('bal').get(user_id=c_user)['bal']
    user = Balance.objects.filter(user_id=c_user).exists()
    return render(request, 'user/cards-and-accounts.html', {'show': show, 'bal': bal, 'users': user})
