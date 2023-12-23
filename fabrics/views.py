from django.http import HttpResponse, JsonResponse, FileResponse
from django.contrib.auth import authenticate, login, logout
from django.core.serializers import serialize
# from django.contrib.auth.decorators import login_required
from django.template.loader import get_template
from django.contrib.auth.models import User
from fabrics.models import CustomUser, Services, Orders, Feedback
from django.shortcuts import redirect, render, get_object_or_404, reverse
from django.views import View
from fabrics.forms import InvoiceForm
from django.contrib import messages
import io
# from reportlab.lib.pagesizes import letter, A4
from reportlab.pdfgen import canvas
from datetime import date
import razorpay

# Create your views here.

def index(request):
    if request.user.is_anonymous:
        return redirect('/login')

    logged_in_user = request.user.username
    if logged_in_user == 'admin':
        users = CustomUser.objects.all()
        return render(request,'adm/index.html', {'users': users})
    else:
        # services = Services.objects.all()
        messages.success(request, "Login Successful")
        return render(request,'index.html')
        # return render(request,'user/services.html', {'services': services})

    return render(request,'fabrics/index.html')

def login_user(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request,user)
            return redirect('/')
        else:
            messages.error(request, "Incorrect username or password!")
            # return render(request, 'login.html')

    return render(request,'login.html')


def logout_user(request):
    logout(request)
    return redirect('/login')

def sign_up(request):
    super_user = 0
    staff = 0
    if request.method == 'POST':
        email = request.POST.get('email')
        name = request.POST.get('name')
        address = request.POST.get('address')
        phone = request.POST.get('phone')
        password = request.POST.get('password')
        username = request.POST.get('username')

        user = CustomUser.objects.create_user(
            email=email,
            password=password,
            name=name,
            phone=int(phone),
            address=address,
            username=username
        )

        messages.success(request, 'Registration Successful. You can now log in.')
        return redirect('login')

    return render(request, 'registration.html')


def show_users(request):
    users = CustomUser.objects.all()
    users_json = serialize('json', users)
    user_list = list(users.values())
    return JsonResponse({'users': user_list})

def delete_user(request, id):
    user = get_object_or_404(CustomUser, id=id)
    user.delete()
    return redirect('/')

def edit_user(request, id):
    user = get_object_or_404(CustomUser, id=id)
    user_info = {
        'id': user.id,
        'name': user.name,
        'email': user.email,
        'address': user.address,
    }
    return JsonResponse(user_info)

def update_user(request):
    if request.method == 'POST':
        id = request.POST.get('id')
        user = get_object_or_404(CustomUser, id=id)
        user.name = request.POST.get('name')
        user.email = request.POST.get('email')
        user.address = request.POST.get('address')
        # user.password = request.POST.get('password')
        
        user.save()
        return redirect('/')

    return redirect('/')

def about(request):
    return render(request, 'about.html')

def services(request):
    services = Services.objects.all()
    if request.user.username == 'admin':
        return render(request, 'adm/services.html', {'services': services})
    
    return render(request, 'services.html', {'services': services})

def add_service(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        image = request.FILES.get('image')
        rate = request.POST.get('rate')

        service = Services.objects.create(
            name=name,
            description=description,
            rate=rate,
            image=image
        )

        # service.save()

        return redirect('services')

def edit_service(request, id):
    service = get_object_or_404(Services, id=id)
    service_info = {
        'id': service.id,
        'name': service.name,
        'description': service.description,
        'rate': service.rate
    }
    return JsonResponse(service_info)

def update_service(request):
    if request.method == 'POST':
        id = request.POST.get('id')
        service = get_object_or_404(Services, id=id)
        service.name = request.POST.get('serviceName')
        service.description = request.POST.get('serviceDescription')
        service.image = request.FILES.get('image')
        service.rate = request.POST.get('serviceRate')
        
        service.save()
        return redirect('/services')

    return redirect('/services')

def delete_service(request, id):
    service = get_object_or_404(Services,id=id)
    service.delete()
    return redirect('/services')

def service(request,id):
    service = get_object_or_404(Services, id=id)
    form = InvoiceForm
    
    return render(request, 'user/service.html', {'service': service, 'form': form})

def order(request):
    if request.method == "POST":
        user = get_object_or_404(CustomUser, id=request.user.id)
        sid = request.POST.get('sid')
        height = request.POST.get('height')
        width = request.POST.get('width')
        area = int(height) * int(width)
        service = get_object_or_404(Services, id=sid)

        order = Orders.objects.create(
            service = service,
            user = user,
            area = area,
            total = service.rate * area,
            date = date.today()
        )

        return redirect('/orders')

def quotation(request,id):
    order = get_object_or_404(Orders,id=id)

    response = HttpResponse(content_type='application/pdf')

    # Set the Content-Disposition header for the response
    response['Content-Disposition'] = 'attachment; filename="invoice.pdf"'

    # Create a canvas for the PDF
    p = canvas.Canvas(response)

    # Set font properties
    p.setFont("Helvetica", 16)

    # Company name in center top
    p.drawCentredString(300, 800, 'Unique Fabrications')

    # Invoice Heading in Bold font
    p.setFont("Helvetica-Bold", 20)
    p.drawCentredString(300, 750, 'Invoice')

    # Reset font to regular
    p.setFont("Helvetica", 16)

    # Billing to information on the left
    p.drawString(50, 650, 'Bill To:')
    p.drawString(50, 630, order.user.name)
    p.drawString(50, 610, f'Address: {order.user.address}')
    p.drawString(50, 590, f'Email: {order.user.email}')

    # Date field on the right
    p.drawString(400, 650, f'Date: {order.date}')

    # Table with headings
    headings = ['Sr. No', 'Service Name', 'Rate', 'Sqft', 'Total (rs)']
    data = [
        [1, order.service.name, order.service.rate, order.area, order.service.rate * order.area],
        # [2, 'Service 2', 150, 30, 4500],
        # Add more rows as needed
    ]

    col_widths = [85, 200, 75, 75, 75]
    row_height = 20
    x = 50
    y = 490

    p.setFont("Helvetica-Bold", 16)
    for heading, width in zip(headings, col_widths):
        p.drawString(x, y, heading)
        x += width


    p.setFont("Helvetica", 16)
    y -= row_height  # Move to the next row
    for row in data:
        x = 50
        for value, width in zip(row, col_widths):
            p.drawString(x, y, str(value))
            x += width
        y -= row_height

    # Company details at the bottom left corner
    p.drawString(50, 200, 'Company Details:')
    p.drawString(50, 180, 'Kothrud, Pune')
    p.drawString(50, 160, 'Contact No: +91 7057270440')
    p.drawString(50, 140, 'Email Id: uniquefabrication@gmail.com')

    # Thank you at the bottom center
    p.drawCentredString(450, 50, 'Thank you!')

    # Save the PDF to the response
    p.showPage()
    p.save()

    return response



def orders(request):
    orders = Orders.objects.all()
    user_orders = Orders.objects.filter(user=request.user.id)
    services = Services.objects.all()
    users = CustomUser.objects.all()

    # print(services)

    if request.user.username == "admin":
        return render(request, 'adm/orders.html', {'orders': orders, 'services': services, 'users': users})
    else:
        return render(request, 'user/orders.html', {'orders': user_orders, 'services': services})

    return render(request, 'user/orders.html', {'orders': orders})

def edit_order(request,id):
    order = get_object_or_404(Orders,id=id)
    data = {
        'user': order.user.name,
        'service': order.service.name,
        'area': order.area,
        'total': order.total,
    }

    return JsonResponse(data)

def update_order(request):
    if request.method == "POST":
        order_id = request.POST.get('oid')
        order = get_object_or_404(Orders,id=order_id)
        service = get_object_or_404(Services,name=request.POST.get('service'))
        user = get_object_or_404(CustomUser,name=request.POST.get('user'))
        order.service = service
        order.user = user
        order.area = request.POST.get('area')
        order.total = request.POST.get('total')

        order.save()

    return redirect('orders')

def delete_order(request,id):
    order = get_object_or_404(Orders,id=id)
    order.delete()
    return redirect('/orders')

def payment(request,id):
    order = get_object_or_404(Orders,id=id)
    client = razorpay.Client(auth=("rzp_test_jVJhjYB6fVmmy7", "7xQlwvndREshe5dPNrOaKTNa"))
    client.set_app_details({"title" : "Unique Farbrications", "version" : "4.2.5"})
    amount = int(order.total) * 100
    order.payment_status = True
    
    data = { "amount": amount, "currency": "INR", "receipt": "order_rcptid_11" }
    payment = client.order.create(data=data)
    order.save()
    return JsonResponse(payment)

def feedback(request):
    if request.user.username == 'admin':
        feedback = Feedback.objects.all()
        return render(request, 'adm/feedback.html', {'feedback': feedback})
        
    return render(request,'user/feedback.html')

def insert_feedback(request):
    if request.method == "POST":
        name = request.POST.get('name')
        email=request.POST.get('email')
        feedback=request.POST.get('feedback')
        
        form = Feedback.objects.create(
            name=name,
            email=email,
            feedback=feedback
        )
    
    return redirect('feedback')
