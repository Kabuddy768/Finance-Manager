from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Profile
from .forms import ProfileForm
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login,logout
from .models import Transaction
from .forms import TransactionForm
from django.db.models import Q
import calendar
from django.db.models import Sum
from datetime import datetime
from .models import Category
from .models import SavingsGoal


# Create your views here.
@login_required
def profile_view(request, user_id):
    profile = Profile.objects.get(user__id=user_id)
    return render(request, 'profile/profile.html', {'profile': profile})

@login_required
def profile_edit(request, user_id):
    profile = Profile.objects.get(user__id=user_id)
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('profile', user_id=user_id)
    else:
        form = ProfileForm(instance=profile)
    return render(request, 'profile/profile_edit.html', {'form': form})

def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']

        # Check if passwords match
        if password1 != password2:
            messages.error(request, "Passwords do not match.")
            return redirect('register')

        # Check if username already exists
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect('register')

        # Check if email already exists
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists.")
            return redirect('register')

        # Create the user
        user = User.objects.create_user(username=username, email=email, password=password1)
        user.save()

 # Create associated Profile
        Profile.objects.create(user=user)

        messages.success(request, "Account created successfully. Please log in.")
        return redirect('login')
    
    return render(request, 'auth/register.html')  # Remove 'context' parameter

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('profile', user_id=user.id)  # Redirect to profile
        else:
            messages.error(request, "Invalid username or password.")
            return redirect('login')
    
    return render(request, 'auth/login.html')

def logout_view(request):
    logout(request)
    return redirect('login')

# Dashboard view
@login_required
def dashboard_view(request):
    transactions = Transaction.objects.filter(user=request.user).order_by('-date')

    # Filter by query parameters
    transaction_type = request.GET.get('transaction_type')
    category = request.GET.get('category')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    if transaction_type:
        transactions = transactions.filter(transaction_type=transaction_type)
    if category:
        transactions = transactions.filter(category=category)
    if start_date and end_date:
        transactions = transactions.filter(date__range=[start_date, end_date])

    # Calculate financial summary
    total_income = sum(t.amount for t in transactions if t.transaction_type == 'income')
    total_expenses = sum(t.amount for t in transactions if t.transaction_type == 'expense')
    savings = total_income - total_expenses

    form = TransactionForm()

    context = {
        'financial_data': {
            'total_income': total_income,
            'total_expenses': total_expenses,
            'savings': savings,
            'balance': savings,
        },
        'transactions': transactions,
        'form': form,
    }
    return render(request, 'dashboard/dashboard.html', context)


@login_required
def reports_view(request):
    # Group transactions by month and type
    current_year = datetime.now().year
    monthly_data = (
        Transaction.objects.filter(user=request.user, date__year=current_year)
        .values('date__month', 'transaction_type')
        .annotate(total=Sum('amount'))
        .order_by('date__month')
    )

    # Prepare data for income vs expenses chart
    income_expenses = {month: {'income': 0, 'expense': 0} for month in range(1, 13)}
    for data in monthly_data:
        month = data['date__month']
        transaction_type = data['transaction_type']
        income_expenses[month][transaction_type] = data['total']

    # Prepare data for category breakdown chart
    category_data = (
        Transaction.objects.filter(user=request.user, transaction_type='expense')
        .values('category')
        .annotate(total=Sum('amount'))
        .order_by('-total')
    )

    context = {
        'income_expenses': income_expenses,
        'category_data': category_data,
    }
    return render(request, 'dashboard/reports.html', context)


@login_required
def add_transaction(request):
    if request.method == 'POST':
        form = TransactionForm(request.POST)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.user = request.user  # Associate the transaction with the current user
            transaction.save()
            messages.success(request, 'Transaction added successfully')
            return redirect('dashboard')
        else:
            # If form is not valid, you might want to show errors
            messages.error(request, 'Please correct the errors below')
    else:
        form = TransactionForm()
    
    return render(request, 'dashboard/dashboard.html', {'form': form})


@login_required
def budget_view(request):
    categories = Category.objects.filter(user=request.user)

    # Check for overspending and calculate progress
    for category in categories:
        if category.budget > 0:
            category.progress = (float(category.spending) / float(category.budget)) * 100  # Calculate progress
        else:
            category.progress = 0  # Avoid division by zero

        if category.spending > category.budget:
            messages.warning(request, f"Warning: You have exceeded the budget for {category.name}!")

    if request.method == 'POST':
        success = True
        for category in categories:
            budget_field = f'budget_{category.id}'
            essential_field = f'essential_{category.id}'
            
            try:
                # Update budget
                if budget_field in request.POST:
                    new_budget = float(request.POST.get(budget_field, category.budget))
                    if new_budget < 0:
                        messages.error(request, f"Budget for {category.name} cannot be negative.")
                        success = False
                    else:
                        category.budget = new_budget

                # Update essential status
                category.is_essential = essential_field in request.POST
                category.save()

            except ValueError:
                messages.error(request, f"Invalid input for {category.name}. Please enter a valid number.")
                success = False

        if success:
            messages.success(request, "Budgets updated successfully!")
        return redirect('budget')

    # Pass categories with progress to the template
    return render(request, 'budget/budget.html', {'categories': categories})

@login_required
def add_budget(request):
    if request.method == 'POST':
        category_name = request.POST.get('category_name')
        category_budget = request.POST.get('category_budget')

        # Validation
        if not category_name or not category_budget:
            messages.error(request, "Both fields are required.")
            return redirect('budget')

        if Category.objects.filter(name=category_name, user=request.user).exists():
            messages.error(request, "This category already exists.")
            return redirect('budget')

        try:
            category_budget = float(category_budget)
            if category_budget < 0:
                messages.error(request, "Budget amount cannot be negative.")
                return redirect('budget')
        except ValueError:
            messages.error(request, "Please enter a valid number for the budget amount.")
            return redirect('budget')

        # Create the category
        Category.objects.create(
            user=request.user,
            name=category_name,
            budget=category_budget
        )

        messages.success(request, f"Budget category '{category_name}' created successfully!")
        return redirect('budget')


@login_required
def category_insights(request, category_id):
    category = Category.objects.get(id=category_id, user=request.user)
    transactions = Transaction.objects.filter(category=category)  # Assuming you have a `Transaction` model
    total_spent = sum(t.amount for t in transactions)

    return render(request, 'budget/category_insights.html', {
        'category': category,
        'transactions': transactions,
        'total_spent': total_spent,
        'remaining_budget': category.budget - total_spent,
    })

@login_required
def edit_budget(request, category_id):
    category = Category.objects.get(id=category_id, user=request.user)
    if request.method == 'POST':
        category.name = request.POST.get('name', category.name)
        category.budget = request.POST.get('budget', category.budget)
        category.save()
        messages.success(request, "Budget updated successfully!")
        return redirect('budget')
    return render(request, 'budget/edit_budget.html', {'category': category})

@login_required
def delete_budget(request, category_id):
    category = Category.objects.get(id=category_id, user=request.user)
    category.delete()
    messages.success(request, "Budget deleted successfully!")
    return redirect('budget')


@login_required
def add_savings_goal(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        target_amount = request.POST.get('target_amount')
        deadline = request.POST.get('deadline')

        # Validation
        if not name or not target_amount or not deadline:
            messages.error(request, "All fields are required.")
            return redirect('add_savings_goal')

        try:
            target_amount = float(target_amount)
            if target_amount <= 0:
                messages.error(request, "Target amount must be greater than zero.")
                return redirect('add_savings_goal')
        except ValueError:
            messages.error(request, "Please enter a valid number for the target amount.")
            return redirect('add_savings_goal')

        # Save the goal
        SavingsGoal.objects.create(
            user=request.user,
            name=name,
            target_amount=target_amount,
            deadline=deadline
        )
        messages.success(request, f"Savings goal '{name}' created successfully!")
        return redirect('view_savings_goals')

    return render(request, 'savings/add_savings_goal.html')

@login_required
def view_savings_goals(request):
    goals = SavingsGoal.objects.filter(user=request.user)
    return render(request, 'savings/view_savings_goals.html', {'goals': goals})