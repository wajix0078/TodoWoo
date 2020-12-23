from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.contrib.auth import login, logout, authenticate
from .forms import TodoForm
from .models import Todo
from django.utils import timezone


# Create your views here.
def signupuser(request):
    if request.method == "GET":
        return render(request, 'todo/signupuser.html', {'form': UserCreationForm()})
    else:
        if request.POST['password1'] == request.POST['password2']:
            try:
                user = User.objects.create_user(request.POST['username'], password=request.POST['password1'])
                user.save()
                login(request, user)
                return redirect('currentTodos')

            except IntegrityError:
                return render(request, 'todo/signupuser.html',
                              {'form': UserCreationForm(),
                               'error': "Username is already taken, Please choose a different username"})

        else:
            return render(request, 'todo/signupuser.html',
                          {'form': UserCreationForm(), 'error': "Passwords did not match"})


def current_todos(request):
    todos = Todo.objects.filter(user=request.user, dateCompleted__isnull=True)
    return render(request, 'todo/currentTodos.html', {'todos': todos})


def logout_user(request):
    if request.method == "POST":
        logout(request)
        return redirect('home')


def login_user(request):
    if request.method == "GET":
        return render(request, 'todo/login.html', {'form': AuthenticationForm()})
    else:
        user = authenticate(request, username=request.POST["username"], password=request.POST["password"])
        if user is None:
            return render(request, 'todo/login.html',
                          {'form': AuthenticationForm(), 'error': 'Username and Password did not match'})
        else:
            login(request, user)
            return redirect('currentTodos')


def create_todos(request):
    if request.method == 'GET':
        return render(request, 'todo/createTodo.html', {'form': TodoForm()})
    else:
        try:
            form = TodoForm(request.POST)
            newtodo = form.save(commit=False)
            newtodo.user = request.user
            newtodo.save()
            return redirect('currentTodos')
        except ValueError:
            return render(request, 'todo/createTodo.html', {'form': TodoForm(), 'error': "Bad data passed.Try Again!"})


def home(request):
    return render(request, 'todo/home.html')


def view_todo(request, todo_pk):
    todo = get_object_or_404(Todo, pk=todo_pk, user=request.user)
    if request.method == "GET":
        form = TodoForm(instance=todo)
        return render(request, 'todo/viewTodo.html', {'todo': todo, 'form': form})
    else:
        try:
            form = TodoForm(request.POST, instance=todo)
            form.save()
            return redirect("currentTodos")
        except ValueError:
            return render(request, 'todo/viewTodo.html', {'todo': todo, 'form': form, 'error': 'Bad Info'})


def complete_todo(request, todo_pk):
    todo = get_object_or_404(Todo, pk=todo_pk, user=request.user)
    if request.method == "POST":
        todo.dateCompleted = timezone.now()
        todo.save()
        return redirect("currentTodos")
