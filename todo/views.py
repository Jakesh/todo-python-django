from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.contrib.auth import login, logout, authenticate
from  .forms import TodoForm
from .models import TODO
from django.utils import timezone
from django.contrib.auth.decorators import login_required

def signupUser(request):
    if request.method == 'GET':
        return render(request, 'todo/signupuser.html', {'form':UserCreationForm()})
    else:
        # CREATE NEW USER
        if request.POST['password1'] == request.POST['password2']:
            try:
                user = User.objects.create_user(request.POST['username'], password=request.POST['password1'])
                user.save()
                login(request, user)
                return redirect('currentTodos')
            except IntegrityError:
                return render(request, 'todo/signupuser.html', {'form':UserCreationForm(), 'error':'Username already exists'})
        else:
            return render(request, 'todo/signupuser.html', {'form':UserCreationForm(), 'error':'Passwords did not match'})

def loginUser(request):
    if request.method == 'GET':
        return render(request, 'todo/login.html', {'form':AuthenticationForm()})
    else:
        # LOGIN USER
        user = authenticate(request, username = request.POST['username'], password = request.POST['password'])
        if user is None:
            return render(request, 'todo/login.html', {'form':AuthenticationForm(), 'error':'Username or Password incorrect'})
        else:
            login(request, user)
            return redirect('currentTodos')

def home(request):
    return render(request, 'todo/home.html')

@login_required
def logoutUser(request):
    if request.method == 'POST':
        logout(request)
        return redirect('home')

@login_required
def currentTodos(request):
    todos = TODO.objects.filter(user=request.user, dateCompleted__isnull=True)
    return render(request, 'todo/current.html', {'todos': todos})

@login_required
def createTodos(request):
    if request.method == 'GET':
        return render(request, 'todo/createTodo.html', {'form':TodoForm()})
    else:
        try:
            form = TodoForm(request.POST)
            newtodo = form.save(commit=False)
            newtodo.user = request.user
            newtodo.save()
            return redirect('currentTodos')
        except ValueError:
            return render(request, 'todo/createTodo.html', {'form':TodoForm(), 'error':'Bad data passed in. Try Again'})

@login_required
def viewTodos(request, todo_pk):
    todo = get_object_or_404(TODO, pk=todo_pk, user=request.user)
    if request.method == 'GET':
        form = TodoForm(instance=todo)
        return render(request, 'todo/view.html', {'todo':todo, 'form':form})
    else:
        try: 
            form = TodoForm(request.POST, instance=todo)
            form.save()
            return redirect('currentTodos')
        except ValueError:
            return render(request, 'todo/view.html', {'todo':todo, 'form':form, 'error':'bad Data'})

@login_required
def completeTodos(request, todo_pk):
    todo = get_object_or_404(TODO, pk=todo_pk, user=request.user)
    if request.method == 'POST':
        todo.dateCompleted = timezone.now()
        todo.save()
        return redirect('currentTodos')
    
@login_required
def deleteTodos(request, todo_pk):
    todo = get_object_or_404(TODO, pk=todo_pk, user=request.user)
    if(request.method == 'POST'):
        todo.delete()
        return redirect('currentTodos')
        
@login_required
def completedTodos(request):
    todos = TODO.objects.filter(user=request.user, dateCompleted__isnull=False).order_by('-dateCompleted')
    return render(request, 'todo/viewCompleted.html', {'todos': todos})