from django.contrib.auth.decorators import login_required
from django.shortcuts import render,redirect
from .models import Admin,Product,Inquiry

def home(request):
    return render(request,'index.html')

def bharatnatyam(request):
    b_products=Product.objects.filter(category='bharatnatyam')
    return render(request,'bharatnatyam.html',{'products':b_products})    
def mohiniyattam(request):
    m_products=Product.objects.filter(category='mohiniyattam')   
    return render(request,'mohiniyattam.html',{'products':m_products})    
def kuchipudi(request):
    k_products=Product.objects.filter(category='kuchipudi')   
    return render(request,'kuchipudi.html',{'products':k_products})   

def admin_login(request):
    if request.method == "POST":
        try:
            username=request.POST.get('username')
            password=request.POST.get('password')
            n=Admin.objects.get(Username=username,Password=password)
            request.session['user_id']=n.id

            return redirect('a_home')
        except Admin.DoesNotExist:   
            messages.error(request,'Invalid credentials.Please try again.') 
            return render(request,'a_login.html')  
    return render(request,'a_login.html')          

def a_home(request):
    # Security Check
    if 'user_id' not in request.session:
        return redirect('admin_login')
    
    # FETCH LIVE DATA:
    total_products = Product.objects.count()
    active_orders = Inquiry.objects.filter(status='Pending').count()
    total_inquiries = Inquiry.objects.count()
    
    context = {
        'total_products': total_products,
        'active_orders': active_orders,
        'total_inquiries': total_inquiries
    }
    return render(request, 'a_home.html', context)

def manage_products(request):
    if 'user_id' not in request.session:
        return redirect('admin_login')
        
    if request.method == "POST":
        action = request.POST.get('action')
        
        if action == 'add':
            Product.objects.create(
                name=request.POST.get('name'),
                category=request.POST.get('category'),
                price=request.POST.get('price'),
                description=request.POST.get('description'),
                sizes=request.POST.get('sizes'),
                image=request.FILES.get('image')
            )
            
        elif action == 'delete':
            product_id = request.POST.get('product_id')
            Product.objects.filter(id=product_id).delete()
            
        return redirect('manage_products')
        
    all_products = Product.objects.all()
    return render(request, 'manage_products.html', {'products': all_products})    
def jewellery(request):
    products = Product.objects.filter(category='Jewellery')
    return render(request, 'jewellery.html', {'products': products})

def antique_jewellery(request):
    products = Product.objects.filter(category='Antique Jewellery')
    return render(request, 'antique_jewellery.html', {'products': products})

def hair_floral(request):
    products = Product.objects.filter(category='Hair & Floral')
    return render(request, 'hair_floral.html', {'products': products})

def orders(request):
    # Security Check
    if 'user_id' not in request.session:
        return redirect('admin_login')
        
    if request.method == "POST":
        action = request.POST.get('action')
        
        # Add a new manual order from WhatsApp
        if action == 'add':
            Inquiry.objects.create(
                customer_name=request.POST.get('customer_name'),
                phone_number=request.POST.get('phone_number'),
                product_interest=request.POST.get('product_interest'),
                notes=request.POST.get('notes')
            )
            
        # Mark an order as resolved/shipped
        elif action == 'resolve':
            inq_id = request.POST.get('inquiry_id')
            Inquiry.objects.filter(id=inq_id).update(status='Resolved')
            
        # Delete an order
        elif action == 'delete':
            inq_id = request.POST.get('inquiry_id')
            Inquiry.objects.filter(id=inq_id).delete()
            
        return redirect('orders')

    # Fetch all orders to display in the HTML, newest first
    all_inquiries = Inquiry.objects.all().order_by('-created_at')
    return render(request, 'orders.html', {'inquiries': all_inquiries})    


# Create your views here.
